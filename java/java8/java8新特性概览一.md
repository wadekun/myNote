### 题记
Java8推出已经两年了，这本书买了也有一年多了，最近才开始看😂。Oracle官方也已经宣布不再更新Java7，同时伴随着Spring Boot的推出与不断更新，越来越多的Java应用会使用Java8。so，抓紧来学习下Java8的新特性。做一下读书笔记。

### lambda
> lambda 表达式就是带有参数的表达式。   

#### lambda表达式语法
格式：参数、箭头（->）、表达式   
`(args) -> {expression}`   

例1：java线程的实现   

    // 线程的业务逻辑   
    class Worker implements Runnable {   
      public void run(){  
        doWork();   
      }    
    }   
    // 将该实例提交到一个线程池中，或者直接启动一个新的线程。  
    Worker w = new Worker();  
    new Thread(w).start();

    // 使用lambda，可以直接这样写  
    new Thread(() -> doWork()).start();

例2: 比较器

    // 一个根据字符串长度来比较的Comparator   
    class LengthComparator implements Comparator<String> {  
      public int compare(String first, String second){   
          return Integer.compare(first.length(), second.length());  
      }  
    }  
    Arrays.sort(strings, new LengthComparator());  

    // 使用lambda，可以直接这样写  
    Arrays.sort(strings, (first, second) -> Integer.compare(first.length(), second.length()));
#### 函数式接口
> 对于**只包含一个抽象方法**的接口，我们**可以通过lambda表达式来创建该接口的对象**。这种接口被称为函数式接口。

例如上面提到的Runnable, Comparator 都是只有一个抽象方法，可以直接通过lambda表达式来创建其实例。  
我们可以在任意的函数式接口上标注`@FunctionalInterface`注解，这样做有两个好处。一：编译器会检查标注该注解的实体，检查它是否是只包含一个抽象方法的接口。二：在javadoc页面也会包含一条声明，说明这个接口是一个函数式接口。  
#### 方法引用
> 有些时候，如果想要传递给其他代码的操作已经有实现的方法了。可以直接将方法传递给对方。   

例如在按钮被点击时打印event对象：    
`button.setOnAction(event -> System.out.println(event));`

直接将println方法传递给setOnAction方法：  
`button.setOnAction(Syetem.out::println);`  

希望不区分大小写对字符串排序：  
`Arrays.sort(strings, String::compareToIgnoreCase)`  

如以上代码所示，`::`操作符将方法名和对象/类的名字分隔开来。以下是三种主要使用情况：   
* 对象::实例方法
* 类::静态方法
* 类::实例方法  

在乾两种情况中，方法引用等同于提供方法参数的lambda表达式。如上所述的 `button.setOnAction(System.out::println)//System.out.println()以action为入参，无返回值`。等同于`button.setOnAction(event -> System.out.println(event))`。`Math::pow`等同于`(x,y) -> Math.pow(x,y)//Math.pow()以两个数值为入参，返回一个数值`。在第三种情况(类::实例方法)中，第一个参数会成为之行方法的对象。例如`String::compareToIgnoreCase`等同于`(x,y) -> x.compareToIgnoreCase(y)//第一个参数为方法的执行者，第二个参数为入参`。
此外还可以捕获方法引用中的this参数。例如：`this::equals`等同于`x -> this.equals(x)`。同样可以使用super。

**注：lambda的1.方法业务、2.方法的入参、3.方法的反回结果 要与外部的使用场景相符。即方法的的入参、返回结果类型要相符。**

#### 构造器引用
> 同方法引用类似，不同的是在构造器引用中的方法名是new。例如：Button:new 表示Button类的构造器引用。  

例如：通过一个字符串列表构造一个stream   

    List<String> labels = ...
    // 编译器会从上下文推断并挑选出只带有一个String参数的Button构造器
    Stream<Button> stream = labels.stream().map(Button:new);
    List<Button> buttons = stream.collect(Collectors.toList());

    //直接返回一个数组
    Button[] buttons = labels.toArray(Button[]::new);
#### 变量作用域
在lambda表达式中可以捕获所在外部环境的变量，但这些被捕获变量的值必须是final的或者有效的final值（即不会被更改的值）。  
例：  

    public static void repeatMessage(String text, int count){
      Runnable r = () -> {
        while(count > 0){
          System.out.println(text);
          count--;  // 非法的操作！！！不可以更改捕获的外部变量的值
        }
      };
    }
另外，lambda表达式中使用this关键字时，你会引用创建该lambda表达式的方法的this参数。
例：

    public class Application{
      public void doWork(){
        Runnable r = () -> {
          this.toString(); // 调用的是Application的toString而不是Runnable实例的toString
        };
      }
    }

#### 接口中的默认方法
在Java8之前，接口中添加扩展方法时，接口的所有实现类必须添加该方法的实现。这在扩展接口时是非常难以接受的。为了解决这个问题，Java设计者们在接口中新增了默认方法来解决这个问题。  
例如有如下接口：

    interface Person{
      long getId();
      //默认方法
      default String getName() {return "John Q. Public "}
    }
实现Person接口的具体类必须实现getId 方法，可以选择性的实现getName方法。这样Java开发者们就可以往接口中方便的扩展实现逻辑。
当有另外一个接口：

    interface Named{
      default String getName() {return getClass.getName  + hashCode()}
    }
此时有类Student同时实现Person 和 Named接口时，必须给出 getNamed的实现。否则编译器会报错。因为编译器无法知道你选择哪个接口的实现。
不过可以通过这种方法指定具体的接口实现：

    class Student implements Person, Named {
      public String getName(){
        Person.super.getName(); // 指定Person接口中的实现
      }
    }
当然此时Student继承了一个父类如果也有getNamed方法那就好办了，因为在Java中，类优先于接口，接口中的相同方法会被忽略掉。
#### 接口中的静态方法
在Java8之前，大多数接口都会配备一个工具类，例如Collection/Collections,Path/Paths，接口中定义规范，类中给出工具方法。Java8在接口中新增的静态方法就是酱这种工具类的静态方法直接移至接口中。  
例如Comparator接口中新增了一个实用的方法comparing，用来接收一个键提取函数，并产生一个用来比较所提取的键的比较器。  
例如：`Comparator.comparing(Student::getNamed);`就返回一个通过getName方法返回值进行比较的比较器。