# 综述
[Centos下安装Zookeeper](http://www.jianshu.com/p/a79ea43c49bc)

[Zookeeper集群环境安装过程详解](http://blog.csdn.net/cruise_h/article/details/19046357)

# 下载（download）
可以到apache的官网找到[下载地址](http://www.apache.org/dyn/closer.cgi/zookeeper/)。    

命令行 `wget  http://mirror.bit.edu.cn/apache/zookeeper/stable/zookeeper-3.4.9.tar.gz` 下载zookeeper

# 安装

```shell
# 解压zk压缩包
tar -zxvf zookeeper-3.4.9.tar.gz
```

# 配置

> zookeeper支持两种运行模式：独立模式（standalone）和复制模式（replicated）。   


> 真正用于生产环境的zookeeper肯定都是使用 **复制模式** 的，这样做可以避免单点问题。想要使用 **复制模式**，但没有多余的机器能够使用，可以再单台机器上通过配置来使用 **复制模式**，从而模拟真实的集群环境。

> 由于zookeeper集群是通过多数选举的方式来产生leader的，因此，集群需要奇数个zookeeper实例组成，也就是至少需要3台（单台不能算做集群）。

## 配置 conf/zoo.conf 文件

```shell
# The number of milliseconds of each tick
tickTime=2000
# The number of ticks that the initial
# synchronization phase can take
initLimit=10
# The number of ticks that can pass between
# sending a request and getting an acknowledgement
syncLimit=5

# the directory where the snapshot is stored.
# do not use /tmp for storage, /tmp here is just
# example sakes.
# 指定实例数据的存放路径，不同的实例要区分开，设置实际的路径
dataDir=dataDir=/var/zk-data/zk-01

# the port at which the clients will connect
# 客户端连接本实例的端口号，默认是2181
# 单机中的不同实例也要区分开，比如2881，2182，2183
clientPort=2181

# servers
# server实例配置，默认端口为 2888:3888
# 这里是单机模拟集群，所以配置三个实例，但是端口不能相同
# 格式为 server.{x}={host}:{port1}:{port2},
# {x}中可以取数字，用来标识集群中唯一的一个实例。配置了多少个server.{x}就
# 表示集群中有多少个实例。{host}为实例所在的主机IP，
# {port1}是集群中实例之间用于数据通信的端口，
# {port2}是集群中实例进行leader选举中使用的通信端口。
# 同一实例的{port1}与{port2}是不可相同的。
# 单台机器部署多个实例的情况，各个端口号配置都要区分，不可相同。
server.1=127.0.0.1:2888:3888
server.2=127.0.0.1:2889:3889
server.3=127.0.0.1:2890:3890

# the maximum number of client connections.
# increase this if you need to handle more clients
#maxClientCnxns=60
#
# Be sure to read the maintenance section of the
# administrator guide before turning on autopurge.
#
# http://zookeeper.apache.org/doc/current/zookeeperAdmin.html#sc_maintenance
#
# The number of snapshots to retain in dataDir
#autopurge.snapRetainCount=3
# Purge task interval in hours
# Set to "0" to disable auto purge feature
#autopurge.purgeInterval=1

```

## 配置myid文件
zoo.cfg中的server.{x}中的{x}就是一个实例的myid，它需要被写在对应实例的{dataDir}/myid文件中。

所以，需要在每个实例的 zoo.cfg的配置文件中所指定的 dataDir 目录下创建一个名为`myid`的文件，文件的内容就是对应的`server.{x}`中的`x`。

比如在`/var/zk-data/zk-01/myid`的文件中写入 `1`:     
```shell
# 脚本语句
echo 1 > /var/zk-data/zk-01/myid
```

# 创建启动与停止集群脚本
> 对于多个实例，分别启动和停止比较麻烦（单台机器上启动多个zk实例的情况），可以写一个脚本来自动完成这个工作。

## 启动集群脚本
```
echo 'starting zk servers...'

echo `/opt/zookeeper-3.4.9-1/bin/zkServer.sh start`
echo `/opt/zookeeper-3.4.9-2/bin/zkServer.sh start`
echo `/opt/zookeeper-3.4.9-3/bin/zkServer.sh start`

echo 'start zk end'
```

## 停止集群脚本
```
#!/bin/bash

echo 'stoping zk servers...'

echo `/opt/zookeeper-3.4.9-1/bin/zkServer.sh stop`
echo `/opt/zookeeper-3.4.9-2/bin/zkServer.sh stop`
echo `/opt/zookeeper-3.4.9-3/bin/zkServer.sh stop`

echo 'stop zk end'
```

# 连接zk
```
/opt/zookeeper-3.4.9-1/bin/zkCli.sh -server {host}:2181
```
