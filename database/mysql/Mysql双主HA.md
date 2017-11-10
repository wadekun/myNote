# 复制原理(基于binlog方式)
1. Master将数据改变记录到二进制文件(binary log)中，也就是`log-bin`参数指定的文件，这些记录又叫做二进制日志事件(binary log events)。    
2. Slave通过I/O线程连接Master，读取Master中的`binary log events`，并写入自己的中继日志(relay log)。
3. Slave重做中继日志中的事件，把中继日志中的事件信息一条一条的在本地执行，完成数据在本地的存储，从而实现将改变反映到自己的数据（数据重放）。

# 步骤

## 1. 安装相同版本mysql
数据一致化，导入导出数据    
```sql
-- 显示创建数据库语句，在Salve上新建数据库
mysql> show create database database_name

-- Master导出数据库文件
mysql> mysqldump -u用户名 -p 数据库名 >> {dir}/数据库名__日期.sql

-- Salve 导入数据
mysql> source {dir}/数据库名__日期.sql
```

## 2.  配置
```shell

### server 1
log-bin=bin # 开启binlog
relay-log=relay-bin # 开启 relay log
server-id=1 # server id 必须唯一
skip-slave-start=1  # 为了数据一致性
auto_increment_offset=1   # 自增字段偏移量
auto_increment_increment=2  # 是自增字段增加的幅度
# log_slave_updates = 1  # 如果你要给这两个实例再加 slave，那么你就需要配置 log_slave_updates 参数

### server 2
log-bin=bin
relay-log=relay-bin
server-id=2
skip-slave-start=1
auto_increment_offset=2
auto_increment_increment=2
# log_slave_updates = 1
```

执行mysql命令，设置slave用户，用于slave读取日志:           
```sql

---- 分别在server1，server2创建 replication用户
mysql> CREATE USER 'replication'@'%' IDENTIFIED BY '123456';

---- 在server1上执行
---- mysql> GRANT REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'replication'@'192.168.1.52' IDENTIFIED BY PASSWORD '123456';
mysql> GRANT REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'replication'@'192.168.1.52';


---- 在server2上执行
----mysql> GRANT REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'replication'@'192.168.1.51' IDENTIFIED BY PASSWORD '123456';
mysql> GRANT REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'replication'@'192.168.1.51';

```

分别查看server1，server2上的master信息，记录下`File`与`Position`字段，用与slave设置master信息。
```sql
mysql> show master status：   
+------------+----------+--------------+------------------+-------------------+
| File       | Position | Binlog_Do_DB | Binlog_Ignore_DB | Executed_Gtid_Set |
+------------+----------+--------------+------------------+-------------------+
| bin.000002 |      154 | logdb        |                  |                   |
+------------+----------+--------------+------------------+-------------------+
1 row in set (0.00 sec)

```

slave设置master信息，并启动slave任务，：      
```sql

---- master_log_file对应上面的File字段，master_log_pos对应Position字段
---- server1
msyql> change master to master_host='192.168.1.52', master_user='replication', master_password='123456', master_port=3306, master_log_file='bin.000002', master_log_pos=10, master_connect_retry=30;

---- server2
msyql> change master to master_host='192.168.1.51', master_user='replication', master_password='123456', master_port=3306, master_log_file='bin.000002', master_log_pos=10, master_connect_retry=30;

---- 在 server1 上执行：
mysql> start slave;

---- 在 server1 上执行：
mysql> start slave;
```

#### issues
1. `The server is not configured as slave; fix in config file or with CHANGE MASTER TO`
查看 `/etc/my.cnf`,看是否正确配置了`server-id`以及slave信息，注意应该配置在`[mysql]` section下。

2.


# keepalived HA
> keepalived是集群管理中保证集群高可用的一个软件解决方案，其功能类似于heartbeat，用来防止单点故障
> keepalived是以VRRP协议为实现基础的，VRRP全称Virtual Router Redundancy Protocol，即虚拟路由冗余协议。
> 虚拟路由冗余协议，可以认为是实现路由器高可用的协议，即将N台提供相同功能的路由器组成一个路由器组，这个组里面有一个master和多个backup，master上面有一个对外提供服务的vip，master会发组播（组播地址为224.0.0.18），当backup收不到vrrp包时就认为master宕掉了，这时就需要根据VRRP的优先级来选举一个backup当master。这样的话就可以保证路由器的高可用了。
> keepalived主要有三个模块，分别是core、check和vrrp。core模块为keepalived的核心，负责主进程的启动、维护以及全局配置文件的加载和解析。check负责健康检查，包括常见的各种检查方式。vrrp模块是来实现VRRP协议的。

