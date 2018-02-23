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

```java
/**
     * Acquires in exclusive mode, ignoring interrupts.  Implemented
     * by invoking at least once {@link #tryAcquire},
     * returning on success.  Otherwise the thread is queued, possibly
     * repeatedly blocking and unblocking, invoking {@link
     * #tryAcquire} until success.  This method can be used
     * to implement method {@link Lock#lock}.
     *
     * @param arg the acquire argument.  This value is conveyed to
     *        {@link #tryAcquire} but is otherwise uninterpreted and
     *        can represent anything you like.
     */
    public final void acquire(int arg) {
        if (!tryAcquire(arg) &&
            acquireQueued(addWaiter(Node.EXCLUSIVE), arg))
            selfInterrupt();
    }
```

函数流程如下：
1. `tryAcquire()` 尝试获取资源，如果成功则返回。
2. `addWaiter(Node.EXCLUSIVE)` 将该线程加入等待队列的尾部，并标记为独占模式。并返回添加的节点。
3. `acquireQueued()` 使线程在队列中获取资源，一直获取到资源后再返回。如果整个等待过程中被中断过则返回`true`，否则返回`false`。
4. `selfInterrupt()` 如果线程在等待的过程中被中断过，它是不响应的。只有获取资源后再进行自我中断`selfInterrupt()`，将中断补上。

### tryAcquire(int)
```java
protected boolean tryAcquire(int arg) {
    throw new UnsupportedOperationException();
}
```
在模板方法`acquire`中，`tryAcquire`就是由子类去实现的操作（通过state的get/set/CAS）。至于能不能重入，能不能加塞，就看自定义的同步器怎么去设计了。

这里之所以设计成`protected`而没有设计成`abstract`，是因为独占模式下只需实现`tryAcquire-tryRelease`，共享模式下只需实现`tryAcquireShared-tryReleaseShared`。如果都设计成`abstract`的，那么每个自定义同步器都需要自己去实现一遍。所以，这也减少了不必要的工作量。

### addWaiter(Node)

该方法将当前线程加入等待队列的队尾，并返回当前线程所在的节点。

```java
/**
    * Creates and enqueues node for current thread and given mode.
    *
    * @param mode Node.EXCLUSIVE for exclusive, Node.SHARED for shared
    * @return the new node
    */
private Node addWaiter(Node mode) {
    // 以给定模式创建节点，mode有两种：EXCLUSIVE（独占），SHARED（共享）
    Node node = new Node(Thread.currentThread(), mode);

    // Try the fast path of enq; backup to full enq on failure
    Node pred = tail;
    if (pred != null) {
        node.prev = pred;
        if (compareAndSetTail(pred, node)) { // 通过cas操作，快速入队至队尾
            pred.next = node;
            return node;
        }
    }
    enq(node); // 如果快速入队失败，则调用enq方法入队
    return node;
}
```

#### enq(Node)

```java
/**
* Inserts node into queue, initializing if necessary. See picture above.
* @param node the node to insert
* @return node's predecessor
*/
private Node enq(final Node node) {
    for (;;) {
        Node t = tail;
        if (t == null) { // Must initialize （如果队列为空，则初始化一个头节点，尾指针也指向它）
            if (compareAndSetHead(new Node()))
                tail = head;
        } else { // 走入队流程，当前节点将前驱指向尾节点，并cas操作将当前节点置为尾节点（尾节点指向当前节点）
            node.prev = t;
            if (compareAndSetTail(t, node)) {
                t.next = node;
                return t;
            }
        }
    }
}
```

### acquireQueued()

经过`tryAcquire`和`addWaiter`当前线程已经获取锁（资源）失败进入等待队列中了。接着就是进入等待状态休息，直到其他线程彻底释放资源后唤醒自己，自己再拿到资源，然后就可以开始自己的表演了（这个过程是不可中断的）。

