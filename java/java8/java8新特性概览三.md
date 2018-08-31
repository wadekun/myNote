### 题外话
最近在知乎上看到个话题，觉得挺有意思。[不浮躁的社会是什么样的？](https://www.zhihu.com/question/22633562)(看完了，反省下自己，别浮躁)。尤其看到[这个答案](https://www.zhihu.com/question/22633562/answer/90351145)的时候，真是被触动到了，由衷的对这个老师感到敬佩。其实，我的梦想之一就是有了足够的钱去建所学校(认真脸)…

### 使用lambda编程
 * 使用lambda表达式的主要原因是，将代码的执行延迟到一个合适的时间点。
 * 当执行一个lambda表达式时，请确认提供了所有必须的参数作为输入。
 * 如果可以，请选择一个已有的函数式接口。
 * 编写一个返回函数式接口实例的方法通常很有用。
 * 当你使用转换时，请考虑如何能组合它们。
 * 要延迟组合转换，你需要保留一个所有未执行的转换列表，并在最后应用它们。
 * 如果你需要多次应用一个lambda表达式，最好将工作分成多个子任务，以便可以并发执行。
 * 考虑如何处理lambda表达式中抛出异常的情况。
 * 当使用泛型函数式接口时，请使用`? Super`通配符作为参数类型，使用`? Extend`通配符作为返回类型。
 * 当使用可以被函数转换的泛型类型时，请考虑使用map和flatMap。

#### 延迟执行
lambda表达式都是 **延迟执行** 的。

延迟执行的原因有很多，例如：  
1. 在另一个线程中运行代码。
2. 多次运行代码。
3. 在某个算法的正确时间上运行代码(例如排序中的比较操作)
4. 当某些情况发生时运行代码(按钮被点击，数据到达等)
5. 只有在需要的时候才运行的代码

例如，在记录INFO级别的日志时

    public static void info(Logger logger, Supplier<String> message){
        if(logger.isLoggable(Level.INFO)){//当日志级别INFO开启时
          logger.info(message.get());
        }
    }

#### 选择一个函数式接口

* 常用函数式接口

| 函数式接口 | 参数类型  | 返回类型    | 抽象方法名  | 描述  | 其他方法
| :------------- | :------------- |
| Runnable       | 无      | void   | run |  执行一个没有参数和返回值的操作|  -  |
| `Supplier<T>`    | 无      |  T   | get  | 提供一个T类型的值|  - |
| `Consumer<T>`    | T       |  void   | accept  |  处理一个T类型的值 |  chain |
| `BiConsumer<T, U>`| T, U  | void     | accept  | 处理一个T类型和U类型的值 | chain |
| `Function<T, R>`  | T     |  R       | apply   | 一个参数类型为T返回值类型为R的函数| compose,andThen,identity|
| `BiFunction<T, U, R>`| T, U | R  |  apply  | 一个参数类型为T和U返回值类型为R的函数  |  andThen|
| `UnaryOperator<T>` | T  |   T  |  apply  |  对类型T进行一元操作 |  compose, andThen, identity|
| `BinaryOperator<T>`| T, T | T  | apply |  对类型T进行的二元操作 | andThen|
| `Predicate<T>`    | T  | boolean | test | 一个计算Boolean值的函数| And, or, negate, isEqual|
| `BiPredicate<T, U>`| T, U| boolean | test| 一个根据T、U类型参数计算boolean值得函数| And, or, negate|

* 为原始类型提供的函数式接口

  当然，API还提供了为原始类型提供的函数式接口。  
  例如返回 boolean的 BooleanSupplier接口。提供Int值的IntSupplier，消费Int值的IntConsumer。Int转double的IntToDoubleFunction。

* 自己动手写一个函数式接口
自己动手写一个函数式接口：  
允许用户指定的一个函数 (int, int, Color) -> Color，根据图片中(x, y)位置上的像素来计算新的颜色   

    @FunctionalInterface
    public interface ColorTransformer {
        Color apply(int x, int y, Color colorAtXY);
    }

#### 返回函数与组合

    public static <T> UnaryOperator<T> compose(UnaryOperator<T> op1, UnaryOperator<T> op2){
      return t -> op2.apply(op1.apply(t));
    }

#### 延迟与并行操作
`todo...`

#### 处理异常
* 提供一个异常处理的handler

      <T> void doInOrderAsync(Supplier<T> first, Consumer<T> second, Consumer<Throwable> handler){
        Thread t = new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    T t = first.get();
                    second.accept(t);
                } catch (Exception e) {
                    handler.accept(e);
                }
            }
        });
        t.start();
      }

