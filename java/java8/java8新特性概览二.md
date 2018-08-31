### 开场诗
《丑奴儿·书博山道中壁》 宋 辛弃疾  

少年不识愁滋味，爱上层楼。爱上层楼，为赋新词强说愁。

而今尽识愁滋味，欲说还休。欲说还休，却道天凉好个秋。

### stream
> Stream 是Java8中处理集合的关键抽象概念，它可以指定希望对集合进行的操作，但是将执行操作的时间交给具体的实现来决定。同时也可以使用并行的Stream APi来并行执行操作，使用多线程来计算每一段的总和与数量，再将结果汇总起来。

* 迭代器意味着特定的遍历策略，禁止来高效的并发执行
* 可以从 **集合、数组、生成器、迭代器** 中创建Stream
* 使用过滤器`filter`来选择元素，使用`map`来改变元素
* 其他改变Stream的操作包括`limit、distinct、sorted`
* 要从Stream中获得结果，请使用`reduction`操作符，例如 `count、 max、 min 、findFirst、 findAny`。其中一些方法会返回一个`Optional`值
* `Optional`类型的目的是为了安全替代使用null值。要想安全的使用它，需要借助于`ifPresent`和`orElse`方法
* 可以收集 集合、数组、字符串、或者 map 中的Stream结果
* `Collectors`类中的`groupingBy`和`partitioningBy`方法允许你对Stream中的内容分组，并获取每个组的结果
* Java8对原始类型 int、long、double提供了专门的Stream
* 当你使用 **并行Stream** 时，请确保不到有副作用(一致性问题)，并且 **考虑放弃排序约束**
* 为了使用 Stream API，需要了解一些函数式接口

* 使用Stream时，大概会通过三个阶段建立一个操作流：创建一个Stream -> 中间操作专拣位另一个Stream -> 终止操作获取一个结果

#### 创建stream
* 集合Collection接口中新添加的stream方法可以将任何集合转化为一个Stream
  例如：

      List<String> list = ...
      Stream<String> stream = list.stream();
* 数组，可以使用静态的`Stream.of`方法将它转化为一个Stream
  Stream.of 方法接收一个可变长度的参数
  例如：  

      //数组
      Stream<String> stream = Stream.of(contents.split("[\\P{L}]+"));
      //变长参数列表
      Stream<String> song = Stream.of("gently","down","the","stream","hehe");
* 通过`Stream.empty()`方法，创建一个不含任何元素的Stream
    `Stream<String> stream = Stream.empty()`

* Stream的 `generate`与`iterate`方法 创建无限Stream
  * `generate`方法接受一个参数列表(Supplier<T>接口的对象)

        // 创建一个包含常量值的无限Stream
        Stream<String> echos = String.generate(() -> "Echo");
        // 创建一个随机数字的无限Stream
        Stream<Double> randoms = Stream.generate(Math::random);

  * `iterate` 接受一个seed(种子)值，和一个函数(一个UnaryOperator<T>接口的对象)作为参数，并且对之前的值重复应用该函数

        //0、1、2、3、... 的无限序列
        Stream<BigInteger> integers = Stream.iterate(BigInteger.ZERO, n -> n.add(BigInteger.ONE));

* 还有其他可以产生Stream的方法
  * `Pattern` 类添加了一个`SplitAsStream`方法，能够按照正则表达式对`CharSequence`对象进行分隔，并创建Stream
  `Stream<String> words = Pattern.compile("[\\p{L}]++").splitAsStream(contents);`

  * 静态方法`Files.lines`会返回一个包涵文件中所有行的Stream。
     Stream接口继承了AutoCloseable接口，当在某个Stream上调用close方法时，底层的文件也会被关闭，为了确保关闭文件，最好采用Java7中提供的`try-with-resources`语句：

         try(String<String> lines = Files.lines(path)){
           //对lines的处理
         }

