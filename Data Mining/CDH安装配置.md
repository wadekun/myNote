# 离线安装CDH
Cloudera官方给了三种安装CDH的方式：
Path A: 通过Cloudera Manager 自动安装，需要所有节点联网。
Path B：使用系统包管理工具安装，需要从官网RPMS目录下下载许多RPM文件。
Path C：利用tar包安装。

本次安装均采用离线方式。

# 环境
| 软件名称 | 版本       |
| -------- | ---------- |
| 操作系统 | Centos 7.4 |
| JDK      | 8U171      |
| Mysql    | 5.7.22     |
| CDH      | 5.14.2

节点：  
10.211.55.12  
10.211.55.13  
10.211.55.14  

# 下载CDH所需安装包
Cloudera Manager:  http://archive.cloudera.com/cm5/cm/5/      
CDH: http://archive.cloudera.com/cdh5/parcels/5.14.2/    

# 配置域名解析
```bash
vi /etc/hosts
```

添加一下三行内容(每个节点都要配置，本机也要写进去)：
```bash
10.211.55.12 cdh1
10.211.55.13 cdh2
10.211.55.14 cdh3
```

# 设置免密码登录（信任关系）
配置节点两两之间的信任关系。
```bash

## 在 cdh1上执行
# 生成无密码的密钥对
ssh-keygen -t rsa  

# 将公钥拷贝到认证文件中
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys

# 拷贝至节点2
scp ~/.ssh/authorized_keys cdh2:/root/.ssh/

## cdh2上执行
# 生成无密码的密钥对
ssh-keygen -t rsa  

# 将公钥拷贝到认证文件中
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys

# 拷贝到节点3
scp ~/.ssh/authorized_keys cdh3:/root/.ssh/

## cdh3上执行
# 生成无密码的密钥对
ssh-keygen -t rsa  

# 将公钥拷贝到认证文件中（此时，认证文件中已经包含了节点一至节点三的公钥）
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys

# 分别拷贝认证文件至其他两个节点
scp ~/.ssh/authorized_keys cdh1:/root/.ssh/
scp ~/.ssh/authorized_keys cdh2:/root/.ssh/
```
此时，在cdh1上直接执行`ssh cdh2`可无密码直接登入。

# 安装jdk（每个节点）
运行CDH需要Oracle的JDK，CDH5.3之后开始支持jdk1.8.这里安装Oracle jdk1.8.注意，各个节点安装jdk版本要相同。

首先需要卸载，linux自带的openjdk。
```bash
> rpm -qa | grep java
python-javapackages-3.4.1-11.el7.noarch
java-1.7.0-openjdk-1.7.0.141-2.6.10.5.el7.x86_64
tzdata-java-2017b-1.el7.noarch
javapackages-tools-3.4.1-11.el7.noarch
java-1.7.0-openjdk-headless-1.7.0.141-2.6.10.5.el7.x86_64

# 针对以上五个包（依次卸载）
> rpm -e --nodeps 包名
```

从官网下载jdk-8u171-linux-x64.tar.gz文件，拷贝至/opt/目录下。
```bash
mkdir /usr/java
mv /opt/jdk-8u171-linux-x64.tar.gz /usr/java/
cd /usr/java/
tar -zxvf jdk-8u171-linux-x64.tar.gz

## 设置环境变量
vim /etc/profile.d/java.sh

# 配置 JAVA_HOME、CLASSPATH、PATH
export JAVA_HOME=/usr/java/jdk1.8.0_171
export CLASSPATH=.:$JAVA_HOME/jre/lib/*:$JAVA_HOME/lib/*
export PATH=$PATH:$JAVA_HOME/bin

# 使环境变量生效
source /etc/profile.d/java.sh
```

# 安装配置NTP服务
集群中所有主机必须保持时间同步，如果时间相差较大会引起各种问题。 具体思路如下：     
master节点作为ntp服务器与外界对时中心同步时间，随后对所有datanode节点提供时间同步服务。
所有datanode节点以master节点为基础同步时间。