## 安装

### pre 安装openssl(先测试下有没有安装，先安装keepalived，如果提示openssl未安装再来执行这一步)
http://blog.csdn.net/gsying1474/article/details/48396205
```bash

##前提：基于redhat 6.5或者CentOS 6.5
##软件包（由yum缓存中提取的）：
##http://pan.baidu.com/s/1dDHIEGD

rpm -e --nodeps keyutils-libs-1.4-4.el6.x86_64
rpm -ivh keyutils-libs-1.4-5.el6.x86_64.rpm
rpm -ivh keyutils-libs-devel-1.4-5.el6.x86_64.rpm
rpm -ivh libsepol-devel-2.0.41-4.el6.x86_64.rpm
## rpm -e --nodeps libselinux-2.0.94-5.3.el6_4.1.x86_64        # 删除以后就再也装不上了，所以切勿执行。。。。，恢复，取消此操作，继续测试

rpm -e --nodeps libselinux-utils-2.0.94-5.3.el6_4.1.x86_64

#安装成功，由此绕过之前5步出错的bug，可能需要先卸载 libselinux-python-2.0.94-5.3.el6_4.1.x86_64包
rpm -Uvh libselinux-2.0.94-5.8.el6.x86_64.rpm   
rpm -ivh libselinux-devel-2.0.94-5.8.el6.x86_64.rpm
rpm -e --nodeps krb5-libs-1.10.3-10.el6_4.6.x86_64
rpm -ivh krb5-libs-1.10.3-42.el6.x86_64.rpm
rpm -e --nodeps libcom_err-1.41.12-18.el6.x86_64
rpm -ivh libcom_err-1.41.12-22.el6.x86_64.rpm
rpm -ivh libcom_err-devel-1.41.12-22.el6.x86_64.rpm
rpm -ivh krb5-devel-1.10.3-42.el6.x86_64.rpm
rpm -ivh zlib-devel-1.2.3-29.el6.x86_64.rpm
rpm -e --nodeps openssl-1.0.1e-15.el6.x86_64
rpm -ivh openssl-1.0.1e-42.el6.x86_64.rpm
rpm -ivh openssl-devel-1.0.1e-42.el6.x86_64.rpm

```
### 安装ipvsadm
不装这个会提示：`IPVS: Protocol not available`，keepalived不会挂掉，其他backup节点不会转为master。
```bash
### 先装 popt，不然ipvsadm编译不通过
rpm -ivh libnl-devel-1.1.4-2.el6.x86_64.rpm
rpm -ivh popt-devel-1.13-7.el6.x86_64.rpm
rpm -ivh popt-static-1.13-7.el6.x86_64.rpm

### 安装ipvsadm
tar -zxvf ipvsadm-1.26.tar.gz
cd ipvsadm-1.26
make && make install

### 此时运行 ipvsadm 命令测试是否安装成功
ipvsadm

```

### 安装keepalived
1. 解压
2. 到keepalived目录内：   

  ```bash
  sh ./configure --prefix=/usr/local/keepalived --with-kernel-dir=/usr/src/kernels/`uname -r` && make && make install
  ```
3. 修改配置
```bash
cp /usr/local/keepalived/etc/sysconfig/keepalived /etc/sysconfig/
mkdir /etc/keepalived
ln -s /usr/local/keepalived/sbin/keepalived /usr/sbin/
touch /etc/init.d/keepalived
chmod +x /etc/init.d/keepalived
vi /etc/init.d/keepalived
```