#### 将stream转换为另一个stream的中间操作
 * filter、map、flatMap方法
   * filter 过滤器  
   `String<String> longWords = words.filter(w -> w.length > 12);// 选择长度大于12的单词`

   * map   
   对Stream中的值进行转换(相当对一个Stream<T> 实例的所有值应用函数 `V f(T t)` 返回值V 可以是任何类型，并最终返回一个`Stream<V>`的实例)
   `Stream<String> lowercaseWords = words.map(String::toLowerCase);`

   * flatMap  
   当使用map方法时，会对流`Stream<T>`中的每个元素应用一个方法`V f(T t)`，并将方法的返回值收集到一个新的流`Stream<V>`中，然而当方法返回的不是一个具体的值，而是一个包涵多个值的流时(即f方法为`Stream<V> f(T t)`)，那map方法的结果就为一个包涵了多个流的流，即 `Stream<Stream<V>>`。
   例子：  

          class Utils{
            public static Stream<Character> characterStream(String s){
              List<Character> result = new ArrayList();
              for (char c : s.toCharArray()){
                result.add(c);
              }
              return result.stream();
            }
          }
          // 对一个stream进行map操作   
          Stream<Stream<Character>> result = words.map(Utils::characterStream);// 得到的是一个Stream<Stream<Character>> 包涵了Stream的Stream

          // 要将Stream<Stream<Character>>展开为一个只包含字符的流，需要使用flatMap方法
          Stream<Character> letters = words.flatMap(w -> characterStream(w));

* 提取子流 和 组合流
  * `limit` 方法用于裁剪指定长度的流   
      Stream<Double> randoms = Stream.generate(Math::random).limit(10);

  * `skip` 与limit正好相反，返回一个跳过指定元素的新流   
      Stream<Double> randoms = Stream.of(contents.split("[\\p{L}]+")).skip(1);

  * `Stream.concat` 静态方法 concat用语将两个流连接到一起   
      Stream<Character> combined = Stream.concat(Utils.characterStream("hello"), Utils.characterStream("world"));

  * `peek` 方法指定一个函数，在每次获取一个元素时，对该元素调用该函数，便于调试
      Stream<Double> randoms = Stream.iterate(1, p -> p * 2).peek(e -> System.out.println("Fetching " + e));

* 有状态的转换  
我所理解的有状态的转换，是 转换依赖与原始流的所有元素的值，也就是需要将原始流的值都遍历一遍。
  * `distinct` 根据原始流中的元素返回一个具有相同顺序、抑制了重复元素的新流。显然，这个操作需要将原始流的所有值都处理一遍。  
  `Stream<String> uniqueWords = Stream.of("merrily", "merrily", "merrily", "gently").distinct(); //只获取到一个 merrily`

  * `sorted` 排序  
  `Stream<String> longestFirst = words.sorted(Comparator.comparing(String::length).reversed());`

#### 终止操作获取一个结果
 * 聚合方法
    * `count`  `max` `min`   
    * `findFirst` 找到第一个并返回
    * `findAny` 找到任何一个并返回
    * `anyMatch`   
    接受一个Predicate<T> (即 boolean f(T t) - 一个从T 到boolean的函数对象) 参数，效果等同于  stream.filter().findAny()  

