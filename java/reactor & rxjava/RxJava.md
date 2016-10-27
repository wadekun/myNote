# RxJava introduction
> RxJava – Reactive Extensions for the JVM – a library for composing asynchronous and event-based programs using observable sequences for the Java VM.

JVM的响应式扩展 - 一个在 Java VM 上使用可观测的序列来组成异步的、基于事件的程序的库。

一个异步操作的库（push-based）。

project : https://github.com/ReactiveX/RxJava

# 编程模型
RxJava的基本组成是 `Observables`(消息/事件 发送者 | 事件源) 和 `Subscribers`（消息/事件 消费者）.

Observable 可以发送任意数量的 消息/事件（包括空消息），当消息被成功处理或者出错时，流程结束。    

`Observable`会调用它的每个`Subscribers`的 `onNext()` 函数，并最终以 `Subscribers` 的 `onComplete()` 或者 `onError()`结束。

RxJava看起来很像是观察者模式，但不同的一个关键点是：Observable 一般只有等到有Subscriber 订阅它，才会开始发送消息。

# Hello World
通过一个 hello world来介绍 RxJava的基本编程模型。


使用 **Observable.create()** 创建一个Observable对象
```java
/**
     * 使用 Observable.create() 创建一个 Observable 实例
     * @return
     */
    public static Observable<String> createObservable() {

        Observable<String> myObservable = Observable.create(new Observable.OnSubscribe<String>() {
            @Override
            public void call(Subscriber<? super String> subscriber) {
              // 发射出一个字符串就结束
                subscriber.onNext("hello, world");
                subscriber.onCompleted();
            }
        });

        return myObservable;
    }
```

通过 **Subscriber 抽象类** 来创建一个Subscriber对象
```java
/**
     * 通过 Subscriber 类创建一个Subscriber对象
     * @return
     */
    public static Subscriber<String> createSubscriber() {

        // 消费Observable发出的字符串
        Subscriber<String> mySubscriber = new Subscriber<String>() {
            @Override
            public void onCompleted() {
                System.out.println("subscriber completed...");
            }

            @Override
            public void onError(Throwable e) {
                System.out.printf("subscriber error = [%s] \n", e.getLocalizedMessage());
            }

            @Override
            public void onNext(String s) {
                System.out.printf("subscriber onNext = [%s] \n", s);
            }
        };

        return mySubscriber;
    }
```

通过 **Observable的 subscribe()方法** 建立订阅关系
```java
public static void subscription() {
        Observable<String> myObservable = createObservable();

        Subscriber<String> mySubscriber = createSubscriber();

        // 通过 Observable的 subscribe() 方法建立订阅关系
        myObservable.subscribe(mySubscriber);
    }
```

# 更高级的用法
接触更高级的API

## Observable的创建
1. `Observable.just(T)` 创建只有一条消息/事件 的Observable
2. `Observable.from()`  创建有一坨事件  的Observable
3. ...

```java
Observable<String> observable = Observable.just("hello, world");
```

可以链式调用，并且应用 java8 的lambda
```java
Observable.just("hello, world").subscribe(value -> System.out.print(value));
```

## Operators （操作符）
操作符就是对Observable 发送的 消息/事件  在发射前进行一系列的操作。

### map 将一个事件转换为另一个事件
```java
Observable.just("hello").map(value -> value + ", world !").subscribe(System.out::println);
```

### filter

### flatMap

###

# subscribeOn()

# observableOn()