keepalived脚本：
```bash
#!/bin/sh
#
# keepalived   High Availability monitor built upon LVS and VRRP
#
# chkconfig:   - 86 14
# description: Robust keepalive facility to the Linux Virtual Server project \
#              with multilayer TCP/IP stack checks.

### BEGIN INIT INFO
# Provides: keepalived
# Required-Start: $local_fs $network $named $syslog
# Required-Stop: $local_fs $network $named $syslog
# Should-Start: smtpdaemon httpd
# Should-Stop: smtpdaemon httpd
# Default-Start:
# Default-Stop: 0 1 2 3 4 5 6
# Short-Description: High Availability monitor built upon LVS and VRRP
# Description:       Robust keepalive facility to the Linux Virtual Server
#                    project with multilayer TCP/IP stack checks.
### END INIT INFO

# Source function library.
. /etc/rc.d/init.d/functions

exec="/usr/sbin/keepalived"
prog="keepalived"
config="/etc/keepalived/keepalived.conf"

[ -e /etc/sysconfig/$prog ] && . /etc/sysconfig/$prog

lockfile=/var/lock/subsys/keepalived

start() {
    [ -x $exec ] || exit 5
    [ -e $config ] || exit 6
    echo -n $"Starting $prog: "
    daemon $exec $KEEPALIVED_OPTIONS
    retval=$?
    echo
    [ $retval -eq 0 ] && touch $lockfile
    return $retval
}

stop() {
    echo -n $"Stopping $prog: "
    killproc $prog
    retval=$?
    echo
    [ $retval -eq 0 ] && rm -f $lockfile
    return $retval
}

restart() {
    stop
    start
}

reload() {
    echo -n $"Reloading $prog: "
    killproc $prog -1
    retval=$?
    echo
    return $retval
}

force_reload() {
    restart
}

rh_status() {
    status $prog
}

rh_status_q() {
    rh_status &>/dev/null
}


case "$1" in
    start)
        rh_status_q && exit 0
        $1
        ;;
    stop)
        rh_status_q || exit 0
        $1
        ;;
    restart)
        $1
        ;;
    reload)
        rh_status_q || exit 7
        $1
        ;;
    force-reload)
        force_reload
        ;;
    status)
        rh_status
        ;;
    condrestart|try-restart)
        rh_status_q || exit 0
        restart
        ;;
    *)
        echo $"Usage: $0 {start|stop|status|restart|condrestart|try-restart|reload|force-reload}"
        exit 2
esac
exit $?
```

4. 配置keepalived.conf
```bash
vim /etc/keepalived/keepalived.conf

```
server1内容：  
```#!/usr/bin/env bash

! Configuration File for keepalived

global_defs {
    router_id MYSQL-1
}

vrrp_instance VI_1 {
   state BACKUP
   interface br0
   virtual_router_id 51
   priority 100
   advert_int 1
   nopreempt
   authentication {
       auth_type PASS
       auth_pass 1111
   }
   virtual_ipaddress {
       192.168.1.100
   }
}

virtual_server 192.168.1.100 3306 {
   delay_loop 6
   lb_algo rr
   lb_kind NAT
   persistence_timeout 50
   protocol TCP

   real_server 192.168.1.231 3306 {
       weight 1
       notify_down /etc/keepalived/bin/mysql.sh
       TCP_CHECK {
           connect_timeout 3
           nb_get_retry 3
           delay_before_retry 3
           connect_port 3306
      }
   }
}                                                                                                                                                            
```
server2内容一样，只需修改 **router_id**, **real_server**, **priority** 即可。

mysql.sh内容：    
```bash
> vim /etc/keepalived/bin/mysql.sh
```
内容：   
```bash
#!/bin/bash
 # pkill keepalived
 # /sbin/ifown br0 && /sbin/ifup br0
   counter=$(ps -C mysqld --no-heading|wc -l)
 if [ "${counter}" = "0" ]; then
     service keepalived stop
 fi
```

6. 启动 keepalived  
```bash
service keepalived start
```

7. 查看
```bash
# 查看网卡server1
ip addr list br0

4: br0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UNKNOWN
    link/ether 00:25:90:1f:a1:96 brd ff:ff:ff:ff:ff:ff
    inet 192.168.1.231/24 brd 192.168.1.255 scope global br0
    inet6 fe80::225:90ff:fe1f:a196/64 scope link
       valid_lft forever preferred_lft forever

```

server2：  
```bash
ip addr list eth0

2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP qlen 1000
    link/ether 00:25:90:1f:a1:82 brd ff:ff:ff:ff:ff:ff
    inet 192.168.1.233/24 brd 192.168.1.255 scope global eth0
    inet 192.168.1.100/32 scope global eth0
    inet6 fe80::225:90ff:fe1f:a182/64 scope link
       valid_lft forever preferred_lft forever
```
8. 注 mysql挂了之后，keepalived也会挂掉，需要重新启动

# Refrences
1. http://www.raye.wang/2017/04/14/mysqlzhu-cong-fu-zhi-da-jian-ji-yu-ri-zhi-binlog/    主从复制
2. http://blog.sina.com.cn/s/blog_821512b50101hxod.html   主从复制(贼详细)
3. http://blog.csdn.net/cjfeii/article/details/48623079   双活HA
4. https://zhuanlan.zhihu.com/p/23715039    Mysql高可用之Keepalived+mysql双主
