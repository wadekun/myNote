# sleuth-zipkin分布式追踪

## 背景

在微服务改造背景下，随着服务数量的增多，系统追踪监控难度越来越大。例如在`A服务->B服务->C服务->D服务`这样一个调用过程中，如何监控整个调用链的耗时情况。

[zipkin](https://github.com/openzipkin/zipkin)项目就是来解决这个问题的。  
[spring-cloud-sleuth](https://github.com/spring-cloud/spring-cloud-sleuth)项目是springcloud专门针对spring boot服务进行日志监控的工具。

一下介绍在项目中集成`spring-cloud-sleuth+zipkin`进行全链路追踪。

## Spring Boot项目集成方法  

### 添加POM依赖

pom.xml代码：

```xml

<properties>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <!-- spring cloud 版本-->
    <spring-cloud.version>Finchley.SR2</spring-cloud.version>
</properties>

<!-- spring boot 版本：2.0.8.RELEASE  -->
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>2.0.8.RELEASE</version>
</parent>

<!-- spring cloud 版本依赖规范 -->
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-dependencies</artifactId>
            <version>${spring-cloud.version}</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>

<!-- 加入 sleuth, zipkin 依赖-->
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-sleuth</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-zipkin</artifactId>
</dependency>

<!-- trace log 通过kafka发送，需要在spring boot项目中加入kafka依赖 -->
<!-- spring kafka -->
<dependency>
    <groupId>org.springframework.kafka</groupId>
    <artifactId>spring-kafka</artifactId>
</dependency>
```

### 项目配置文件

application.yml代码：

```yaml
spring:
  application:
    # 服务名称（根据服务的功能设置成唯一值）
    name: log-service
  zipkin:
    # zipkin 服务端地址
    base-url: http://zipkinserver:9411
    enable: true
    kafka:
      topic: zipkin
    # 日志发送方式  
    sender:
      type: KAFKA
  sleuth:
    # 采样率控制
    sampler:
      percentage: 1.0
      probability: 1
  # kafka配置，将zipkin trace log发送到kafka
  # 后续可以配置zipkin server端从kafka消费日志数据，存入ES等存储
  kafka:
    bootstrap-servers: brocker1:9092,brocker2:9092,brocker3:9092
    consumer:
      group-id: uniondrug-log
      value-deserializer: org.apache.kafka.common.serialization.StringDeserializer
    producer:
      value-serializer: org.apache.kafka.common.serialization.StringSerializer
    listener:
      concurrency: 2
```

## zipkin server docker 部署

可以使用docker部署`zipkin server`，具体参照[docker-compose.yml](docker-compose.yml)。  
官方示例：<https://github.com/openzipkin/docker-zipkin>

### 请求调用链查看

经过上面配置之后，服务每被调用一次都会向kafka中发送一条调用数据。zipkin会消费kafka中的调用数据，存储至Elasticsearch中，并可以在zipkin中进行查询分析。

zipkin访问地址：<http://zipkinserver:9411/zipkin/>

当然也可以在`elasticsearch-head`或者`kibana`中直接查看es中存储的调用数据，索引名称以`zipkin`为前缀。

## logback 日志打入kafka

在生产环境中，通常需要在项目出现异常时进行告警，已经集中收集日志信息统一查看、分析。所以在项目中配置`logback`日志直接打入`kafka`，并且消费kafka日志消息，过滤日志`level=ERROR`的进行告警，通知开发或者运维人员进行查看修复。  
具体配置参照：[logback2kafka.md](logback2kafka.md)

## kafka-connect

可以使用`kafka-connect-elasticsearc`将kafka中的`logback`日志数据存入`elasticsearch`中，通过`kibana`等工具进行查看分析。

## 总结

这样，在项目中就实现了通过kafka统一收集`trace log`与通过`logback`打的系统日志，`elasticsearch`进行存储。  
同时可以自己开发`kafka-consumer`消费kafka中的`zipkin trace log`以及`logback log`定制**调用超时**以及**系统异常**告警服务。

## References

<https://cloud.spring.io/spring-cloud-static/spring-cloud-sleuth/2.0.2.RELEASE/single/spring-cloud-sleuth.html#_sampling>)
