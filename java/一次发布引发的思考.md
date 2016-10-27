# 起因
线上的功能bug，需要替换一个class文件（）。把class文件发给运维N多次，结果都发现线上的代码依然有问题。反编译后发现，并没有替换成功。

后来经架构师提示，同时替换了`$1.class`后，发布成功。

# 动手

## 例一
```java

// 在 com/liangck 目录下
package com.liangck;

public class TestJavac {

  void Test() {

      new Runnable(){
         public void run() {
           System.out.println("....sdfsfds");
         }
      };
  }

  private class innerClass {
     void biubiubiu() {
       System.out.println("biubiubiu...");
     }
  }

  public static void main(String[] args) {
    System.out.println("Test Javac...ooo");
  }
}

```

此时 使用 `javac`命令编译：

* 在 `com/liangck` 目录下：`javac TestJavac`
* 在 `com` 的同级目录下：`javac com/liangck/TestJavac.java`

可以看到在 `com/liangck`目录下生成了三个 `.class`文件：

* `TestJavac$1.class`
* `TestJavac$innerClass.class`
* `TestJavac.class`

## 例二
上面的TestJavac 把 `new Runnable` 部分注释掉
```java
// 在 com/liangck 目录下
package com.liangck;

public class TestJavac {

  void Test() {
    /**
      new Runnable(){
         public void run() {
           System.out.println("....sdfsfds");
         }
      };
      **/
  }

  private class innerClass {
     void biubiubiu() {
       System.out.println("biubiubiu...");
     }
  }

  public static void main(String[] args) {
    System.out.println("Test Javac...ooo");
  }
}
```

此时，使用 `javac` 进项编译，可以看到生成了两个`.class` 文件：

* `TestJavac$innerClass.class`
* `TestJavac.class`

## 例三
把内部类 `innerClass` 注释掉：
```java
package com.liangck;

public class TestJavac {

  void Test() {
    /**
      new Runnable(){
         public void run() {
           System.out.println("....sdfsfds");
         }
      };
      **/
  }
/**
  private class innerClass {
     void biubiubiu() {
       System.out.println("biubiubiu...");
     }
  }
**/
  public static void main(String[] args) {
    System.out.println("Test Javac...ooo");
  }
}

```

编译，可以看到一个 `.class`文件：

* `TestJavac.class`

## 运行（另一个问题）

使用 `java`命令运行：

* 在 `com/liangck`目录下：`java TestJavac` 或 `java com.liangck.TestJavac`
  报错：错误: 找不到或无法加载主类 com.liangck.TestJavac （class not found）

* 在 `com/` 目录下： `java -cp .. com.liangck.TestJavac`  运行成功
* 在 `com` 同级目录下： `javac com/liangck/TestJavac.java` 运行成功

# 总结

## 第一个问题
javac在编译时，会把当前类中的内部类 以 `外部类名+$+内部类名` 的格式生成 `.class`文件

javac编译时，会把当前类中的匿名内部类 以 `外部类名称+$+序号` 其中序号为 1,2,3,4.... ， 的格式生成`.class` 文件

## 第二个问题
javac 编译时，总是将当前工作目录 (.) 添加到类路径，而不管您是否曾显式地要求这样做。

`java Helloworld` 命令执行class文件时，会在 CLASSPATH 目录下找相应的 class 文件。

`java -cp . HelloWorld` 命令指定当前目录下查找 class文件

java 命令执行 class 文件，必须 带上class的完整类路径， 如示例中的 `com.liangck.TestJavac`

## 最后
原来，这次在某service类中（化名为`OutServiceImpl`）改动的代码使用了 google guava的`Collections2.transform(Collection collection, Function funciton)`，来对一个集合进行转换，其中`new Funciton(){}`的部分其实就是一个匿名内部类，
  会生成一个`OutServiceImpl$1.class` 文件，然而这个文件并没有被替换。

其实以前还是了解过的。。。只不过许久没看，忘了。。。

  因为这个问题，浪费了大家三个多小时，现在想想还是有些内疚。。。

  基础的重要性。。。