```bash
# 安装ntp(每个节点)
yum instal ntp

# 配置主节点（这里选cdh1）ntp配置文件
vim /etc/ntp.conf
# 添加对时服务器，保存退出
server 202.112.29.82 prefer

# 先在主节点上同步一次时间
ntpdate 202.112.29.82

# 启动主节点ntp服务
systemctl enable ntpd.service  # enable，开机自启
systemctl start ntpd.service # 立即启动ntpd 服务

# 配置子节点
vim /etc/ntp.conf
# 添加对时服务器，设置为cdh1，保存并退出
server cdh1 prefer

# 启动子节点ntp服务
systemctl enable ntpd.service  # enable，开机自启
systemctl start ntpd.service # 立即启动ntpd 服务
```

# 安装mysql
下载安装包 
https://dev.mysql.com/get/Downloads/MySQL-5.7/mysql-5.7.22-1.el7.x86_64.rpm-bundle.tar  
加压。
`yum install mysql-community-{server,client,common,libs}-*` 安装。
**注：解压tar包后，安装之前，删除server-minimal包**

https://zhuanlan.zhihu.com/p/34719781

## 修改root密码
```bash
systemctl stop mysqld

# 编辑 mysql配置文件设置无需密码登录
vim /etc/my.cnf

# Disabling symbolic-links is recommended to prevent assorted security risks
skip-grant-tables     #添加这句话，这时候登入mysql就不需要密码
symbolic-links=0

# systemctl start mysqld

# 直接 mysql -uroot -p 登录mysql
# 修改root密码
mysql> set password for root@localhost = password('123456');
ERROR 1290 (HY000): The MySQL server is running with the --skip-grant-tables option so it cannot execute this statement
mysql> flush privileges;  #更新权限
Query OK, 0 rows affected (0.00 sec)
mysql> set password for root@localhost = password('123456'); or update user set authentication_string=PASSWORD("123456") where user="root";
Query OK, 0 rows affected, 1 warning (0.00 sec)
mysql>flush privileges; #更新权限
mysql>quit; #退出  

# 去掉my.cnf中skip-grant-table设置并重启mysql服务

```
# 安装Cloudera Manager Service
将`cloudera-manager-el6-cm5.14.3_x86_64.tar.gz`包拷至`/opt`目录下，并解压。得到`cm-5.14.3`文件夹。

## 建立cloudera-scm用户
```bash
>useradd --system --home=/opt/cm-5.14.3/run/cloudera-scm-server --no-create-home --shell=/bin/false --comment "Cloudera SCM User" cloudera-scm

>echo USER=\"cloudera-scm\" >> /etc/default/cloudera-scm-agent

#>echo "Detaults secure_path = /sbin:/bin:/user/sbin:/user/bin" >> /etc/sudoers
```

## 建立 Cloudera Manager 元数据库
1. 首先下载mysql驱动包`mysql-connector-java-5.1.46-bin.jar`至`/opt/cm-5.14.3/share/cmf/lib/`目录下。

2. 在主节点初始化CM数据库：   
```bash
# 创建cm数据库
/opt/cm-5.14.3/share/cmf/schema/scm_prepare_database.sh mysql cm -hlocalhost -uroot -p**** --scm-host localhost scm scm scm
```

`Access denied for user 'root'@'%' to database 'cm'` :    
```sql
mysql> SELECT `User`, `Grant_priv` FROM `mysql`.`user` WHERE `User` = 'root';
-- You will probably notice it returns a 'N' for Grant_priv. So do this:

mysql> UPDATE `mysql`.`user` SET `Grant_priv` = 'Y' WHERE `User` = 'root';
mysql> FLUSH PRIVILEGES;
mysql> SELECT `User`, `Grant_priv` FROM `mysql`.`user`;
```

如遇到` Access denied for user 'scm'@'59net' (using password: YES)` 错误，需要向 `scm`用户授权。cm在用mysql`root`用户登录后会创建`scm`用户，来访问创建的`cm`库。
```sql
grant all privileges on cm.* to 'scm'@'%' identified by 'scm';
```


密码问题：   https://www.jianshu.com/p/5779aa264840

# 配置Agent
```bash
# 修改 /opt/cm-5.14.3/etc/cloudera-scm-agent/config.ini 中的server_host，改为cdh1
server_host=cdh1
``` 

