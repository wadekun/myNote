# 修改字段
ALTER TABLE `item` CHANGE COLUMN `item_id` `item_id` BIGINT(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID';

# 删除索引
alter table table-name DROP PRIMARY KEY;

**如果索引是自增的，删除索引可能会失败提示，自增字段必须是一个key**   

这时需要将字段的自增长去掉，也就是正常的修改字段语句

# 新增索引
alter table  table-name ADD PRIMARY KEY (`item_id`);
