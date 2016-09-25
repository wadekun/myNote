# 在CentOS上安装RabbitMQ

## 官网文档

[Installing on RPM-based Linux](https://www.rabbitmq.com/install-rpm.html)

## 第一步 安装 Erlang（rabbitMQ是Erlang语言写的）
参考 http://stackoverflow.com/questions/21186276/unable-to-install-erlang-on-cent-os

install erlang using erlang-solution repo
* install repo
  `wget http://packages.erlang-solutions.com/erlang-solutions-1.0-1.noarch.rpm`
* install erlang
  `sudo yum install erlang`

## 安装 rabbitMQ
```bash
# 下载安装包
wget http://www.rabbitmq.com/releases/rabbitmq-server/v3.3.5/rabbitmq-server-3.3.5-1.noarch.rpm

# 安装
yum install rabbitmq-server-3.3.5-1.noarch.rpm
```