复制Agent到其他节点：
```bash
scp -r /opt/cm-5.14.3/ cdh2:/opt/
scp -r /opt/cm-5.14.3/ cdh3:/opt/
```
# CDH 安装准备
其他子节点创建cloudera-scm用户：
```bash
>useradd --system --home=/opt/cm-5.14.3/run/cloudera-scm-server --no-create-home --shell=/bin/false --comment "Cloudera SCM User" cloudera-scm

>echo USER=\"cloudera-scm\" >> /etc/default/cloudera-scm-agent

#>echo "Detaults secure_path = /sbin:/bin:/user/sbin:/user/bin" >> /etc/sudoers
```

# 准备Parcels
1. 将Parcels相关三个文件复制到主节点`/opt/cloudera/parcel-repo`目录下：
```bash
mv /opt/CDH/CDH-5.14.2-1.cdh5.14.2.p0.3-el7.parcel /opt/cloudera/parcel-repo/
mv /opt/CDH/CDH-5.14.2-1.cdh5.14.2.p0.3-el7.parcel.sha1 /opt/cloudera/parcel-repo/
mv /opt/CDH/manifest.json /opt/cloudera/parcel-repo/
```
2. 将CDH-5.14.2-1.cdh5.14.2.p0.3-el7.parcel.sha1，重命名为CDH-5.14.2-1.cdh5.14.2.p0.3-el7.parcel.sha，这点必须注意，否则，系统会重新下载CDH-5.1.3-1.cdh5.1.3.p0.12-el6.parcel文件。

```bash
cd /opt/cloudera/parcel-repo/
mv CDH-5.14.2-1.cdh5.14.2.p0.3-el7.parcel.sha1 CDH-5.14.2-1.cdh5.14.2.p0.3-el7.parcel.sha
```

3. 修改相关文件夹属主：
```bash
chown -R cloudera-scm:cloudera-scm /opt/cm-5.14.3/
chown -R cloudera-scm:cloudera-scm /opt/cloudera/
```

4. 每个主机上建立`/opt/cloudera/parcels`目录，并修改属主
```bash
mkdir -p /opt/cloudera/parcels
chown -R cloudera-scm:cloudera-scm /opt/cloudera/parcels
``` 

# 在cdh1上启动cm server
```bash
/opt/cm-5.14.3/etc/init.d/cloudera-scm-server start 

/opt/cm-5.14.3/etc/init.d/cloudera-scm-agent start # 这里启动失败
## 查看/opt/cm-5.14.3/log/cloudera-scm-agent/cloudera-scm-agent.out ，/usr/bin/env: python2.6: 没有那个文件或目录
## 原来是我的 cm版本有问题，centos7，这里下了el6的版本。。。重新下载 cloudera-manager-centos7-cm5.14.3_x86_64.tar.gz。。。。
```

参考：   http://blog.51cto.com/ciscolang/1543810

# 在所有节点上启动cm agent
```bash
/opt/cm-5.14.3/etc/init.d/cloudera-scm-agent start
```

# 登录Cloudera Manager控制台，安装配置CDH
`http://cdh1:7180`    
默认的用户名密码都是`admin`。


# 为即将安装的服务建立元数据库
```bash
mysql -u root -p -e "create database hive DEFAULT CHARACTER SET utf8; create database rman DEFAULT CHARACTER SET utf8; create database oozie DEFAULT CHARACTER SET utf8; create database hue DEFAULT CHARACTER SET utf8;grant all on *.* TO 'root'@'%' IDENTIFIED BY 'Q1@r';"
```

# 开机自启

```bash
# server
cp /opt/cm-5.14.3/etc/init.d/cloudera-scm-server /etc/init.d/
chkconfig --add cloudera-scm-server
chkconfig cloudera-scm-server on

## 修改 server配置
vim /etc/init.d/cloudera-scm-server
#### 添加 JAVA_HOME配置
export JAVA_HOME=/usr/java/jdk1.8.0_172
#### 修改CM安装目录
将 CMF_DEFAULTS=${CMF_DEFAULTS:-/etc/default} 修改为：CMF_DEFAULTS=${CMF_DEFAULTS:-/opt/cm-5.14.3/etc/default}

# agent
cp /opt/cm-5.14.3/etc/init.d/cloudera-scm-agent /etc/init.d/
chkconfig --add cloudera-scm-agent
chkconfig cloudera-scm-agent on
```

# ISSUES

