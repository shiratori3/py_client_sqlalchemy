# SQL python客户端

基于SQLAlchemy的sql python客户端

## 当前实现功能

### 基础功能

- 通过LogManager管理器管理输出信息流，通过logging.yaml文件进行配置
- 通过Ignorer管理gitignore文件，避免文件误上传
- 通过ConfManager管理器管理yaml形式的配置文件

### SQL客户端

- 通过ConnManagerUI实现SQL服务器登录的指令式交互（增加/删除/更改连接信息/更改连接名称/清空），并通过ConnManager管理器管理用户登录凭证，可rsa加密保存
- 读取SQL语句文件并以dataframe或list of tuple形式返回查询结果，并保存查询结果至对应excel文件
- 通过SqlTemplate创建模板，目前仅支持错别字查询模板
- 以jupyter notebook的形式执行

### 网络请求及响应

- 通过RequestParams统一发起request并处理对应response

## 后续希望实现的功能

- RequestParams的多线程化