#### lambda表达式和泛型
**一般准则是父类作为参数类型，子类作为返回类型** ，这样，可以将一个`Consumer<Object>` 传递给一个 `Stream<String>`的forEach方法。可以处理Object，也就是任何对象，当然也包括String咯。
这样刚才的doInOrderAsync方法的入参应如下：     
`void doInOrderAsync(Supplier<? extends T> first, Consumer<? super T> second, Consumer<? super T> handler)`

### 新的日期和时间API
  * 所有java.time对象都是不可变的
  * 一个瞬间(Instant)是时间线上的一个点(与Date类似)
  * 在Java事件中，每天都是86400秒(即没有闰秒)
  * 持续时间(Duration)是两个瞬间之间的时间
  * LocalDateTime没有时区信息
  * TemporalAdjuster 的方法可以处理常用的日历计算，例如找到某个月的第一个星期二
  * ZonedDateTime 是指定时区中的某一个时间点(类似于Gregorian Calendar)
  * 单处理带时区的时间时，请使用时段(Period)，而非 Duration，以便将夏令时的变化考虑在内
  * 使用DateTimeFormatter 来格式化日期和时间

#### 时间点与时间段
  在java中有如下时标：
  1. 每天都有86400秒
  2. 每天正午与官方时间准确匹配
  3. 其他时间也要以一种精确定义的方式与其紧密匹配

Java8中引入的时间点与持续时间
  * `Instant`：一个instant对象表示时间轴上的一个点。  
    时间原点被规定为1970年1月1日的午夜，此时本初子午线正在穿过伦敦格林尼治皇家天文台。
      * `Instant.MIN` 表示10亿年前。
      * `Instant.MAX` 表示10 0000 0000 年的12月31日。
      * `Instant.now()`会返回当前的瞬间点。
  * `Duration` : 两个时间点之前的时间量   

        Instant start = Instant.now();
        runAlgorithm();
        Instant end = Instant.now();
        Duration timeElapsed = Duration.between(start, end);
        long millis = timeElapsed.toMillis();
  * `Period` 时段：表示一段逝去的年、月 或 日


  * Instant与Duration的其他操作见API
#### 本地日期(LocalDate)
  `LocalDate` 是一个带有年份，月份，当月天数的日期。
  * 创建LocalDate
     * `LocalDate today = LocalDate.now(); //今天的日期`
     * `LocalDate alonzosBirthday = LocalDate.of(1903, 6, 14);`
       `alonzosBirthday = LocalDate.of(1903, Month.JUNE, 14); //使用Month枚举`

#### 日期矫正器
  对于一些需要安排调度的应用程序，通常需要计算例如“每月的第一个周二”这样的日期。`TemporalAdjusters`类提供了许多静态方法来进行常用的矫正。你可以将一个矫正方法的结果传递给with方法。例如，你可以通过如下代码来计算某个月第一个周二：    

        LocalDate firstTuseDay = LocalDate.of(year, month, 1).with(TemporalAdjusters.nextOrSame(DayOfWeek.TUESDAY));
#### 本地时间
  LocalTime 表示一天中的某个时间，例如 15:30:00。你可以使用now或者of方法来创建一个LocalTime实例。

        LocalTime rightNow = LocalTime.now();
        LocalTime bedtime = LocalTime.of(22, 30);// 或者LocalTime.of(22, 30, 00);

#### 带时区的时间
  `ZonedDateTime`
  * localDateTime.atZone(zoneId)
  * ZonedDateTime.of(1969, 7, 16, 9, 32, 0, 0, ZoneId.of("America/New_York"));

#### 格式化和解析 `DateTimeFormatter`
  提供了三种方法来格式化打印日期/时间：
  * 预定义的标准格式
  * 语言环境相关的格式
  * 自定义的格式   
    `DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");`

