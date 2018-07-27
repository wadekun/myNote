# Scatter-Gather I/O简介
Scatter-Gather IO是一种高性能的IO标准技术，是一种DMA（direct memory access）传输方式。对于一个数据块，在内存中可能存在于一些离散的缓冲区，换言之，就是一些离散的内存缓冲区一起保存一个数据块。如果没有scatter/gather技术，那么当我们要建立一个从内存到磁盘的传输，需要为每个buffer做一个传输，或者把这些离散的buffer中的数据转移到一个大的buffer中，然后统一传输到磁盘上。毫无疑问，这两种方式效率都不是很高。

如果能把这些离散缓冲区中的数据收集起来（gather up）并转移到目标位置是一个单一的操作的话，效率一定会更高。反之，磁盘向内存中的传输，如果把磁盘中的整块数据，能够分散（Scatter）到内存中适当的位置是一个单一的操作，而不需要移动中间的块或者其他操作，那么显然，效率应该会更高。

Java NIO内置了对Scatter/Gather的支持。   

# Scatter
Scattering read指的是从一个通道中读取数据分散（scatter）到多个buffer中。   
![Scatter](imgs/scatter.png)    

 
```java
RandomAccessFile raf = new RandomAccessFile("nio-data.txt", "rw");
FileChannel channel = raf.getChannel();

ByteBuffer header = ByteBuffer.allocate(512);
ByteBuffer body = ByteBuffer.allocate(512);

ByteBuffer[] bufferArray = {header, body};

channel.read(bufferArray);
```

# Gather
Gathering write指的是把多个buffer中的数据写入一个channel中。  
![Gathering write](imgs/gather.png)   


```java
RandomAccessFile raf = new RandomAccessFile("nio-data.txt", "rw");
FileChannel channel = raf.getChannel();

ByteBuffer header = ByteBuffer.allocate(512);
ByteBuffer body = ByteBuffer.allocate(512);
// TODO write data to header and body, and flip themes   

ByteBuffer[] bufferArray = {header, body};

channel.write(bufferArray);
```
