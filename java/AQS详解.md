# AbstractQueuedSynchronizer(AQS) 概述
`AbstractQueuedSynchronizer`抽象队列同步器，定义了一套多线程访问共享资源的同步器框架，Java中许多同步工具类都依赖于它，如常用的`ReentrantLock/Semaphore/CountDownLatch`。

# 框架

图片来自 http://www.cnblogs.com/waterystone/p/4920797.html

![](imgs/aqs_framework.png)

`AQS`维护了一个`volatile int state`变量（代表共享资源）。和一个`FIFO`队列(CLH队列)，多线程争用资源被阻塞时会进入此队列。

`state`的三个操作： 
* `getState()`
* `setState()`
* `compareAndSetState()`

AQS定义资源有两种使用方式：Exclusive（独占，当前时刻只能一个线程运行，如ReentrantLock）和Share（共享，多个线程可同时执行，如Semaphore、CountDownLatch）。
不同的自定义同步器争用共享资源的方式也不同。**自定义同步器只要实现资源state的获取和释放即可**，至于线程等待队列的维护（线程获取资源失败后 阻塞入队、唤醒出队等）AQS已经实现好了。自定义同步器实现时主要实现以下几个方法：
1. `isHeldExclusively()`：该线程是否正在独占资源。只有用到`condition`才需要去实现它。
2. `tryAcquire(int)`：独占方式，尝试获取资源。成功返回`true`，失败返回`false`。
3. `tryRelease(int)`：独占方式，尝试释放资源。成功返回`true`，失败返回`false`。
4. `tryAcquireShared(int)`：共享方式尝试获取资源。负数表示失败。0表示成功，但没有可用资源。整数表示成功，且有剩余资源。
5. `tryReleaseShared(int)`：共享方式尝试释放资源。如果释放后允许唤醒后续等待节点返回`true`，否则返回`false`。

独占模式以`ReentrantLock`为例。`state`初始化为0。A线程`lock`时，调用`tryAcquire(1)`获取资源资源，获取成功，state值为1。此时，其他线程尝试获取资源就会失败。只有当A线程`unlock`时，调用`tryRelease(1)`释放资源。在`ReentrantLock`中，线程A可以使用`tryAcquire()`重复获取资源，当然每次`tryAcquire`必须通过一次`tryRelease`来释放。只有当`state == 0`时，其他线程才可以获取资源。

共享模式以`CountDownLatch`为例。构造方法`CountDownLatch(int count)`，初始化state为指定值count，每个业务线程在执行到指定位置时，调用`countDown()`方法释放资源，当`state`值置为`0`时，`await`线程被唤醒(unpark)。

# 源码解析

## acquire(int arg)

## release(int arg)

## acquireShared(int arg)

## releaseShared(int arg)

# 参考
http://www.cnblogs.com/waterystone/p/4920797.html