**Optional 类型**
    Optional<T> 对象是对一个T类型对象的封装，或者表示不适任何对象。一般比指向T类型的引用更安全，因为它不会返回null(正确使用的前提下)。
  * `get`方法   
          如果存在被封装的对象，那个get方法会返回该对象，否则会抛出一个NoSuchElementException。   
  * `ifPresent`方法     
          这个方法有两种使用方式：  
            * `if (optionalValue.isPresent()) optionalValue.get().someMethod()` //和判断 value != null 并没有太大区别   
            * `optionalValue.isPresent(v -> process(v));` // 每有操作的返回值   
  ＊ `map` 方法  
          `Optional<Boolean> added = optionalValue.map(results::add);` // added 有可能是以下三种值：被封装到Optional中的true或false(根据optionalValue值是否存在)，或者是一个空的可选值  
  * `orElse` 设置一个空值的替代值   
          `String result = optionalValue.orElse("");` //封装字符串如果没有返回 空字符串""   
          `String result = optionalValue.orElse(() -> System.getProperty("user.dir"));`   //该函数在北需要时才会被调用
  * `orElseThrow` 在没有值的时候抛出一个异常   
          `String result = optionalValue.orElseThrow(NoSuchElementException::new);`
  * 创建可选值  
      * `Optional.of(result)`
      * `Optional.empty()`
      * `Optional.ofNullable(result)` 如果result不为null时，会返回Optional.of(result)，否则会返回Optional.empty()  
  * 使用`flatMap` 来组合可选值函数
        s对象如果有一个返回Optinal<T>的方法 f，并且目标类型T有一个会返回Optional<U>的方法g。这时 s.f().g() 是不可行的，因为 s.f()返回的是Optional<T>并不是T，此时可以这样操作 `Optional<U> = s.f().flatMap(T::g);` 如果s.f()存在则会继续调用，否则返回一个空的Optional<U>。此时Optional可以看作一个元素数为1的流，与流的flatMap作用一致。

#### 聚合操作 `reduce`
  当我们希望对元素求和，或者以其他方式将流中的元素组合为一个值时，可以使用聚合方法。   
  * 使用一个二元函数  

          Stream<Integer> values = ...   
          Optional<Integer> sum = values.reduce((x, y) -> x + y);
  * 提供标识值

          Stream<Integer> values = ...
          Optinal<Integer> sum = values.reduce(0, (x, y) -> x + y);// 当流为空时，返回标识值 0
  * 对属性进行聚合
      如果我们想对流中的元素的某个属性进行聚合，比如 String 的 length() 函数得到的值：

          int result = words.reduce(0,
            (total, word) -> total + word.length(),//累加器函数，该函数会被重复调用，形成累加值。
            (total1, total2) -> total1 + total2);// 当并行计算时，会形成累加值，所以要提供第二个函数，将形成的多个累加值再累加起来。

#### 收集结果
当需要将Stream以聚合值之外的其它形式返回时。
  * 收集到数组中
        Stream<String> words = ...
        String[] result = words.toArray(String[]::new);
  * 列表  
    `List<String> result = stream.collect(Collectors.toList());`  
    `TreeSet<String> result = stream.collect(Collectors.toCollection(TreeSet::new))` //控制得到的Set类型
  * 字符串的收集  
    `String result = stream.collect(Collectors.joining());//将所有的字符串连接并收集`    
    `String result = stream.collect(Collectors.joining(", ")//加分隔符)`  
    `String reuslt = stream.map(Object::toString).collect(Collectors.joining()); //流包含字符串以外的对象`  
  * 数值的收集
    对数值进行收集，并希望获取 总和、最大值、 最小值、平均值时，可以使用 Collectors.summarizingInt(Integer|Long|Double)

        IntSummaryStatistics summary = words.collect(Collectors.summarizingInt(String::length));
        double averageWordLength = summary.getAverage();
        double maxWordLength = summary.getMax();

  * 收集到Map中
    对于一个Stream<Person>实例personStream有

    * Person 的 id 作为key， name作为value

      `Map<Integer, String> idToName = personStream.collect(Collectors.toMap(Person::getId, Person::getName));`

    * 以id作为key， 元素自己作为 value

      `Map<Integer, Person> idToPerson = personStream.collect(Collectors.toMap(Person::getId, Function.Identity()));`

