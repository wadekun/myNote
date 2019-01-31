# kafka-connect-elasticsearch 遇到的问题
背景：
>应用日志需要存储到es进行分析查询，而且需要根据当前日志等级（INFO、ERROR等）进行前端告警等操作，所以需要提供接口给各个应用，然后统一写入kafka，不同消费者处理不同的业务逻辑（邮件告警、前端告警、存ES以及其他流处理等）。这里采用了kafka的组件kafka-connect-elasticsearch完成kafka到es的数据同步工作，同时es中只保存两周的数据，两周前的数据需要根据time字段删除。

## 问题描述
kafka-connect-elasticsearch 将kafka数据写入es时，默认将日志中时间类型的字段`time`（格式为`yyyy-MM-dd HH:mm:ss.SSSSSS`）mapping设置成了`text`，导致无法根据时间进行排序（Range查询）。

## 解决方案
停止connect进程，更新mapping配置。

1. time类型设置为`date`，添加`format`字段
2. `log`type下设置    

`"date_detection": true`：开启时间字符串检测
`"dynamic_date_formats": ["yyyy-MM-dd HH:mm:ss.SSSSSS||yyyy-MM-dd HH:mm:ss"]`：动态时间格式，匹配这两个格式的字符串都将索引成功

重新启动connect进行，就可以看到新增的数据了。


## delete两周前的log代码
```java
// 删除两周之前的es日志，每天凌晨一点执行
@Scheduled(cron = "0 0 1 1/1 * ?")
public void deleteOldLogs() {
    String twoWeeksLaterStr = LocalDateTime.now().minusDays(14).format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss.SSSSSS"));

    // 设置时间范围
    RangeQueryBuilder rangeQuerybuilder = QueryBuilders
            .rangeQuery("time")
            .lte(twoWeeksLaterStr).format("yyyy-MM-dd HH:mm:ss.SSSSSS");

    DeleteByQueryAction.INSTANCE.newRequestBuilder(elasticsearchTemplate.getClient())
            .filter(rangeQuerybuilder)
            .source(index)
            .execute(new ActionListener<BulkByScrollResponse>() {
                @Override
                public void onResponse(BulkByScrollResponse bulkByScrollResponse) {
                    LOGGER.info("delete two weeks later logs: {} docs.", bulkByScrollResponse.getDeleted());
                }

                @Override
                public void onFailure(Exception e) {
                    e.printStackTrace();
                }
            });
}
```

## mapping：    
```json
{
  "mappings": {
    "log": {
      "date_detection": true,
      "dynamic_date_formats": ["yyyy-MM-dd HH:mm:ss.SSSSSS||yyyy-MM-dd HH:mm:ss"],
      "properties": {
        "level": {
          "type": "text",
          "fields": {
            "keyword": {
              "ignore_above": 256,
              "type": "keyword"
            }
          }
        },
        "module": {
          "type": "text",
          "fields": {
            "keyword": {
              "ignore_above": 256,
              "type": "keyword"
            }
          }
        },
        "requestMethod": {
          "type": "text",
          "fields": {
            "keyword": {
              "ignore_above": 256,
              "type": "keyword"
            }
          }
        },
        "pid": {
          "type": "long"
        },
        "content": {
          "type": "text",
          "fields": {
            "keyword": {
              "ignore_above": 256,
              "type": "keyword"
            }
          }
        },
        "duration": {
          "type": "float"
        },
        "serverAddr": {
          "type": "text",
          "fields": {
            "keyword": {
              "ignore_above": 256,
              "type": "keyword"
            }
          }
        },
        "requestId": {
          "type": "text",
          "fields": {
            "keyword": {
              "ignore_above": 256,
              "type": "keyword"
            }
          }
        },
        "requestUrl": {
          "type": "text",
          "fields": {
            "keyword": {
              "ignore_above": 256,
              "type": "keyword"
            }
          }
        },
        "action": {
          "type": "text",
          "fields": {
            "keyword": {
              "ignore_above": 256,
              "type": "keyword"
            }
          }
        },
        "taskName": {
          "type": "text",
          "fields": {
            "keyword": {
              "ignore_above": 256,
              "type": "keyword"
            }
          }
        },
        "id": {
          "type": "long"
        },
        "time": {
          "type": "date",
          "format": "yyyy-MM-dd HH:mm:ss.SSSSSS",
          "fields": {
            "keyword": {
              "ignore_above": 256,
              "type": "keyword"
            }
          }
        },
        "taskId": {
          "type": "long"
        }
      }
    }
  }
}
```