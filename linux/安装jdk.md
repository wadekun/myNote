# 命令行安装jdk

## Downloading Latest Java Archive

**64位**
```
# cd /opt/
# wget --no-cookies --no-check-certificate --header "Cookie: gpw_e24=http%3A%2F%2Fwww.oracle.com%2F; oraclelicense=accept-securebackup-cookie" "http://download.oracle.com/otn-pub/java/jdk/7u79-b15/jdk-7u79-linux-x64.tar.gz"

# tar xzf jdk-7u79-linux-x64.tar.gz
```

**32位**
```
# cd /opt/
# wget --no-cookies --no-check-certificate --header "Cookie: gpw_e24=http%3A%2F%2Fwww.oracle.com%2F; oraclelicense=accept-securebackup-cookie" "http://download.oracle.com/otn-pub/java/jdk/7u79-b15/jdk-7u79-linux-i586.tar.gz"

# tar xzf jdk-7u79-linux-i586.tar.gz
```

**jdk8 64**
```shell
cd /opt/
wget --no-cookies --no-check-certificate --header "Cookie: gpw_e24=http%3A%2F%2Fwww.oracle.com%2F; oraclelicense=accept-securebackup-cookie" "http://download.oracle.com/otn-pub/java/jdk/8u131-b11/d54c1d3a095b4ff2b6607d096fa80163/jdk-8u131-linux-x64.tar.gz"

tar xzf jdk-8u131-linux-x64.tar.gz
```
## Install Java with Alternatives
> After extracting archive file use alternatives command to install it. alternatives command is available in chkconfig package.

```bash
# cd /opt/jdk1.8.0_131/
# alternatives --install /usr/bin/java java /opt/jdk1.8.0_131/bin/java 2
# alternatives --config java


There are 3 programs which provide 'java'.

  Selection    Command
-----------------------------------------------
*  1           /opt/jdk1.7.0_71/bin/java
 + 2           /opt/jdk1.8.0_45/bin/java
   3           /opt/jdk1.8.0_91/bin/java
   4           /opt/jdk1.8.0_131/bin/java

Enter to keep the current selection[+], or type selection number: 4

```

## Check Installed Java Version
```bash
root@tecadmin ~# java -version

java version "1.8.0_131"
Java(TM) SE Runtime Environment (build 1.8.0_131-b11)
Java HotSpot(TM) 64-Bit Server VM (build 25.131-b11, mixed mode)
```
