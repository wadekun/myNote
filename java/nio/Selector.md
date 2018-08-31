# Selector（选择器）
选择器（Selector）管理着一个被注册的通道集合的信息和它们的就绪状态。通道是和选择器一起被注册的，并且使用选择器来更新通道的就绪状态。当这么做的时候，可以选择将被激发的线程挂起，直到有就绪的通道。

`Selector`的API：   
```java
public abstract class Selector
{
        public static Selector open( ) throws IOException
        public abstract boolean isOpen( );
        public abstract void close( ) throws IOException;
        public abstract SelectionProvider provider( );
        public abstract int select( ) throws IOException;
        public abstract int select (long timeout) throws IOException;
        public abstract int selectNow( ) throws IOException;
        public abstract void wakeup( );
        public abstract Set keys( );
        public abstract Set selectedKeys( );
}
```

# SelectableChannel（可选择通道）
该抽象类提供了实现通道可选择性所需要的公共方法。它是所有支持就绪检查的通道类的父类。FileChannel对象不是可选择的，因为它没有继承`SelectableChannel`抽象类。所有`Socket`通道都是可选择的，包括`Pipe`对象中获得的通道。  

`SelectableChannel`可以被注册到`Selector`对象上，同时可以指定对那个`Selector`而言，哪种操作是感兴趣的。一个通道可以被注册到多个选择器上，但在每个选择器上只能注册一次。


`SelectableChannel` API：    
```java
public abstract class SelectableChannel
    extends AbstractInterruptibleChannel
    implements Channel
{

    protected SelectableChannel() { }

    /**
     * Returns the provider that created this channel.
     *
     * @return  The provider that created this channel
     */
    public abstract SelectorProvider provider();

    /**
     * Returns an <a href="SelectionKey.html#opsets">operation set</a>
     * identifying this channel's supported operations.  The bits that are set
     * in this integer value denote exactly the operations that are valid for
     * this channel.  This method always returns the same value for a given
     * concrete channel class.
     *
     * @return  The valid-operation set
     */
    public abstract int validOps();

    public abstract boolean isRegistered();
    
    public abstract SelectionKey keyFor(Selector sel);
    //
    // sync(keySet) { return findKey(sel); }

    /**
     * Registers this channel with the given selector, returning a selection
     * key.
     *
     * @param  sel
     *         The selector with which this channel is to be registered
     *
     * @param  ops
     *         The interest set for the resulting key
     *
     * @param  att
     *         The attachment for the resulting key; may be <tt>null</tt>
     *  {@code set & ~validOps() != 0}
     *
     * @return  A key representing the registration of this channel with
     *          the given selector
     */
    public abstract SelectionKey register(Selector sel, int ops, Object att)
        throws ClosedChannelException;
    
    /**
     * Registers this channel with the given selector, returning a selection
     * key.
     *
     * <blockquote><tt>sc.{@link
     * #register(java.nio.channels.Selector,int,java.lang.Object)
     * register}(sel, ops, null)</tt></blockquote>
     *
     * @param  sel
     *         The selector with which this channel is to be registered
     *
     * @param  ops
     *         The interest set for the resulting key
     *
     * @return  A key representing the registration of this channel with
     *          the given selector
     */
    public final SelectionKey register(Selector sel, int ops)
        throws ClosedChannelException
    {
        return register(sel, ops, null);
    }

    public abstract SelectableChannel configureBlocking(boolean block)
        throws IOException;
    
    public abstract boolean isBlocking();

    /**
     * Retrieves the object upon which the {@link #configureBlocking
     * configureBlocking} and {@link #register register} methods synchronize.
     * This is often useful in the implementation of adaptors that require a
     * specific blocking mode to be maintained for a short period of time.
     *
     * @return  The blocking-mode lock object
     */
    public abstract Object blockingLock();

}
```

# SelectionKey（选择键）
SelectionKey封装了特定通道与特定选择器的注册关系。选择键对象被`SelectableChannel.register()`返回，并提供一个表示这种注册关系的标记。   
**选择键包含了两个比特集（以整数的形式进行编码），指示了该注册关系所关心的通道操作，以及通道已经准备好的操作。**   

