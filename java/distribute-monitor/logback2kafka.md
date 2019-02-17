# logback日志存入kafka

在项目中，可直接配置logback日志存入kafka，方便后续收集分析

## 配置

* pom.xml：

```xml
<!-- 引入logback-kafka-appender 依赖包 -->
<dependency>
    <groupId>com.github.danielwegener</groupId>
    <artifactId>logback-kafka-appender</artifactId>
    <version>0.2.0-RC2</version>
    <scope>runtime</scope>
</dependency>
<!-- 输出JSON格式日志 -->
<dependency>
    <groupId>net.logstash.logback</groupId>
    <artifactId>logstash-logback-encoder</artifactId>
    <version>5.3</version>
    <scope>runtime</scope>
</dependency>
<!-- logback 包 -->
<dependency>
    <groupId>ch.qos.logback</groupId>
    <artifactId>logback-classic</artifactId>
    <version>1.2.3</version>
</dependency>
```

* logback-spring.xml

**建议使用logback-spring.xml替代logback.xml**
logback.xml后于`application.yml`解析，无法读取`application.yml`中配置的变量信息。

```xml
<appender name="STDOUT" class="ch.qos.logback.core.ConsoleAppender">
    <encoder class="ch.qos.logback.classic.encoder.PatternLayoutEncoder">
        <!--格式化输出：%d表示日期，%thread表示线程名，%-5level：级别从左显示5个字符宽度%msg：日志消息，%n是换行符-->
        <pattern>%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{50} - %msg%n</pattern>
    </encoder>
</appender>

<!-- 获取服务名 -->
<springProperty scope="context" name="appName" source="spring.application.name"/>

<!-- This is the kafkaAppender -->
<appender name="kafkaAppender" class="com.github.danielwegener.logback.kafka.KafkaAppender">
    <!--<encoder>
        <pattern>%d{HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n</pattern>
    </encoder>-->

    <encoder class="net.logstash.logback.encoder.LoggingEventCompositeJsonEncoder">
            <providers>
                <!--<timestamp>
                    <timeZone>UTC</timeZone>
                </timestamp>-->
                <pattern>
                    <pattern>
                        {
                        "level": "%level",
                        "service": "${appName:-}",
                        "trace": "%X{X-B3-TraceId:-}",
                        "span": "%X{X-B3-SpanId:-}",
                        "parent": "%X{X-B3-ParentSpanId:-}",
                        "exportable": "%X{X-Span-Export:-}",
                        "pid": "${PID:-}",
                        "thread": "%thread",
                        "time": "%date{\"yyyy-MM-dd HH:mm:ss.SSS\"}",
                        "class": "%logger{40}",
                        "line_number": "%line",
                        "stack_trace": "%exception{5}",
                        "content": "%message"
                        }
                    </pattern>
                </pattern>
            </providers>
        </encoder>

    <topic>uniondrug.java.logs</topic>
    <keyingStrategy class="com.github.danielwegener.logback.kafka.keying.NoKeyKeyingStrategy" />
    <deliveryStrategy class="com.github.danielwegener.logback.kafka.delivery.AsynchronousDeliveryStrategy" />

    <!-- Optional parameter to use a fixed partition -->
    <!-- <partition>0</partition> -->

    <!-- Optional parameter to include log timestamps into the kafka message -->
    <!-- <appendTimestamp>true</appendTimestamp> -->

    <!-- each <producerConfig> translates to regular kafka-client config (format: key=value) -->
    <!-- producer configs are documented here: https://kafka.apache.org/documentation.html#newproducerconfigs -->
    <!-- bootstrap.servers is the only mandatory producerConfig -->
    <producerConfig>bootstrap.servers=broker1:9092,broker2:9092,broker3:9092</producerConfig>

    <!-- this is the fallback appender if kafka is not available. -->
    <appender-ref ref="STDOUT" />
</appender>

<!-- 异步输出日志 -->
<appender name="ASYNC" class="ch.qos.logback.classic.AsyncAppender">
    <appender-ref ref="kafkaAppender" />
</appender>

<!-- 在自定义logger中引入异步kafka appender -->
<logger name="com.corefy.log" level="INFO" >
    <appender-ref ref="ASYNC" />
</logger>
```

## kafka中接收到的消息示例

```json
{
  "level": "INFO",
  "service": "log-service",
  "trace": "968ccac06d5d1671",
  "span": "4f8c0432284695af",
  "parent": "326181b3fb4cd5d1",
  "exportable": "true",
  "pid": "17178",
  "thread": "org.springframework.kafka.KafkaListenerEndpointContainer#0-1-C-1",
  "time": "2019-02-12 16:19:21.981",
  "class": "c.corefy.log.kafka.LogConsumer2Frontend",
  "line_number": "?",
  "stack_trace": "",
  "content": "received message: {\"id\":0,\"requestId\":\"JSDFLJ7989-NJONKL112-MLJSLJDF\",\"time\":\"2019-01-24 10:13:34.123456\",\"module\":\"java.mudule.user\",\"level\":\"INFO\",\"serverAddr\":\"192.168.1.43:8080\",\"requestMethod\":\"POST\",\"requestUrl\":\"/u/login\",\"content\":\"test batch 05\",\"action\":\"C\",\"duration\":0.000123,\"pid\":1,\"taskId\":0,\"taskName\":\"test_task\"}"
}
```

## 编码注意

建议统一使用SLF4J包进行日志打印：  

## 注意事项

* 在部署时，需要修改`logback-spring.yml`中的`producerConfig`配置，需要在`application.yml`中指定配置文件位置：

```yaml
logging:
  level: debug
  # 指定配置文件位置
  config: file:/uniondrug/log-service/config/logback-spring.xml
```

* 需要提前在ES中设置index的mapping，不然ES有可能将time识别为text格式，会影响根据time进行的一些操作  
[es-log-mappings.md](es-log-mappings.md)