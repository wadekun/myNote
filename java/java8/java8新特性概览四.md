### 杂项改进
除了lambda和stream Api等重大改进外，Java8 还对库进行了大量微小却实用的改进。包括对 字符串、数字、数学、集合、文件、注解、正则表达式及JDBC等。

#### 字符串
* `String.join()`
  我们经常会遇到这样的需求：将多个字符串通过一个分隔符链接起来。现在Java8中 String 类中新增的 `join` 方法可以实现这个功能。这是Java8中String类添加的唯一一个方法。字符串可以来自于一个数组或者一个`Iterable<? extends CharSequence>` (可迭代的)对象  

          String joined = String.join("/", "usr", "local", "bin"); // "usr/local/bin"
          System.out.println(joined);
          String ids = String.join(", ", ZonedId.getAvailableZoneIds()); // 将可用时区id连接成为字符串
          System.out.println(ids);// 在我的电脑上：Asia/Aden, America/Cuiaba, Etc/GMT+9, Etc/GMT+8, Africa/Nairobi, America/Marigot...

#### 数字类
* BYTES 字段 与 SIZE 字段
  从Java5开始，7中原始类型的包装类(不包含Boolean)都提供了一个`静态字段SIZE`，用来表示该类型以`bit`为单位的长度。在Java 8 中，他们都提供了一个`BYTES`字段，以byte为单位来表示该类型的长度，以便于无法被8整除的情况。
* hashCode 方法
  所有原始类型的包装类都提供了一个静态的hashCode方法，用来返回与实例方法想用的哈希码，这样就不需要在经历 装箱/拆箱 的过程了。
* 静态 sum、max、min
  Short、Integer、Long、Float、Double这5种类型，现在分别提供了静态方法 sum、max、min，用来在流操作中作为聚合(reduce)函数使用。同样，Boolean类现在也提供了静态方法 logicalAnd、logicalOr、logicalXor
* 无符号计算
  Integer类现在支持无符号计算。例如，以往Byte表示从 -128到127的范围，现在可以调用静态方法 Byte.toUnSignedInt(b);来获取一个从-到255的值。一般来说，使用无符号数字，你会丢失负数并获得原来两倍范围的整数。   
  Integer和Long类中新增了处理无符号值的 `compareUnsigned`、`divideUnsigned` 和 `remainderUnsigned` 方法。你不需要特殊的方法来计算加法、减法 和 乘法。操作符 `+` 和 `-`已经能够正确的处理无符号值。由于大于 `Integer.MAX_VALUE`的无符号整数相乘会溢出，对于溢出的数值，应当调用`toUnSignedLong`将值作为长整形。
* BigInteger.(long|int|short|byte)ValueExact()
  BigInteger类新增加了实例方法 (long|int|short|byte)ValueExact，分别用来返回 long、int、short 或者 byte。并且当值不在目标范围内时抛出一个 ArithmeticException异常。

#### 新的数学函数
* (add|subtract|multiply|increment|decrement|negate)Exact 参数为int和long类型的值
  如果结算结果溢出会抛出一个异常。 `toIntExact`方法可以将一个long值转换为等价的int值
* floorMod(取余)、floorDiv(整除)
* Math.nextDown() Math.nextUp()
    Math.nextDown() 返回一比指定数字小，但最接近指定数字的浮点数字
#### 集合
 集合库的最大改变就是支持了Stream。同时，还有其他的一些略小改动。


 | 类/接口      | 新方法        |
 | :------------- | :------------- |
 | Iterable     | forEach       |
 | Collection   | removeIf  |
 | List  | replaceAll |
 | Map    | forEach, replace, replaceAll, remove(key, value)(只有当key到value的映射存在时才删除), putIfAbsent, compute, computeIf(Absent or Present), merge  |
 | Iterator | forEachRemaining |
 | BitSet  | stream |

* removeIf 立即删除匹配的值
* forEachRemaining 将剩余的迭代元素都传递给一个函数
* BitSet 类有一个方法可以生成集合中的所有元素
#### Collections类

