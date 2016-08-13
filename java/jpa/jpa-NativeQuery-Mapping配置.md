# 场景描述
在JPA中使用HQL不能满足需要使用Native Query(例如需要多表联合查询，或者对某个字段进行分组统计时)，Native Query的查询结果是 List<Object[]>，即把每条记录都直接以Object数组的形式返回了，并没有进行任何的Bean转换，因为ORM框架(Hibernate)不知道怎样对结果进行映射。最后往往需要手动对查询结果进行转换。

# 解决方案
使用`@NamedNativeQuery`注解定义Native Query，使用`@SqlResultSetMapping`注解定义POJO映射(类似于Mybatis的ResultMap)。

# 例子

## 场景描述
例如有个对订单按日期进行统计的需求，Native Query 如下：
```
SELECT ifnull(sum(order_price), 0) AS day_money, ifnull(count(order_id), 0) AS day_count, DATE_FORMAT(pay_time, '%Y-%m-%d') AS pay_time
				FROM order
				WHERE order_status = '3'
				      AND pay_time BETWEEN :startTime and :endTime
				GROUP BY DATE_FORMAT(pay_time, '%Y-%m-%d')
```

## 定义native query
```
@NamedNativeQueries({
		@NamedNativeQuery(name = "Order.getStatisticsBeans", query = "SELECT ifnull(sum(order_price), 0) AS day_money, ifnull(count(order_id), 0) AS day_count, DATE_FORMAT(pay_time, '%Y-%m-%d') AS pay_time " +
				"FROM order " +
				"WHERE order_status = '3' " +
				"      AND pay_time BETWEEN :startTime and :endTime " +
				"GROUP BY DATE_FORMAT(pay_time, '%Y-%m-%d') ", resultSetMapping = "orderStatisticsBean")
})
```
注：@NamedNativeQuery要定义在@Entity中。

## 定义 resultSetMapping
```
@SqlResultSetMapping(
		name = "orderStatisticsBean",
		classes = {
				@ConstructorResult(
						targetClass = StatisticsBean.class,
						columns = {@ColumnResult(name = "pay_time", type = String.class), @ColumnResult(name = "day_count", type = Long.class), @ColumnResult(name = "day_money", type = BigDecimal.class)}
				)
		}
)
```
即POJO与查询结果的映射，在`@NamedNativeQuery`的`resultSetMapping`中要指定该resultMapping。

## 在Repository中定义查询方法
```
@Query(nativeQuery = true)
    List<StatisticsBean> getStatisticsBeans(@Param("startTime") String startTime, @Param("endTime") String endTime);
```

# 参考资料

* http://stackoverflow.com/questions/29082749/spring-data-jpa-map-the-result-to-non-entity-pojo
* http://stackoverflow.com/questions/25179180/jpa-joining-two-tables-in-non-entity-class/25184489#25184489
* http://stackoverflow.com/questions/11452586/sqlresultsetmapping-columns-as-and-entities
* http://stackoverflow.com/questions/25188939/mapping-nativequery-results-into-a-pojo
* http://stackoverflow.com/questions/24160817/getting-error-could-not-locate-appropriate-constructor-on-class
