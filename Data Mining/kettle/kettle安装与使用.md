# Kettle源码下载与编译
kettle：https://github.com/pentaho/pentaho-kettle   
Shims：https://github.com/pentaho/pentaho-hadoop-shims   

<!-- pentaho-osgi-bundles:  https://github.com/pentaho/pentaho-osgi-bundles -->

kettle、Shims checkout 相同版本的分支，进行编译。

将编译后的Shim：CDH14 放入 `data-integration/plugins/pentaho-big-data-plugin/hadoop-configurations/`目录下。  

# Kettle 链接 Hiveserver2
1. 修改`pentaho-big-data-plugin/plugin.properties`：`active.hadoop.configuration=hdp26`
2. 将`pentaho-big-data-plugin/hadoop-configurations/hdp26/lib`中`hive`开头的包全部删除，到服务器上拷贝`hive`开头的包到该目录下。   
3. 启动kettle，新建作业，主目录树中选择`Datasource Connection`，类型选择`Hiveserver2`，填写相应配置。



