# 说明
* TABLE_NAME : 要查询的表名
* COLUMN_NAME: 字段名

# 查看每张表的实际使用物理空间大小
```sql
select num_rows * avg_row_len/1024/1024 "实际表占用空间大小(M)" from user_tables where table_name = 'TABLE_NAME';
```
# 常用分页
```sql
select * from (select a.*, ROWNUM rnum from ( select * from TABLE_NAME order by COLUMN_NAME ) a where ROWNUM <= 10 ) where rnum > 0;
```

# 分页优化版
```sql
-- 使用rowid加速
select * from TABLE_NAME d, (select rid from (select rownum rn, t.rid from (select rowid rid from TABLE_NAME order by COLUMN_NAME) t where rownum <= 10)  where rn > 0) t2 where d.rowid = t2.rid;
```
