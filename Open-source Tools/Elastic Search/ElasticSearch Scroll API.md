## 今天来学习下ElasticSearch Scroll API
两篇相关文章：[Elasticsearch Scroll API详解](http://hansight.com/blog-elasticsearch-scroll-api.html) | [扫描和滚屏](http://es.xiaoleilu.com/060_Distributed_Search/20_Scan_and_scroll.html)

`scan` 搜索类型 和 `scroll` API一起使用来从Elasticsearch里高效的取回巨大数据量的结果而不需要付出 深度分页的代价。

## 相关数据库知识
传统数据库游标：游标(cursor)是系统为用户开设的一个数据缓冲区，存放sql语句的执行结果。每个游标区都有一个名字，用户可以用sql语句逐一从游标中获取记录，并赋值给主变量，交由主语言进一步处理。简单说就是 数据库将受影响的数据暂存到了一个内存虚表中，这个虚表就是游标。

## Scroll 滚屏
Scroll允许我们做一个初始阶段的搜索并且持续批量的从Elasticsearch中拉取数据直至没有结果剩下。有点像传统数据库的cursor(游标)。例如分页搜索中，直接获取第100页的数据，elasticsearch通常会先确定docs的排序，然后取出第一页至第100页的数据，然后去掉前99页。 scroll搜索会一开始将所有数据缓存起来，为下一次请求做准备。

Scroll搜索会及时的制作快照。这个快照不会保存任何在初始请求之后对index所做的修改。通过将旧的数据文件保存在手边，保护index看起来像搜索开始时的样子。

存储资源的空间是有限的，不可能一直保存每一次Scroll搜索时的快照。所以，在Scroll搜索时要传递一个参数，就是保存快照的时长。

## Scroll 使用
使用Scroll API很简单，只需要在查询后加上参数 `scroll=t`，其中t 就是快照保存的时间，例如：`curl -XGET localhost:9200/bank/account/_search?pretty&scroll=2m -d {"query":{"match_all":{}}}`，其中`2m`代表保存时间2分钟（数字+单位）。   
单位如下：

| Time | units     |
| :------------- | :------------- |
| y      | year       |
| M | month|
| w | week |
| d | day  |
| h | hours |
| m | minute|
| s | second |
上面的查询语句 返回的结果如下：
```
{
  "_scroll_id": : " cXVlcnlUaGVuRmV0Y2g7NTs5MTM6aDEySHRHNVpScVNiN2VUZVV6QV9xdzs5MTQ6aDEySHRHNVpScVNiN2VUZVV6QV9xdzs5MTU6aDEySHRHNVpScVNiN2VUZVV6QV9xdzs5MTc6aDEySHRHNVpScVNiN2VUZVV6QV9xdzs5MTY6aDEySHRHNVpScVNiN2VUZVV6QV9xdzswOw==",
  "took" : 3,
  "timed_out" : false,
  "_shards" : {
    "total" : 5,
    "successful" : 5,
    "failed" : 0
    }…
```
观察结果可以发现，新增了 `_scroll_id` 字段，这是在之后的查询所用到的句柄，之后的查询如下：
```
curl –XGET 'localhost:9200/_search/scroll?
scroll=2m&pretty&scroll_id=cXVlcnlUaGVuRmV0Y2g7NTs5MTM6aDEySHRHNVpScVNiN2VUZVV6QV9xdzs5MTQ6aDEySHRHNVpScVNiN2VUZVV6QV9xdzs5MTU6aDEySHRHNVpScVNiN2VUZVV6QV9xdzs5MTc6aDEySHRHNVpScVNiN2VUZVV6QV9xdzs5MTY6aDEySHRHNVpScVNiN2VUZVV6QV9xdzswOw=='
```
在上面语句的返回结果中，又会包含`_scroll_id`字段，每次查询都会返回一个`_scroll_id`，也就是最新的查询句柄，只有最新的`_scroll_id`是有效的。    
在查询中如果包含聚合，则只有最初的查询结果是聚合结果。

## Scanning Sroll API
深度分页最大的代价是对结果的全局排序，如果禁用排序就可以以很低的代价获得全部返回结果。如果对查询结果的排序不感兴趣，可以使用`Scanning and scroll`。使用方法很简单，只需在查询语句后面加上`search_type=scan`即可。
```
GET /old_index/_search?search_type=scan&scroll=1m  // 保持Scroll开启一分钟
{
    "query": { "match_all": {}},
    "size":  1000
}
```
这个请求的响应没有包含任何命中的结果，但是包含了一个Base-64编码的_scroll_id（滚屏id）字符串。现在我们可以将_scroll_id传递给_search/scroll末端来获取第一批结果。

A Scanning scroll 查询与 a standard scroll 查询有几点不同：
1. A scanning Scroll 结果没有排序，结果的顺序是doc入库时的顺序；
2. A scanning scroll 查询不支持聚合；
3. A scanning Scroll 最初的查询结果"hits"列表中不会包含结果；
4. A scanning scroll 最初的查询中如果设定了"size"：
```
curl -XGET 'localhost:9200/bank/account/_search?pretty&scroll=2m&search_type=scan' -d '{"size":3,"query":{"match_all":{}}}'
```
这个size会应用到每个分片上，所以我们在每个批次里最多获得 size * number_of_primary_shards （size * 主分片数）个document。

## 清除Scroll API
默认在超时后，scroll数据会自动删除。当然也可以手动删除。
1. 删除单个：
```
curl -XDELETE 'localhost:9200/_search/scroll' -d 'c2Nhbjs2OzM0NDg1ODpzRlBLc0FXNlNyNm5JWUc1'
```
2. 删除所有
```
curl -XDELETE ‘localhost:9200/_search/scroll/_all’
```
