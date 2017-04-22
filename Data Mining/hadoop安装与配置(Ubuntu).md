# 先决配置
在安装hadoop之前，需要做一些配置。

## 安装jdk
可以通过PPA来安装：https://tecadmin.net/install-oracle-java-8-ubuntu-via-ppa/

```bash
# 添加ppa源
$ sudo add-apt-repository ppa:webupd8team/java
# 更新
$ sudo apt-get update
# 安装 oracle java8
$ sudo apt-get install oracle-java8-installer

# 此时，可通过 java -version来验证
$ java -version

java version "1.8.0_121"
Java(TM) SE Runtime Environment (build 1.8.0_121-b13)
Java HotSpot(TM) 64-Bit Server VM (build 25.121-b13, mixed mode, sharing)

# 安装java8 的默认环境配置
$ sudo apt-get install oracle-java8-set-default

# 编辑  /etc/environment ，添加以下两行

JAVA_HOME=/usr/lib/jvm/java-8-oracle
JRE_HOME=/usr/lib/jvm/java-8-oracle/jre
```

## 创建 hadoop用户
```bash
# 创建 hadoop用户
$ sudo useradd -m hadoop -s /bin/bash

# 设置密码
$ sudo passwd hadoop

# 添加管理员权限
$ sudo adduser hadoop sudo
```

# 安装ssh，设置ssh无密码登录
> hadoop 的集群，单节点都需要 ssh进行远程登录。

```bash
# ubuntu 默认安装了 SSH client，还需要安装 SSH server
$ sudo apt-get install openssh-server

# 添加本机信任关系
$ cd ~/.ssh
$ ssh-keygen -t rsa  # 生成rsa公私钥
$ cat ./id_rsa.pub >> ./authorized_keys

# 此时  ssh localhost，不需要输入密码就可以登录了
$ ssh localhost
```

# 下载
http://hadoop.apache.org/releases.html
选择最新的稳定版，这里我选择的是2.7.3。

# 解压
tar -zxvf hadoop-2.7.3.tar.gz

# 单机配置（非分布式）
hadoop默认为单机模式，直接运行 $HADOOP_HOME/bin/hadoop 即可
```bash
# 运行 hadoop自带的example
$ cd $HADOOP_HOME
$ mkdir input  # 创建input文件夹            
$ cp ./etc/hadoop/*.xml ./input  # /etc/hadoop 下的xml配置文件拷贝到 input文件夹下

# 运行mapreduce-example grep 统计 符合正则的单词出现的次数，结果输出到output目录中
$ ./bin/hadoop jar ./share/hadoop/mapreduce/hadoop-mapreduce-examples-2.7.3.jar grep ./input ./output 'dfs[a-z.]+'   
```

# hadoop伪分布式

## 修改 $HADOOP_HOME/etc/hadoop/core-site.xml

**注意修改自己的hadoop路径，这这里路径是自定义的，与hadoop路径无关**

```xml
<configuration>
        <property>
                <name>fs.defaultFS</name>
                <value>hdfs://localhost:9000</value>
                <description>NameNode URI</description>
        </property>
        <property>
             <name>hadoop.tmp.dir</name>
             <value>file:/usr/local/hadoop/tmp</value>
             <description>Abase for other temporary directories.</description>
        </property>
</configuration>
```

## 修改配置文件 $HADOOP_HOME/etc/hadoop/hdfs-site.xml

**注意修改自己的hadoop路径，这这里路径是自定义的，与hadoop路径无关**

```xml
<configuration>
        <property>
                <name>dfs.replication</name>
                <value>1</value>
        </property>
        <property>
                <name>dfs.namenode.name.dir</name>
                <value>file:/home/hadoop/tmp/dfs/name</value>
        </property>
        <property>
                <name>dfs.datanode.data.dir</name>
                <value>file:/home/hadoop/tmp/dfs/data</value>
        </property>
</configuration>
```

## 下面是yarn相关配置

## mapred-site.xml
```xml
<configuration>
        <property>
                <name>mapreduce.framework.name</name>
                <value>yarn</value>
        </property>
</configuration>
```

## yarn-site.xml
```xml
<configuration>
        <property>
                <name>yarn.nodemanager.aux-services</name>
                <value>mapreduce_shuffle</value>
        </property>
</configuration>
```

## 格式化namenode
```bash
$ ./bin/hdfs namenode -format
```

## 开启 namenode和datanode守护进程
```bash
$ ./sbin/start-dfs.sh
```

## 启动yarn
```bash
$ ./sbin/start-yarn.sh
```

##
```bash
$ ./sbin/mr-jobhistory-daemon.sh start historyserver # 开启历史服务才能在WEB中查看任务运行
```

# 启动成功
yarn ui：http://node-ip:8088/cluster      
hdfs ui：http://node-ip:50070/       
