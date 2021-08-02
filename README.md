# 简单的sql python客户端

基于SQLAlchemy的python客户端

## 当前实现功能

- 基于命令形式的用户登录凭证管理器（增删改），可保存用户登录凭证（rsa加密）
- 读取SQL语句文件并以dataframe或list of tuple形式返回查询结果，并保存查询结果至对应excel文件
- 以jupyter notebook的形式执行

## 后续希望实现的功能

- 底层配置文件用更流行的yaml库而非自带的configparser库