### 并发增强
  * 使用`updateAndGet/accumulateAndGet`方法可以更容易的更新原子变量
  * 在激烈的竞争环境下，`LongAccumulator/DoubleAccumulator`比`AtomicLong/AtomicDouble`效率更高
  * 使用`compute/merge`方法可以更容易的更新`ConcurrentHashMap`中的元素项
  * ConcurrentHashMap提供了对键、值、键值对 及各元素项的各类操作，例如：search、reduce、forEach
  * 集合视图允许将ConcurrentHashMap作为一个Set来使用
  * Arrays 类提供了排序、填充 及前缀操作的并行方法
  * 完善的Future 类允许你创建异步的操作

#### 原子值
在Java5中提供了 java.util.concurrent包，为我们提供了线程安全的集合和线程池，以及很多其他的并发工具。  
在Java8之前常见的 CAS(compare and swap)加自旋来更新一个原子量：

      public static AtomicLong largest = new AtomicLong();
      do {
        oldValue = largest.get(); //获得当前值
        newValue = Math.max(oldValue, observed); // observed 观测值
      } while (!largest.compareAndSet(oldValue, newValue));

在Java8中，可以通过 `updateAndGet(LongUnaryOperator updateFunction)/getAndAccumulate(long x, LongBinaryOperator accumulatorFunction)`，来更方便的实现这个操作：

      largest.updateAndGet(x -> Math.max(x, observed));
      //或
      largest.getAndAccumulate(observed, Math::max);

当有大量线程访问同一个原子值时，偶遇乐观锁更新需要太多次重试，因此会导致性能严重下降。为此Java8提供了`LongAdder`和`LongAccumulator`来解决该问题。LongAdder由多个变量组成，这些变量会自动增加新的被加数。由于通常情况下都是知道所有工作完成后才需要总和值，所以这种方法效率很高。

如果你的环境中存在高度竞争，那么就应该用LongAdder 来替代 AtomicLong。 在LongAdder中，`increment()`方法用来将计数器自增1，`add`方法用来加上某个数值，`sum`方法用来获取总和值。

      final LongAdder adder = new LongAdder();
      for(...){
        pool.submit(() -> {
          while(...){
            ...
            if (...) adder.increment(); //自增1
          }
        });
      }
      ...
      long total = adder.sum();