**通道在被注册到一个Selector之前，必须先设置为非阻塞（configureBlocking(false)）模式。**

```java
public abstract class SelectionKey
{
        public static final int OP_READ
        public static final int OP_WRITE
        public static final int OP_CONNECT
        public static final int OP_ACCEPT
        public abstract SelectableChannel channel( );
        public abstract Selector selector( );
        public abstract void cancel( );
        public abstract boolean isValid( );
        public abstract int interestOps( );
        public abstract void interestOps (int ops);
        public abstract int readyOps( );
        public final boolean isReadable( )
        public final boolean isWritable( )
        public final boolean isConnectable( )
        public final boolean isAcceptable( )
        public final Object attach (Object ob)
        public final Object attachment( )
}
```

# 可选择通道与选择器关系
调用可选择通道的`register()`方法会将它注册到一个选择器上。如果视图注册一个阻塞状态的通道，`register()`将会抛出未检查异常`IllegalBlockingModeException`。同样，通道一旦被注册，则不能恢复到阻塞状态，如果试图这么做的话，将在调用`configuraBlocking()`方法时抛出`IllegalBlockingModeException`异常。      
在试图将一个已关闭的通道注册到选择器上时，将会抛出`ClosedChannelException`异常，就像方法原型所指示的那样。

建立监控三个通道的选择器：     
```java
Selector selector = Selector.open();

channel1.registor(selector, SelectionKey.OP_READ);
channel2.registor(selector, SelectionKey.OP_WRITE);
channel3.registor(selector, SelectionKey.OP_READ | SelectionKey.OP_WRITE);

// Wait up to 10 seconds for a channel to become ready
readyCount = selector.select(10000);  
```
这段代码创建了一个新的选择器，然后将这三个（已经存在）的`socket`通道注册到这个选择器上，而且感兴趣的操作各不相同。        
`Selector`的API细节：    
```java
public abstract class Selector
{
    // This is a partial API listing
    public static Selector open( ) throws IOException
    public abstract boolean isOpen( );
    public abstract void close( ) throws IOException;
    public abstract SelectionProvider provider( );
}
```
选择器是通过调用静态工厂方法`open()`来实例化的。选择器不是像通道或流那样的基本I/O对象：数据从来没有经过他们进行传输。类方法`open()`像`SPI`发出请求，通过默认的`SelectorProvider`对象获取一个新的实例。通过调用一个自定义的`SelectorProvider`对象的`openSelector`来创建一个`Selector`实例也是可行的。您可以通过调用`provider()`方法来决定由哪个`SelectorProvider`对象来创建给定的`Selector`实例。大多数情况下，我们不需要关注`SPI`，只需要调用`open()`方法来创建`Selector`对象。

下面来看看如何将通道注册到选择器上：   
```java
public abstract class SelectableChannel
           extends AbstractChannel
           implements Channel
{
    // This is a partial API listing
    public abstract SelectionKey register (Selector sel, int ops)
    throws ClosedChannelException;
    public abstract SelectionKey register (Selector sel, int ops,
    Object att)
    throws ClosedChannelException;
    public abstract boolean isRegistered( );
    public abstract SelectionKey keyFor (Selector sel);
    public abstract int validOps( );
}
```
选择键：    
```java
package java.nio.channels;
public abstract class SelectionKey
{
    public static final int OP_READ
    public static final int OP_WRITE
    public static final int OP_CONNECT
    public static final int OP_ACCEPT
    
    public abstract SelectableChannel channel( );
    public abstract Selector selector( );
    public abstract void cancel( );
    public abstract boolean isValid( );
    public abstract int interestOps( );
    public abstract void interestOps (int ops);
    public abstract int readyOps( );
    public final boolean isReadable( )
    public final boolean isWritable( )
    public final boolean isConnectable( )
    public final boolean isAcceptable( )
    public final Object attach (Object ob)
    public final Object attachment( )
}
```