## cloudera manager 无法发出查询：未能连接到 Host Monitor
在安装CM集群时，由于虚拟机磁盘问题，中断了，后来重新安装，节点状态报错：无法发出查询：未能连接到 Host Monitor。
查看 cloudera-scm-agent.log：
```
Error, CM server guid updated, expected 85587073-270d-43d9-a44a-e213d9f7e45b, received 4c1402a5-8364-4598-a382-0c760710e897
```

再出问题的节点删除 `/opt/cm-5.14.3/lib/cloudera-scm-agent/cm_guid`，重启`cloudera-scm-agent`即可。

## cloudera 主机配置
* master 内存 >= 4GB
* slave  内存 >= 2GB

## Permission denied: user=mapred, access=WRITE, inode="/":hdfs:supergroup:drwxr-xr-x
错误日志：  
```
Service org.apache.hadoop.mapreduce.v2.hs.HistoryFileManager failed in state INITED; cause: org.apache.hadoop.yarn.exceptions.YarnRuntimeException: Error creating done directory: [hdfs://cdh1:8020/user/history/done]
org.apache.hadoop.yarn.exceptions.YarnRuntimeException: Error creating done directory: [hdfs://cdh1:8020/user/history/done]
	...
Caused by: org.apache.hadoop.security.AccessControlException: Permission denied: user=mapred, access=WRITE, inode="/":hdfs:supergroup:drwxr-xr-x
	...
Caused by: org.apache.hadoop.ipc.RemoteException(org.apache.hadoop.security.AccessControlException): Permission denied: user=mapred, access=WRITE, inode="/":hdfs:supergroup:drwxr-xr-x
	...
...
JobHistoryServer metrics system shutdown complete.
上午10点44:05.354分	FATAL	JobHistoryServer	
```

```bash
# 第一步：

sudo -u hdfs hdfs dfs -chmod 775 /

# 第二步：

sudo -u hdfs hdfs dfs -mkdir /user

sudo -u hdfs hdfs dfs -chown mapred:mapred /user

sudo -u hdfs hdfs dfs -mkdir /tmp

sudo -u hdfs hdfs dfs -chown mapred:mapred /tmp
```

http://www.cnblogs.com/split/articles/4583412.html

## Hive报错
```
Caused by: org.datanucleus.exceptions.NucleusException: Attempt to invoke the "BONECP" plugin to create a ConnectionPool gave an error : The specified datastore driver ("com.mysql.jdbc.Driver") was not found in the CLASSPATH. Please check your CLASSPATH specification, and the name of the driver.
	...
Caused by: org.datanucleus.store.rdbms.connectionpool.DatastoreDriverNotFoundException: The specified datastore driver ("com.mysql.jdbc.Driver") was not found in the CLASSPATH. Please check your CLASSPATH specification, and the name of the driver.
	...
```

这里安装Hive的时候可能会报错，因为我们使用了MySql作为hive的元数据存储，hive默认没有带mysql的驱动，通过以下命令拷贝一个就行了：
```bash
cp /opt/CDH/mysql-connector-java-5.1.46/mysql-connector-java-5.1.46-bin.jar  /opt/cloudera/parcels/CDH-5.14.2-1.cdh5.14.2.p0.3/lib/hive/lib/
```


## Hive 启动报错
https://stackoverflow.com/questions/42209875/hive-2-1-1-metaexceptionmessageversion-information-not-found-in-metastore

## Hue 测试连接数据库报错
```
django.core.exceptions.ImproperlyConfigured: Error loading MySQLdb module: libmysqlclient_r.so.16: cannot open shared object file: No such file or directory
```

安装节点缺少`libmysqlclient_r.so.16`文件。从别的服务器上拷贝至`/usr/lib64/`下，执行`ldconfig`即可。

## 初始化oozie库表 java.lang.classnotfoundexception com.mysql.jdbc.driver
原来以为像`hive`一样放到``


## Hue load balancer启动失败，并且日志文件不存在
需要提前安装环境
httpd
mod_ssl
利用yum install 安装上面的包 即可启动

https://ask.csdn.net/questions/671624

## spark-shell 权限问题
启动`spark-shell`报错：   
```
org.apache.hadoop.security.AccessControlException: Permission denied: user=root, access=WRITE, inode="/user":hdfs:supergroup:drwxr-xr-x
	...
```

https://github.com/sequenceiq/docker-spark/issues/30    

在spark节点上执行：    
```
export HADOOP_USER_NAME=hdfs
```