#### 分组和分片
**以下所有直接使用方法的均视为直接静态引用了Collectors.***
  * 分组
  例子：对本地可用语言环境进行分组

        //获取本地可用语言环境
        Stream<Locale> localeStream = Stream.of(Locale.getAvailableLocales());
        //分组一：按照国家分组
        Map<String, List<Locale>> countryToLocale = localeStream.collect(Collectors.groupingBy(Locale::getCountry));
        //分组二：当分类函数是一个 Predicate<T>(即一个返回boolean值的函数)时，流元素会被分为两组列表，一组是函数返回true的元素，另一组是函数返回false的元素。
        //这种情况下，使用 Collectors.partitioningBy() 会更有效率。
        Map<String, List<Locale>> englishAndOtherLocales = localeStream.collect(Collectors.partitioningBy(l -> l.getLanguage().equals("en")));

        // 三：goupingByConcurrent 方法会返回一个并发map，用于并行流时可以并发的插入值。
        Map<String, List<Locale>> countryToLocales = localeStream.parallel().collect(Collectors.groupingByConcurrent(Locale::getCountry));

    对分组后的元素进行 downstream 处理
    * counting 返回所收集元素的总个数

          // counting 返回收集元素的总个数
          Map<String, Long> countryToLocalesCount = localeStream.collect(Collectors.groupingBy(Locale::getCountry, Collectors.counting()));

    * summing(Integer|Long|Double) 方法接受一个函数作为参数，应用到收集的元素，并将结果求和

          //summing求和
          Map<String, Integer> stateToCityPopulation = cities.collect(Collectors.groupingBy(Locale::getState, Collectors.summingInt(City::getPopulation)));

    * maxBy 和 minBy 会接受一个比较器，生成一个最大值和最小值

          Map<String, City> stateToLargestCity = cities.collect(Collectors.groupingBy(City::getState, Collectors.maxBy(Comparator.comparing(City::getPopulation))));

    * mapping 方法会将一个函数应用到 downstream结果上，并且需要另一个收集器来处理结果。

          //这里，先将城市按照州进行分组，在每个州中，我们生成每个城市的名称并按照其最大长度进行聚合
          Map<String, Optional<String>> stateToLongestCityName = cities.collect(
            groupingBy(City::getState,
              mapping(City::getName,
                maxBy(Comparator.comparing(String::length)))));

    * 如果 grouping 或者mapping 函数的返回类型时int、lang、或者double，可以将元素收集到一个 summary statistics对象中。

          Map<String, IntSummaryStatistics> stateToCityPopulationSummary = cities.collect(
            groupingBy(City::getState,
              summarizingInt(City::getPopulation))
            );

    * reducing 方法会对 downstream 元素进行一次普通的聚合操作。  
      该方法有三种形式：
      * reducing(binaryOperator)
      * reducing(identity, binaryOperator)
      * reducing(identity, mapper, binaryOperator)

            // 按照州分组，并将城市影射(mapper)到自己的名称上，然后将他们追加起来
            Map<String, String> stateToCityNames = cities.collect(
              groupingBy(City::getState,
                reducing("", City::getName,
                (s, t) -> s.length() == 0 ? t : s + "," + t))
              );
            // 另一种实现方式
            Map<String, String> stateToCityNames = cities.collect(
              groupingBy("",
              mapping(City::getName,
                joining(", "))
              ));



  如上，downstream收集器可以产生非常复杂的表达式。我们应该只有在为了通过`groupingBy`或`partitioningBy`来产生"downstream"map时，才使用它们。其它情况下，只需要对流直接应用map，reduce，max，或者min方法即可。

