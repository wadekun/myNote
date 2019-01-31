# kafka-connect-elasticsearch 遇到的问题
## 问题描述
kafka-connect-elasticsearch 将kafka数据写入es时，默认将日志中一个时间类型的字段`time`（格式为`yyyy-MM-dd HH:mm:ss.SSSSSS`）mapping设置成了`text`，导致无法根据时间进行排序。

## 解决方案
停止connect进程，更新mapping配置。

1. time类型设置为`date`，添加`format`字段
2. `log`type下设置    

`"date_detection": true`：开启时间字符串检测
`"dynamic_date_formats": ["yyyy-MM-dd HH:mm:ss.SSSSSS||yyyy-MM-dd HH:mm:ss"]`：动态时间格式，匹配这两个格式的字符串都将索引成功

重新启动connect进行，就可以看到新增的数据了。

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