关于LongAdder的实现，可以参看[从LongAdder看更高效的无锁实现](http://coolshell.cn/articles/11454.html)。

LongAccumulator 将这个思想带到了任意的累加操作中。在构造函数中，你需要提供操作类型及其中的中立元素。要与新值相加，需要调用accumulate方法。然后调用 get 方法获取当前值。以下代码与 LongAdder 的效果是一样的：

      LongAccumulator adder = new LongAccumulator(Long::sum, 0);
      //在某些线程中
      adder.accumulate(value);

在 LongAccumulator 的内部，包含 a1,a2,a3,...an等多个变量。每个变量都被初始化为中立元素(在上面的例子中即为0)。   
当调用 accum 方法累加值V时，这些变量其中之一会自动被更新为 `ai = ai op v`，其中op是以中缀形式表示的累加操作。在上面的实例中，调用accumulate会对变量i计算 ai = ai+v。 get 方法的结果为 a1`op`a2`op`a3`op`...`op`an。在上面的例子中，它会计算所有变量的总和，即 a1+a2+...+an。

Java8中新增了一个`StampedLock`类，用来实现乐观读。

        public class Vector{
          private int size;
          private Object[] elements;
          // 实现乐观读
          private StampedLock lock = new StampedLock();

          public Object get(int n){
            //1.获得一个 印戳
            long stamp = lock.tryOptimisticRead();
            //2.读取值
            Object[] currentElements = elements;
            int currentSize = size;
            //3.检查印戳 是否仍然有效
            if (!lock.validate(stamp)){
              //4. 印戳无效，获得一个读锁(将会阻塞所有的写锁)
              stamp = lock.readLock();
              //5. 在此读取值
              currentElements = elements;
              currentSize = size;
              //6. 释放读锁
              lock.unlockRead(stamp);
            }
            return n < currentSize ? currentElements[n] : null;
          }
          ...
        }

#### ConcurrentHashMap 改进
compute方法与merge方法
##### 更新值
先看一个非线程安全的更新值的例子A：

      Long oldValue = map.get(word);
      Long newValue = oldValue == null ? 1 : oldValue + 1;
      map.put(word, newValue); //错误

为什么非线程安全？因为这个`取值，加值，更新值`并不是一个原子操作。可以通过使用 `replace`加自旋来进行这个操作：

      do {
        oldValue = map.get(word);
        newValue = oldValue == null ? 1 : oldValue + 1;
      } while (!map.replace(word, oldValue, newValue));

另外，可以使用AtomicLong或者LongAdder 实现上述功能。

      map.putIfAbsent(word, new LongAdder()); // 确保 word键值对存在
      map.get(word).increment();

      //由于putIfAbsent方法会返回映射值，可以将这两条语句合并为一条：
      map.putIfAbsent(word, new LongAdder()).increment();

Java8 中 `compute` 方法可以通过一个键和一个函数来计算出新的值。该函数会获取键及其相关的值(如果没有值则为null)，然后计算出新的值。

      map.compute(word, (k, v) -> v == null ? 1 : v + 1);

Java8中还提供了`computeIfPresent`和`computeIfAbsent`方法，分别在值存在 和 值尚未村阿紫的情况下，才计算新值。因此，还可以这样写

      map.computeIfAbsent(word, k - > new LongAdder()).increment(); // 值尚未存在的时候，设置一个 新的 LongAdder

`merge`方法更新值

      map.merge(word, 1L, (existingValue, newValue) -> existingValue + newValue); // 参数 1L 表示，键尚未存在时的值。
      // 或
      map.merge(word, 1L, Long::sum); // 还记得lambda中的构造器引用吗。

注意：
    1. 如果传递给`compute`或`merge`方法的函数返回null，那么有的数据项会从映射中删除掉。
    2. `compute`和`merge`方法运行时，其他一些更新映射的操作可能会被阻塞。所以，最好不要在 提供给这两个方法的函数中进行大量的工作。

##### 批量数据操作
Java 8 为ConcurrentHashMap提供了批量数据操作，即使是在其他线程同时操作映射时也可以安全的执行。批量数据操作会遍历映射并对匹配的元素进行操作。

批量数据操作有三类：

  * search 会对每个键和(或)值应用一个函数，直到该函数返回一个null的结果。然后search会终止并返回该函数的结果。
  * reduce 会通过提供的累积函数，将所有的键和(或)值组合起来。
  * forEach 会对所有键和(或)值应用一个函数。

每个操作都有下面4个版本：

  * searchKeys/reduceKeys/forEachKeys：对键操作
  * searchValues/reduceValues/forEachValues：对值操作
  * search/reduce/forEach：对键和值操作
  * searchEntries/reduceEntries/forEachEntries：对Map.Entry对象操作

在使用这四个操作时，需要指定一个并行阀值。如果映射包含的元素数量超过了这个阀值，批量操作就以并行方式执行。

以search方法为例，来看上面的四个版本：

  * U searchKeys(long threshold, Function<? super K, ? extends U> f)
  * U searchValues(long threshold, Function<? super K, ? extends U> f)
  * U search(long threshold, BiFunction<? super K, ? super V, ? extends U> f)
  * U searchEntries(long threshold, Function<Map.Entry<K, V>, ? extends U> f)

注：书上的searchKeys,searchValues,searchEntries三处的函数接口写成了BiFunction，在这里显然是不对的，因为只有一个入参，应该是Function接口，查阅Oracle API文档确实如此，在这里要纠正下。不知道是原作者写错了，还是翻译成中文的时候写错了，还是印刷错误。。想给原作者的站点去反馈的，可是感觉英文表达好费劲。。。不管怎样还是被自己的机智所感动啊。恩，看书，要有自己的想法，有所思。

例如，假设我们希望找到第一个出现超过1000次的单词，我们需要搜索键和值：

      String result = map.search(threshold, (k, v) -> v > 1000 ? k : null);

forEach 方法有两种形式，第一种只是对每个映射数据项简单的应用一个消费者函数：

      map.forEach(threshold, (k, v) -> System.out.println(k + " -> " + v));

第二种形式会额外的接受一个转换器函数，首先会应用该转换器函数，然后再将其结果传递给消费者函数：

      map.forEach(threshold,  //并行阀值
                    (k, v) -> k + " -> " + v, // 转换器函数
                    System.out::println); // 消费者函数

转换器函数可以被用作一个过滤器。当转换器函数返回null时，值会被直接跳过。

例如，我们可以使用如下代码打印值较大的数据项：

      map.forEach(threshold,
                    (k, v) -> v > 1000 ? k + " -> " + v : null,  // 转换器同时具有过滤器的功能
                      System.out::println); // 消费者函数

reduce 操作将其输入与一个累加函数结合起来。例如，下面的代码展示了如何计算所有值的总和：

      Long sum = map.reduceValues(threshold, Long::sum);

同forEach一样，你也可以提供一个转换器函数。我们这里计算最长键的长度：

      Integer maxLength = map.reduceKeys(threshold,
                                          String::length,   // 转换器，将String转换为Integer，作为消费者函数的输入
                                          Integer::max);    // 消费者，消费转换器的结果

转换器可以作为一个过滤器，通过返回null，来排除不想要的输入。这里，我们计算大于1000的数据项的个数：

      Long count = map.reduceValues(threshold,
                                        v -> v > 1000 ? 1L : null,  // 带有过滤功能的转换器，过滤掉小于1000的数据项
                                        Long::sum);  // 消费者函数
##### Set视图
* newKeySet    
    静态方法newKeySet 会返回一个 Set<K>对象，它实际上就是对 ConcurrentHashMap<K, Boolean> 对象的封装(所有映射的值都是Boolean.TRUE)。     
    `Set<String> words = ConcurrentHashMap.<String>newKeySet();`
* keySet     
    如果你已经有了一个map，那么keySet会返回所有键的Set。该Set是可变的。如果你删除该Set中的元素，那么相应的键(以及它的值)也会从映射中删除。但是你无法向这个键Set中添加元素，因为无法添加相应的值。于是Java8 又给ConcurrentHashMap添加了另一个keySet方法，它可以接受一个默认值，以使用与向Set中添加元素。

            Set<String> words = map.keySet(1L);
            words.add("Java");

    如果words中尚未存在"Java"，那么它当前有一个值，为1。

#### 并行数组操作
* Arrays.parallelSort(words)  并行排序
* Arrays.parallelSetAll  将数组中的值按照一个函数的计算结果过滤出来。改函数会获得元素索引，并计算该位置处的值     
    `Arrays.parallelSetAll(values, i -> i % 10) // values的值将被设置为0 1 2 3 4 5 6 7 8 9 10 0 1 2 ...`
* Arrays.parallelPrefix  将数组中的每个元素替换为指定关联操作的前缀的累积

        int [] values = new int[] {1, 2, 3, 4, 5, 6, 7, ... };

        // 排序后数组的值为：[1, 1 * 2, 1 * 2 * 3, 1 * 2 * 3 * 4, ...]
        Arrays.parallelPrefix(values, (x, y) -> x * y);


#### CompletableFuture
##### 回顾下`Future`
假设有如下方法：    
`public Future<String> readPage(URL url)`     
该方法会在一个单独的线程中读取一个网页，这一个过程需要花费一点时间。当你调用     
`Future<String> contents = readPage(url);`     
时，改方法会立即返回，同时你持有一个Future<String>对象。假设现在我们希望从页面中提取所有的URL，从而构建一个Web爬虫。现在我们有一个名为Parser的类，其中含有一个方法：    
`public static List<URL> getLinks(String page);`     
如何从上面得到的Future<String>中应用这个getLinks方法呢？只有一种方式，就是调用Future的get方法获取结果，然后调用getLinks方法：     

        String page = contents.get();
        List<URL> links = Parser.getLinks(page);

但是这时，调用get会被阻塞，直到readPage 方法完成，Future中存在可用结果。

##### 使用`CompletableFuture`
让我们对上面的readPage方法做些改动，使它返回一个 CompletableFuture<String> 对象。与普通Future对象不同，CompletableFuture对象拥有一个`thenApply`方法，你可以把进行后续处理的函数传递给它。     

        CompletableFuture<String> contents = readPage(url);
        CompletableFuture<List<String>> links = contents.thenApply(Parser::getLinks);

thenApply 方法不会被阻塞。它会立刻返回另一个Future对象。当第一个Future对象完成时，它的结果会发给getLink方法，然后该方法的返回值会成为最终的结果。

##### Future 流水线
在前面，我们已经了解到一个Stream 流水线的过程，由创建流开始，然后经过一个或多个转换过程，最后由一个终止操作结束。Future 对象的流水线也是这样。

* 创建 CompletableFuture 对象
   创建CompletableFuture对象通常都是由静态方法 `supplyAsync` 来完成。该方法需要一个 Supplier<T> 参数，即一个无参数、返回类型 T 的函数。该函数会在另一个线程中被调用。   
   仍使用上面的例子：`CompletableFuture<String> contents = CompletableFuture.supplyAsync(() -> blockingReadPage(url));`    
   CompletableFuture还有一个静态方法`runAsync`，它接受一个Runnable 对象作为参数，返回一个CompletableFuture<Void>对象。当你只是想一个接一个地执行操作，而不需要在操作之前传递数据时，可以使用该方法。
* 运行接下来的操作
    接下来，你可以使用 `thenApply` 或 `theApplyAsync` 方法，在`同一个线程`或`另一个线程中`运行另一个操作。不管使用哪个方法，你都需要提供一个函数，并且会得到一个 CompletableFuture<U> 对象，其中 U 表示函数的返回类型。    
    `CompletableFuture<List<String>> links = CompletableFuture.supplyAsync(() -> blockingReadPage(url)).thenApply(Parser::getLinks);`
* 处理结果
    `thenAccept` 方法接受一个 `Consumer` 函数 -- 即一个返回类型为 void 的函数。   
    `CompletableFuture<Void> links = CompletableFuture.supplyAsync(() -> blockingReadPage(url)).thenApply(Parser::getLinks).thenAccept(System.out::println);`

##### 编写异步操作
为了使用 CompletableFuture ，Java8提供了大量的方法。    
* 处理单个 Future 的方法

| 方法 | 参数     |  描述           |
| :------------- | :------------- |:-----------|
| thenApply  | T -> U   | 为结果提供一个函数    |
| thenCompose| T -> CompletableFuture<U> | 对结果调用一个函数，并执行返回的 Future 对象|
| handle     | (T, Throwable) -> U | 处理结果或者错误 |
| thenAccept | T -> void     | 同 thenApply 类似，但是结果为void类型|
| whenComplete| (T, Throwable) -> void | 同handle类似 但是结果为void类型|
| thenRun  |   Runnable  | 执行返回void的Runnable对象|

* 组合多个对象

| 方法     | 参数     |  描述
| :------------- | :------------- |
| thenCombine   | CompletableFuture<U>, (T, U) -> V      | 执行两个对象，并将结果按照指定的函数组合起来
| thenAcceptBoth| CompletableFuture<U>, (T, U) -> void   | 同thenCombine 类似，但是结果为void类型
| runAfterBoth | CompletableFuture<?>, Runnable  | 在两个对象完成后，执行Runnable对象
| applyToEither| CompletableFuture<T>, T -> V | 当其中一个对象的结果可用时，将结果传递给指定的函数
| acceptEither | CompletableFuture<T>, T -> void | 同applyToEither 类似，但是结果为void类型
| runAfterEither| CompletableFuture<?>, Runnable | 在其中一个对象结束后，执行Runnable对象
| static allOf | CompletableFuture<?>... | 在所有的Future对象结束后，并返回void结果
| static anyOf | CompletableFuture<?>... | 在任何一个Future对象结束后，并返回void结果

前三个方法会并行运行一个 CompletableFuture<T>(也就是方法的调用者)和一个 CompletableFuture<U>(方法的参数Future) 操作，并将结果组合(就是第二个函数参数)到一起。      
接下来三个方法会并行运行两个 CompletableFuture<T> 操作，只要其中任何一个结束，就会返回该结果并忽略其他的结果。    
最后静态方法 allOf 和 anyOf 可以接受一组可结束的 Future 对象，并返回一个 CompletableFuture<Void> 结果，当这些 Future 对象全部结束，或者他们中的任意一个结束时，该结果就会结束。没有结果会被传播出去。