#### 原始类型流
  将整数包装成相应对象是一个很低效的做法，对于其它原始类型 double，float，short，char，byte，及boolean也是一样。为此，Stream API提供了IntStream，LongStream和DoubleStream等类型。专门用来直接存储原始类型值。  
  **如果要存储 short、char、byte、boolean类型的值，请使用 IntStream；  
  如果要存储 float 类型的值，请使用 DoubleStream。**
  * IntStream stream = IntStream.of(1, 2, 3, 4, 5);
  * IntStream stream = Arrays.stream(values, from, to); //values是一个 int 数组
  * IntStream zeroToNinetyNine = IntStream.range(0, 100);
  * IntStream zerToHundred = IntStream.rangeClosed(0, 100);
  * IntStream codes = stringInstance.codePoints();    
    //CharSequence接口有两个方法：codePoints和chars 可以生成包含字符的Unicode代码的流，或者包涵UTF-16编码的 *代码单元* 的IntStream。
  * 对象流转换为原始类型流: mapToInt 、mapToLong、 mapToDouble    
    `IntStream lengths = words.mapToInt(String::length);`
  * 原始类型流转向对象流: boxed 方法
    `Stream<Integer> integers = IntStream.range(0, 10).boxed();`

  * toArray 方法会返回一个原始类型的数组
  * 产生Optional结果的方法会返回一个 OptionalInt、OptinalLong 或者 OptionalDouble 类型。这些类型于Optional类型相似，只是没有get方法，而是对应的getAsInt、getAsLong、getAsDouble类代替

  * 方法 sum、average、max、min 会返回总和、平均值、最大值和最小值。在对象流中并没有这些方法
  * summaryStatistics 方法会产生一个 IntSummaryStatistics、LongSummaryStatistics、DoubleSummaryStatistics 对象，可以同时获得总和、平均值、最大值、最小值
  * Random 类现在提供了 ints、longs、doubles 这些方法，来返回包涵随机数字的原始类型流

#### 并行流
  首先，你得有个并行流：
  * Collection.parallelStream()
  * Stream.of(words).`parallel()`;
  并行流注意事项：
  * 竞态条件 ： 你要确认传递给并行流操作的函数是线程都是安全的。
  * 关于排序：默认情况下，从有序集合(数组或列表)，范围值，生成器 或迭代器，或者调用 Stream.sorted所产生的流都是有序的。
    有序的流会按照原始元素的顺序进行累计，并且是完全可预测的。如果你将同一个操作运行两次，你将会得到一模一样的结果。有序并不会妨碍并行。例如，当计算stream.map(fun)时，流可以被分片为n段，每一段都会被并行处理。然后按顺序将结果组合起来。   
    当不考虑有序时，一些操作可以更有效的并行运行。调用`Stream.ubordered()`方法可以不关心排序。Stream.distinct就是一个可以从中获益的方法。对于一个有序的流，distinct会保留所有相等元素的第一个。这样就会阻碍并行，因为要处理某段元素的线程只有在之前的元素段处理完毕后，才知道自己应该丢弃哪些元素。
  * 关于改变流底层的集合
    由于intermediate(中间)流操作是延迟的，所以当终止操作执行时他有可能会改变集合。

        //正确的代码
        List<String> wordList = ...;
        Stream<String> words = wordList.stream();
        wordList.add("END");
        long n = words.distinct().count();//触发流中间操作，此时底层集合改变生效

        //错误的代码
        Stream<String> words = wordList.stream();
        words.forEach(s -> if(s.length() < 12) wordList.remove(s));//错误

#### 函数式接口
在Stream API中使用的函数式接口

| 函数式接口 | 参数类型     |        返回类型     | 描述                |
| :------------- | :------------- |:-----------|:--------------------|
| Supplier<T>       | 无      | T         | 提供一个T类型的值|
| Consumer<T>       | T       |  void     | 处理一个T类型的值|
| BiConsumer<T, U>  | T, U    | void      | 处理T类型和U类型的值|
| Predicate<T>      | T       | boolean   | 一个通过给定T类型值计算Boolean值的函数|
|ToIntFunction<T>   | T        | int      |  计算int 的函数|
|ToLongFunction<T>  | T        | long     |  计算 long的得函数|
|ToDoubleFunction<T>| T        | double    | 计算double的得函数|
|IntFunction<R>     | int      | R         | 参数为int 返回R     |
|LongFunction<R>    | long     | R         | 参数为long 返回R|
|DoubleFunction<R>  | double   | R          | 参数为double返回R|
|Function<T, R>     | T        | R          | 参数为T返回R|
|BiFunction<T, U, R>| T, U     | R          | 参数为T、U、返回R|
|UnaryOperator<T>   | T        | T          | 对类型T进行的一元操作|
|BinaryOperator<T>  | T , T    | T          | 对T类型进行的二元操作|