#### 比较器
Comparator接口新增的静态方法`comparing`可以接受一个“键提取器”，将某类型映射为一个可比较的类型(例如String)。  
例如：`Arrays.sort(people, Comparator.comparing(Person::getName));`     
通过`thenComparing`方法进行多级比较   
例如： `Arrays.sort(people, Comparator.comparing(Person::getLastName)).thenComparing(Person::getFirstName);`,如果两人拥有相同的姓，就会使用第二个比较器。    
Comparator新增的`comparingInt`、`comparingLong`、`comparingDouble`方法可以避免int、long、double值得装箱拆箱。    
`Arrays.sort(people, Comparator.comparingInt(p -> p.getName().length()));`    
当键提取器可以返回null时，可以使用`nullsFirst`或者`nullsLast`方法，该方法接受一个比较器来比较两个字符串。    
例如： `Arrays.sort(people, Comparator.comparing(Comparator.nullsFirst(Comparator.naturalOrder())))`，   
naturalOrder方法可以为实现了Comparable接口的类生产一个比较器。 `reverseOrder`与`naturalOrder().reverse()`可以实现倒序。
#### 使用文件
java8为使用流读取文件行及访问目录提供了一些简便的方法。

使用`Files.lines()`方法。它会产生一个包含字符串的流，每个字符串就是文件的一行。

      Stream<String> lines = Files.lines(path); // lines方法默认会以 UTF-8字符编码打开文件
      Optional<String> passwordEntry = lines.filter(s -> s.contains("password")).findFirst();

Stream 接口继承了 AutoClosable 类。可以使用Java7提供的try-with-resources 来关闭底层打开的文件：

      try (Stream<String> lines = Files.lines(path)) {
        Optional<String> passwordEntry = lines.filter(s -> s.contains("password")).findFirst();
      } // 这里首先会关闭流，然后紧接着关闭文件

如果希望关闭流的时候收到通知，可以附加一个onClose方法：
      try (Stream<String> lines = Files.lines(path).onClose(() -> System.out.println("closing..."))) {
        Optional<String> passwordEntry = lines.filter(s -> s.contains("password")).findFirst();
      } // 这里首先会关闭流，然后紧接着关闭文件
#### Base64编码
Base64编码可以将一组字节序列编码为一个(更长的)可打印的ASCII字节序列。它经常用于电子邮件消息中的二进制数据，以及“基本的”HTTP认证。

现在Java8提供了一个标准的编码器和解码器。

      //编码：
      Base64.Encoder encoder = Base64.getEncoder();// getEncoder, getUrlEncoder, getMimeEncoder
      String original = username + ":" + password;
      String encoded = encoder.encodeToString(original.getBytes(StandardCharsets.UTF_8));

      // 还可以“包装”一个输出流，这样所有发送给它的数据都会自动进行编码。
      Path originalPath = ..., encodedPath = ...;
      Base64.Encoder encoder = Base64.getMimeEncoder();
      try (OutputStream output = Files.getOutputStream(encodedPath)) {
        Files.copy(originalPath, encoder.wrap(output)); // 源地址copy到编码地址
      }

      // 解码， 只需要将这些操作反过来
      Path encodedPath = ..., originalPath = ...;
      Base64.Encoder = Base64.getMimeEncoder();
      try (InputStream input = Files.newInputStream(encodedPath)) {
        Files.copy(decoder.wrap(input), decodedPath); // 从编码地址 copy到解码地址
      }

#### 注解
* 可重复的注解 @Repeatable
* 可用于类型的注解
* 方法参数反射，及可以通过反射获取方法参数的名称
#### 其他一些细微的改进
* Null检查，Objects类新增了两个静态predicate方法isNull 和 nonNull。可以在流中使用，来过滤元素
* 正则表达式， Pattern 新增 splitAsStream方法，可以将一个CharSequence按照正则表达式进行分割
* 语言环境
* JDBC。java8中，jdbc升级到了版本4.2。java.sql 包中的Date,Time,Timestamp类都提供了一些方法，可以与java.time报下对应的LocalDate,LocalTime,LocalDateTime互相转换
* Statement类新增了一个executeLargeUpdate方法，用来执行修改函数会超过Integer.MAX_VALUE的更新操作
* JDBC4.1 为Statement和ResultSet执行了一个泛型方法，getObject(column, type)。其中type是一个Class实例   
    例如：`URL url = result.getObject("link", URL.class);` 当然也提供了相应的setObject方法。

### 容易被忽略的Java7特性
* 对所有实现AutoCloseable接口的对象使用try-with-resources语句。
* 如果在关闭一个资源时抛出另一个异常，try-with-resources语句会重新抛出原来异常(try-catch语句块中的异常)。
* 反射操作的异常新增了一个公共的父类ReflectiveOperationException。
* 使用Path 接口来替代File类。
* 使用`Files`类的静态方法来读取，写入，删除，创建文件 以及创建目录。
* 使用`Objects.equals`
* `Objects.hash`

### JavaScript引擎－Nashorn
  `todo...`

### JavaFX
  `todo...`
