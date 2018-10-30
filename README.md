# xiaoqiang_log

小强日志记录程序，数据存储在本地mongodb数据库，然后在有网络时上传服务器。
本程序主要用于统计机器人数据。比如机器人电压随时间的变化，机器人任务执行情况等等。把需要记录的数据发送至/xiaoqiang_log话题。

## 相关话题

|话题|类型|
|--|--|
|/xiaoqiang_log|LogRecord|

## 使用方式

在服务端运行xiaoqiang_log_server节点。并配置好xiaoqiang_log_node的server_url。详细的例子可以参考xiaoqiang_log_test.launch文件

把需要统计的数据发送至/xiaoqiang_log话题。数据会根据网络自动同步到远程服务端的数据库。