```java
/**
* Acquires in exclusive uninterruptible mode for thread already in
* queue. Used by condition wait methods as well as acquire.
*
* @param node the node
* @param arg the acquire argument
* @return {@code true} if interrupted while waiting
*/
final boolean acquireQueued(final Node node, int arg) {
    boolean failed = true; // 标记是否成功拿到资源
    try {
        boolean interrupted = false; // 中断标记
        for (;;) {
            final Node p = node.predecessor(); // 前驱节点

            // 如果前驱节点是头节点，那么再次尝试获取资源
            // 进行到这一步，可能是初次入队，也可能是前驱节点释放完资源唤醒自己，也可能是被interrupt了
            if (p == head && tryAcquire(arg)) { 
                setHead(node); // 如果获取成功，表名前驱节点已经执行完毕彻底释放资源，将当前节点置为头节点
                p.next = null; // help GC
                failed = false;
                return interrupted; // 返回等待过程中是否被中断过
            }

            // shouldParkAfterFailedAcquire 检查当前线程是否应该休息
            // parkAndCheckInterrupt 当前线程休眠并检查中断状态
            if (shouldParkAfterFailedAcquire(p, node) &&
                parkAndCheckInterrupt())
                interrupted = true; // 如果当前线程曾被中断，则设置中断标记为true
        }
    } finally {
        if (failed)
            cancelAcquire(node);
    }
}
```

#### shouldParkAfterFailedAcquire(Node, Node)

```java
/**
* Checks and updates status for a node that failed to acquire.
* Returns true if thread should block. This is the main signal
* control in all acquire loops.  Requires that pred == node.prev.
*
* @param pred node's predecessor holding status
* @param node the node
* @return {@code true} if thread should block
*/          
private static boolean shouldParkAfterFailedAcquire(Node pred, Node node) {
    int ws = pred.waitStatus;  // 前驱节点的状态
    if (ws == Node.SIGNAL) // 如果状态为SIGNAL(-1)，表名前驱获取到资源后会通知(unpark)自己，则可以安心休息，直接返回true
        /*
            * This node has already set status asking a release
            * to signal it, so it can safely park.
            */
        return true;
    if (ws > 0) { 
        // 如果状态大于0，则表名前驱已经放弃(CANCEL)，一直往前找，找到最近的一个未放弃的节点，排在它后面
        // 中间跳过的节点将被回收掉(GC)
        /*
            * Predecessor was cancelled. Skip over predecessors and
            * indicate retry.
            */
        do {
            node.prev = pred = pred.prev;
        } while (pred.waitStatus > 0);
        pred.next = node;
    } else { // 状态为0(未设置过等待状态)或-2时，将状态设置为SIGNAL。即 拿到资源后通知下自己
        /*
            * waitStatus must be 0 or PROPAGATE.  Indicate that we
            * need a signal, but don't park yet.  Caller will need to
            * retry to make sure it cannot acquire before parking.
            */
        compareAndSetWaitStatus(pred, ws, Node.SIGNAL);
    }
    return false;
}
```
整个流程中，如果前驱不为SIGNAL，则需要跳过那些状态值大于0(CANCEL)的节点，链到状态值小于0的节点后，并将新的前驱状态值设置为SIGNAL。
总之就是保证前驱的状态为SIGNAL，才能放心的去休息。

#### parkAndCheckInterrupt()
```java
/**
* Convenience method to park and then check if interrupted
*
* @return {@code true} if interrupted
*/
private final boolean parkAndCheckInterrupt() {
    LockSupport.park(this); // 调用 park() 使线程进入waiting状态
    return Thread.interrupted(); // 如果被唤醒，则检查自己是否被中断过
}
```

`park()`会让线程进入`waiting`状态，这个状态下的线程有两种途径可以唤醒：1) 被unpark()，2) 被interrupt()。
Thread.interrupted()会检查当前的终端状态，并将中断状态清除。

## release(int arg)

## acquireShared(int arg)

## releaseShared(int arg)

# 参考
http://www.cnblogs.com/waterystone/p/4920797.html