# Windows下
修改 tomcat_home/bin/setclasspath.sh
修改 tomcat_home/bin/catalina.sh

例如jdk目录为/usr/local/jdk8，修改时分别在开头处加上：   
```
set JAVA_HOME=/usr/local/jdk8
set JRE_HOME=/usr/local/jdk8/jre
```
# Linux下
修改 tomcat_home/bin/setclasspath.sh
修改 tomcat_home/bin/catalina.sh

例如jdk目录为/usr/local/jdk8，修改时分别在开头处加上：   
```
export JAVA_HOME=/usr/local/jdk8
export JRE_HOME=/usr/local/jdk8/jre
```
