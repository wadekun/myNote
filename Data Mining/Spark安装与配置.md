# Spark安装与配置
Spark 是一个内存计算框架。包含spark core，spark sql， spark streaming， mllib等模块。

* spark core：spark核心部分，transformation、action 操作接口，以及内部实现
* spark sql：对spark core的封装，提供了内部自动优化的机制，减少了人为的优化。
* spark streaming：spark 流式操作
* mllib：机器学习库

# 下载spark
http://spark.apache.org/downloads.html
其中两种版本：without-hadoop与Pre build for hadoop***:    
* Pre build for hadoop***： 为了特定版本hadoop构建的
* without-hadoop: 不依赖特定版本hadoop，经过配置可在任意版本hadoop上运行

**注：Spark对hadoop的依赖体现在spark可以操作在hdfs上的数据，以及spark跑在2.0的yarn上。**

# 配置
https://spark.apache.org/docs/latest/hadoop-provided.html

## spark-env.conf

编辑 $SPARK_HOME/conf/spark-env.conf依照文档三种方式任意一种进行配置
```bash
# 就是上面文档中讲到的指定hadoop lib位置，因为spark需要依赖hadoop的jar访问hdfs
export SPARK_DIST_CLASSPATH=$(/home/hadoop/spark/hadoop-2.7.3/bin/hadoop classpath)
# hadoop配置文件的位置，这样spark才可以 以yarn的方式运行
export HADOOP_CONF_DIR=/home/hadoop/spark/hadoop-2.7.3/etc/hadoop
```

## spark-default.conf
编辑 $SPARK_HOME/conf/spark-default.conf   
```bash
spark.yarn.historyServer.address=master:8089
spark.history.ui.port=8089 spark.eventLog.enabled=true
# spark日志路径，默认是 /tmp/spark-events 目录下
# 现在配置到hdfs上，所以要在hdfs上创建改一下目录:
# $HADOOP_HOME/bin/hdfs dfs -mkdir -p /tmp/spark/events
spark.eventLog.dir=hdfs:///tmp/spark/events
spark.history.fs.logDirectory=hdfs:///tmp/spark/events
```

## 启动
```bash
# 本地模式启动
$ ./bin/spark-shell  --master local
# 在yarn上运行
$ ./bin/spark-shell --master yarn --deploy-mode client
```

spark historyserver ui：http://node-ip:8089
spark ui：http://node-ip:4040

## 启动遇到的问题

```
hadoop@ubuntu:~/spark$ ./spark/bin/spark-shell --master yarn --deploy-mode client
Setting default log level to "WARN".
To adjust logging level use sc.setLogLevel(newLevel). For SparkR, use setLogLevel(newLevel).
17/04/22 08:09:29 WARN util.NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable
17/04/22 08:09:31 WARN yarn.Client: Neither spark.yarn.jars nor spark.yarn.archive is set, falling back to uploading libraries under SPARK_HOME.
17/04/22 08:09:44 ERROR cluster.YarnClientSchedulerBackend: Yarn application has already exited with state FINISHED!
17/04/22 08:09:44 ERROR spark.SparkContext: Error initializing SparkContext.
java.lang.IllegalStateException: Spark context stopped while waiting for backend
	**
	at org.apache.spark.deploy.SparkSubmit.main(SparkSubmit.scala)
17/04/22 08:09:44 ERROR client.TransportClient: Failed to send RPC 7718993726494524736 to /10.211.55.9:47358: java.nio.channels.ClosedChannelException
java.nio.channels.ClosedChannelException
	at io.netty.channel.AbstractChannel$AbstractUnsafe.write(...)(Unknown Source)
17/04/22 08:09:44 ERROR cluster.YarnSchedulerBackend$YarnSchedulerEndpoint: Sending RequestExecutors(0,0,Map()) to AM was unsuccessful
java.io.IOException: Failed to send RPC 7718993726494524736 to /10.211.55.9:47358: java.nio.channels.ClosedChannelException
	**
```
**就是spark通过yarn将依赖的jar包分发到集群中时遇到的RPC问题。**
解决方法：http://stackoverflow.com/questions/38988941/running-yarn-with-spark-not-working-with-java-8    
即在yarn-site中添加：
```property
<property>
    <name>yarn.nodemanager.pmem-check-enabled</name>
    <value>false</value>
</property>

<property>
    <name>yarn.nodemanager.vmem-check-enabled</name>
    <value>false</value>
</property>
```
