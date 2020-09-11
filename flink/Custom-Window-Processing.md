# 高级Flink应用程序模式：自定义窗口处理

**本文翻译自：<https://flink.apache.org/news/2020/07/30/demo-fraud-detection-3.html>**

## 引言

在本系列的前几篇文章中，我介绍了如何基于动态更新的配置（一组欺诈检测规则）实现灵活的流分区，以及如何利用Flink的广播（Broadcast）机制在运行时在相关的算子（operators）之间分发处理配置。

接着我们上次对端到端解决方案的讨论，这篇文章中我们将描述如何使用Flink的“瑞士军刀”-[Process Function](https://ci.apache.org/projects/flink/flink-docs-release-1.11/dev/stream/operators/process_function.html)来创建针对我们业务逻辑需求量身定制的实现。我们的讨论将在[欺诈检测引擎](https://flink.apache.org/news/2020/01/15/demo-fraud-detection.html#fraud-detection-demo)的背景下继续进行。我们还将演示如何在DataStream API可用的开箱即用的窗口无法满足您的要求的情况下，实现对时间窗口的自定义替换。特别的，我们将研究在设计需要针对单个事件进行低延迟响应的解决方案时可以做出的取舍。

本文将介绍一些可以独立应用的高级概念，但是建议您回顾本系列的第一部分和第二部分中的内容，并检查代码库，以使其更容易理解。

## ProcessFunction as a "Window"

### 低延迟

让我们先提醒一下我们希望支持的欺诈检测规则类型：

*只要在24小时内从同一付款人向同一受益人的付款总和大于20万美元，就会触发报警。*

换句话说，由给定联合了付款人和受益人字段的键划分的交易流，我们想及时回顾一下，并未每笔传入交易确定两个特定参与者之间所有先前付款的总和是否超过定义的阈值。事实上，对于特定的数据分区键，计算窗口始终沿最后观察到的事件的位置移动。

![](https://flink.apache.org/img/blog/patterns-blog-3/time-windows.png)
<center>图一：时间窗口</center>

欺诈检测系统的常见关键要求之一是响应时间短。越早发现欺诈行为，阻止该欺诈行为并减轻其负面后果的机会就越大。该要求在金融领域尤为突出，在该领域中，您有一个重要的约束条件--花费在评估欺诈检测模型上的任何时间就是系统中守法用户在等待响应上所花费的时间。处理的迅速性通常成为各种支付系统之间的竞争性优势并且产生报警的时间限制可以低至300-500毫秒。从将事务事件吸收到欺诈检测系统的那一刻起，直到报警对下游系统可用为止，这就是您能用的所有时间。

如您所知，Flink提供了强大的Window API，适用于各种用例。但是，如果你遍历所有可用类型的受支持窗口，你将意识到他们都不完全符合我们对此用例的主要要求-每个传入事务的低延迟评估。Flink中没有一种类型的窗口可以表达“从当前事件回溯x分钟/小时/天”的语义。在Window API中，事件属于窗口（由窗口[分配器](https://ci.apache.org/projects/flink/flink-docs-release-1.11/dev/stream/operators/windows.html#window-assigners)定义），但是事件本身不能单独控制窗口的创建和评估。这就提出了在这种情况下应用Window API的可行性问题。Window API提供了一些用于自定义触发器（triggers），evictors和窗口分配器（window assigners）的选项，这些选项可能会达到所需的结果。但是，通常很难做到这一点（而且容易破解）。而且，此方法不提供对广播状态的访问，这是实现业务规则的动态配置所必须的。

*）除了会话窗口外，然而仅限于基于会话[间隔（gaps）](https://ci.apache.org/projects/flink/flink-docs-release-1.11/dev/stream/operators/windows.html#session-windows)的分配

![](https://flink.apache.org/img/blog/patterns-blog-3/evaluation-delays.png)
<center>图二：评估延迟</center>

让我们以使用Flink的Window API中的[滑动窗口（sliding window）](https://ci.apache.org/projects/flink/flink-docs-release-1.11/dev/stream/operators/windows.html#sliding-windows)为例。使用以S为步长的滑动窗口可转换为等于S/2的评估延迟期望值。这意味着，及时不考虑任何实际计算时间，也需要定义600-1000ms的窗口滑动时间来满足300-500ms延迟的低延迟要求。Flink为每个窗口存储单独的窗口状态的事实使这种方法在任何中高负载的条件下都不可行。

为了满足要求，我们需要创建自己的低延迟窗口实现。幸运的是，Flink为我们提供了所需的所有工具。ProcessFunction是Flink API中低级但功能强大的构建块。它有一个简单的定义：
```java
public class SomeProcessFunction extends KeyedProcessFunction<KeyType, InputType, OutputType> {

	public void processElement(InputType event, Context ctx, Collector<OutputType> out){}

	public void onTimer(long timestamp, OnTimerContext ctx, Collector<OutputType> out) {}

	public void open(Configuration parameters){}
}
```

* processElement() 依次接收输入事件。您可以通过调用`out.collect(someOutput)`对下一个运算符产生一个或多个输出事件来对每个输入做出响应。您还可以将数据传递到[side output](https://ci.apache.org/projects/flink/flink-docs-release-1.11/dev/stream/side_output.html)或者忽略特定的输入集合。

* onTimer() 当先前注册的计时器触发时，被Flink会调用。时间时间和处理时间都支持。

* open() 等效于构造函数。它在TaskManager的JVM内部调用，用于初始化，例如注册Flink管理的状态。这也是初始化不可序列化且无法从JobManager的JVM传输的字段的合适位置。

最重要的事，ProcessFunction还可以访问由Flink处理的容错状态。这种结合以及Flink的消息处理和传递保证，使得可以使用几乎任意复杂的业务逻辑来构建具有弹性的事件驱动的应用程序。这包括创建和处理带有状态的自定义窗口。

## 实现

### 状态与清理

为了能够处理事件窗口，使我们需要跟踪属于程序内部船舶港口的数据。为了确保改数据是容错的并且在分布式系统中幸免于难（survive failures），我们应该将其存储在Flink管理状态下。随着时间的推移，使我们不需要保存所有以前的交易。根据是样本规则，所有早于24小时的事件都将变得无关紧要。我们正在查看一个不断移动的数据窗口，以及需要将过时的事务不断溢出范围（换句话说，从状态中清除）的窗口。

![](https://flink.apache.org/img/blog/patterns-blog-3/window-clean-up.png)
<center>图3：窗口清理</center>

我们将使用MapState来存储窗口的各个事件。为了有效的清理范围外的事件，我们将事件时间戳用作MapState键。

在一般情况下，我们必须考虑到可能存在完全相同的时间戳的不同事件，因此，我们每个键（时间戳）将存储集合而不是单独的事务。

`MapState<Long, Set<Transaction>> windowState;`

 如本系列的第一篇博客中所述，我们根据活动欺诈检测规则中指定的key分派事件。多个不同规则可以基于同一分组键。这意味着我们的报警功能可以潜在地接收以相同key（例如{payerId=25;beneficiaryId=12}）为范围的交易，DNA注定要根据不同的规则进行评估，这意味着时间窗口的长度可能不同。这就提出了一个问题，即如何在KeyedProcessFunction中以最好的方式存储容错窗口状态。一种方法是为是每个规则创建和管理单独的MapState。但是，这种方法将很浪费 -- 我们将为重叠的时间窗口分别保持状态，因此不必要地存储重复事件。更好的方法是始终存储足够的数据，以便能够估计所有当前活动的规则，这些规则受同一key限制。为了实现这一点，无论何时添加新规则，我们都将确定其时间窗口是否具有最大跨度，并将其存储在广播状态下的特殊保留WIDEST_RULE_KEY下。稍后将在状态清除过程中使用此信息，如本节后面所述。

 ```java
 @Override
public void processBroadcastElement(Rule rule, Context ctx, Collector<Alert> out){
  ...
  updateWidestWindowRule(rule, broadcastState);
}

private void updateWidestWindowRule(Rule rule, BroadcastState<Integer, Rule> broadcastState){
  Rule widestWindowRule = broadcastState.get(WIDEST_RULE_KEY);

  if (widestWindowRule == null) {
    broadcastState.put(WIDEST_RULE_KEY, rule);
    return;
  }

  if (widestWindowRule.getWindowMillis() < rule.getWindowMillis()) {
    broadcastState.put(WIDEST_RULE_KEY, rule);
  }
}
 ```

现在，让我们详细了解一下主要的方法processElement()的实现。

在之前的[博客文章](https://flink.apache.org/news/2020/01/15/demo-fraud-detection.html#dynamic-data-partitioning)中，我们描述了DynamicKeyFunction如何允许我们基于规则定义中的groupingKeyNames参数执行动态数据分区。随后的描述集中在DynamicAlertFunction上，该函数利用其余的规则设置。

![](https://flink.apache.org/img/blog/patterns-blog-3/sample-rule-definition.png)

如博客系列文章前面部分所述，我们的alerting procss fcuntion接收类型为`Keyed<Transaction, String,  Integer>`的事件，其中Transaction是主要的事件“包装”，String是key（图一中的payer#x - beneficiary#y），Integer是导致分发该事件的规则的ID。该规则已经[存储在了广播状态](https://flink.apache.org/news/2020/03/24/demo-fraud-detection-2.html#broadcast-state-pattern)中，必须通过ID从该状态中检索。这是大概的实现：

```java
public class DynamicAlertFunction
    extends KeyedBroadcastProcessFunction<
        String, Keyed<Transaction, String, Integer>, Rule, Alert> {

  private transient MapState<Long, Set<Transaction>> windowState;

  @Override
  public void processElement(
      Keyed<Transaction, String, Integer> value, ReadOnlyContext ctx, Collector<Alert> out){

    // Add Transaction to state
    // 添加该笔交易到状态中
    long currentEventTime = value.getWrapped().getEventTime();                            // <--- (1)
    addToStateValuesSet(windowState, currentEventTime, value.getWrapped());

    // Calculate the aggregate value
    // 计算合计值
    Rule rule = ctx.getBroadcastState(Descriptors.rulesDescriptor).get(value.getId());    // <--- (2)
    Long windowStartTimestampForEvent = rule.getWindowStartTimestampFor(currentEventTime);// <--- (3)

    SimpleAccumulator<BigDecimal> aggregator = RuleHelper.getAggregator(rule);            // <--- (4)
    for (Long stateEventTime : windowState.keys()) {
      if (isStateValueInWindow(stateEventTime, windowStartForEvent, currentEventTime)) {
        aggregateValuesInState(stateEventTime, aggregator, rule);
      }
    }

    // Evaluate the rule and trigger an alert if violated
    // 评估规则，如果违反则触发报警
    BigDecimal aggregateResult = aggregator.getLocalValue();                              // <--- (5)
    boolean isRuleViolated = rule.apply(aggregateResult);
    if (isRuleViolated) {
      long decisionTime = System.currentTimeMillis();
      out.collect(new Alert<>(rule.getRuleId(),
                              rule,
                              value.getKey(),
                              decisionTime,
                              value.getWrapped(),
                              aggregateResult));
    }

    // Register timers to ensure state cleanup
    // 注册计时器以确保状态清除
    long cleanupTime = (currentEventTime / 1000) * 1000;                                  // <--- (6)
    ctx.timerService().registerEventTimeTimer(cleanupTime);
  }
```

以下是每一步的详细信息：

1）我们首先将每个新事件添加到窗口状态：

```java
static <K, V> Set<V> addToStateValuesSet(MapState<K, Set<V>> mapState, K key, V value)
      throws Exception {
    Set<V> valuesSet = mapState.get(key);
    if (valuesSet != null) {
      valuesSet.add(value);
    } else {
      valuesSet = new HashSet<>();
      valuesSet.add(value);
    }
    mapState.put(key, valuesSet);
    return valuesSet;
}
```

2）接下来，我们检索之前广播的规则，根据该规则需要评估传入的交易。

3）getWindowStartTimestampFor 确定了我们的评估应该跨多远的时间，在给定规则中定义的时间窗口跨度和当前事务时间戳的情况下。

4）通过迭代所有窗口状态条目并应用聚合函数来计算聚合值。它可以是平均值，最大值，最小值，也可以是总和，如本节开头的示例规则中所示。

```java
private boolean isStateValueInWindow(
    Long stateEventTime, Long windowStartForEvent, long currentEventTime) {
  return stateEventTime >= windowStartForEvent && stateEventTime <= currentEventTime;
}

private void aggregateValuesInState(
    Long stateEventTime, SimpleAccumulator<BigDecimal> aggregator, Rule rule) throws Exception {
  Set<Transaction> inWindow = windowState.get(stateEventTime);
  for (Transaction event : inWindow) {
    BigDecimal aggregatedValue =
        FieldsExtractor.getBigDecimalByName(rule.getAggregateFieldName(), event);
    aggregator.add(aggregatedValue);
  }
}
```

5）有了合计值，我们可以将其与规则定义中定义的阈值进行比较，并在必要时发出报警。

6）最后，我们使用ctx.timeService().registerEventTimeTimer()注册清除定时器。这个定时器将清除超出时间范围的交易。

> **Notice:** the rounding during timer creation. It is an important technique which enables a reasonable trade-off between the precision with which the timers will be triggered, and the number of timers being used. Timers are stored in Flink’s fault-tolerant state, and managing them with millisecond-level precision can be wasteful. In our case, with this rounding, we will create at most one timer per key in any given second. Flink documentation provides some additional [details](https://ci.apache.org/projects/flink/flink-docs-release-1.11/dev/stream/operators/process_function.html#timer-coalescing).

7）onTime方法将触发窗口状态的清除。

如之前所述，我们始终在状态中保持许多事件，以评估具有最大窗口跨度的活动的规则。这意味着在清理过程中，我们只需要删除超出此最大窗口范围的状态。

![](https://flink.apache.org/img/blog/patterns-blog-3/widest-window.png)

这是清理过程的一种实现：

```java
@Override
public void onTimer(final long timestamp, final OnTimerContext ctx, final Collector<Alert> out)
    throws Exception {

  Rule widestWindowRule = ctx.getBroadcastState(Descriptors.rulesDescriptor).get(WIDEST_RULE_KEY);

  Optional<Long> cleanupEventTimeWindow =
      Optional.ofNullable(widestWindowRule).map(Rule::getWindowMillis);
  Optional<Long> cleanupEventTimeThreshold =
      cleanupEventTimeWindow.map(window -> timestamp - window);
  // Remove events that are older than (timestamp - widestWindowSpan)ms
  cleanupEventTimeThreshold.ifPresent(this::evictOutOfScopeElementsFromWindow);
}

private void evictOutOfScopeElementsFromWindow(Long threshold) {
  try {
    Iterator<Long> keys = windowState.keys().iterator();
    while (keys.hasNext()) {
      Long stateEventTime = keys.next();
      if (stateEventTime < threshold) {
        keys.remove();
      }
    }
  } catch (Exception ex) {
    throw new RuntimeException(ex);
  }
}
```

>**提示** 你可能会有疑问既然要经常迭代窗口中的所有值，为什么我们不用`ListState`？这其实是针对`RocksDBStateBackend`的一种优化。遍历`ListState`会导致所有`Transaction`对象反序列化。使用`MapState`的key迭代，只会反序列化key（long类型），因此减少了计算开销。

到此结束了对实现细节的描述。一旦有新的交易到达，我们的方法就会触发对时间窗口的评估。因此，它满足了我们的主要需求--尽可能的低延迟以触发报警。对于完整的实现，请查看[github上的项目](https://github.com/afedulov/fraud-detection-demo)。

## 改进和优化

这种方式的优缺点？

### 优点
  * 低延迟
  * 定制的解决方案，有优化的潜力
  * 有效的状态重用（具有相同键的规则的共享状态）

### 缺点
  * Cannot make use of potential future optimizations in the existig Window API
  * No late event handling, which is available out of the box in the Window API 
  * 平方计算复杂度和潜在的大状态

让我们看看后面两个缺点，看看是否可以解决它们。

### Late events

处理迟到的事件提出了一个问题 - 在事件迟到的情况下重新评估窗口是否仍然有意义？ In case this is required, you would need to extend the widest window used for the clean-up by your maximum expected out-of-orderness. This would avoid having potentially incomplete time window data for such late firings (see Figure 7).（如果需要这样做，则需要根据最大的预期乱序，扩展用于清理的最宽窗口）。

