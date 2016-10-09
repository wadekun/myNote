# Message Queue（消息队列）
消息队列中间件是分布式系统中重要的组件，主要解决应用耦合，一部消息，流量削峰等问题。实现高性能，高可用，可伸缩，最终一致性架构。

消息队列的应用场景有：异步处理，应用解耦，流量削峰和消息通讯等

目前比较流行的消息队列实现有：`ActiveMQ, RabbitMQ, ZeroMQ, Kafka, MetaMQ, RocketMQ`等。


# Java消息服务 （Java Message Service）

## 简介
Java Message Service（Java消息服务） 是一个Java平台关于消息服务的一套规范（类似于JDBC）。提供了一套接口，允许应用程序基于Java平台来创建，消费消息。

## 消息模型
JMS标准目前支持两种消息模型：P2P（Point to Point），Publish/Subscribe（Pub/Sub）


## JMS编程模型（应用程序接口）
* `ConnectionFactory`接口 （连接工厂）

创建 Connection对象的工厂，针对两种不同的jms消息模型，分别有 `QueueConnectionFactory`和`TopicConnectionFactory`

* `Connection` 接口 （连接）

Connection 标示在客户端和JMS系统之间建立的连接（对TCP/IP socket的包装）。
与 ConnectionFactory一样，Connection也有`QueueConnection`和`TopicConnection`

* `Destination` 接口

Destination 的意思是消息生产者的消息发送目标或者说消息消费者的消息来源。即某个队列（Queue）或主题（Topic）

* `Session` 接口

Session 是操作消息的接口。可以通过session创建生产者、消费者、消息等。是一个单线程的上下文。由于是单线程，所以，消息是按照顺序发送的，并且可以支持事务。同样，也分QueueSession和TopicSession。

* `MessageProducer`接口（消息生产者）

由会话创建的对象，用于发送消息到目标。用户可以创建某个目标的发送者。有两个子接口：`QueueSender`和`TopicPublisher`

* `MessageConsumer` 接口 （消息消费者）

接收发送到目标的消息。消费者可以同步阻塞，或异步非阻塞的接收队列和主题类型的消息。

* `MessageListener` 消息监听者

如果注册了消息监听器，一旦消息到达，将自动调用监听器的`onMessage`方法。

* `Message` 消息接口

  是在消息消费者和生产者之间传送的对象。一个消息有三个主要部分：
  1. 消息头（必须）：包含用于识别和为消息寻找路由的操作设置
  2. 一组消息属性（可选）：包含额外的数学，支持其他提供者和用户的兼容。客户创建定制的字段和过滤器。
  3. 一个消息体（可选）：允许用户创建五种类型的消息（文本消息，映射消息，字节消息，流消息和对象消息：BytesMessage, MapMessage, ObjectMessage, StreamMessage, TextMessage）


# 参考资料

[大型网站架构系列：分布式消息队列（一）](http://www.cnblogs.com/itfly8/p/5155983.html)

[大型网站架构系列：消息队列（二）](http://www.cnblogs.com/itfly8/p/5156155.html)
