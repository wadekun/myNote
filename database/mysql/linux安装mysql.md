1、准备工作
环境：CentOS6.5
版本：mysql-5.7.18-linux-glibc2.5-x86_64.tar.gz

2、解压
tar -zxvf /data/software/mysql-5.7.18-linux-glibc2.5-x86_64.tar.gz
mv mysql-5.7.18-linux-glibc2.5-x86_64/* /usr/local/mysql/

3、添加用户/组
shell> groupadd mysql?
shell> useradd -r -g mysql -s /bin/false mysql

4、建立mysql默认的配置文件/etc/my.cnf
[mysqld]?
basedir=/usr/local/mysql
datadir=/usr/local/mysql/data
socket=/tmp/mysql.sock
user=mysql
port=3306
server_id=1
# Disabling symbolic-links is recommended to prevent assorted security risks
symbolic-links=0

5、建立data文件夹，并给mysql用户赋予权限
mkdir /usr/local/mysql/data
shell> chmod 750 data
shell> chown -R mysql .
shell> chgrp -R mysql .

6、在mysql目录下对mysqld初始化
bin/mysqld --initialize --user=mysql

7、添加服务，启动
cp /usr/local/mysql/support-files/mysql.server /etc/init.d/mysqld
service mysqld start

8、修改root登陆密码
bin/mysql --user=root -p
update user set password=password('123') where user='root' and host='localhost';
flush privileges;
或
set password for root@localhost = password('123');
或
alter user 'root'@'localhost' identified by 'newpswd'

9、开机自启动
# chmod 755 /etc/init.d/mysql
# chkconfig --add mysql
# chkconfig --level 345 mysql on

10、设置允许其他机器访问mysql
```sql
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY '123456'  WITH GRANT OPTION;
-- GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY 'password';
flush privileges;
```

NOTE:
1、错误：
Starting MySQL...The server quit without updating PID file (/usr/local/mysql/data/snsgou.pid)
解决：log-error=/var/log/mysqld.log 该日志文件无写权限
