# 商品管理与搜索项目事实

以下是虚拟项目的事实快照。表中的位置标识事实来源，本夹具只提供这份快照。

| 位置 | 当前行为 |
| --- | --- |
| `ProductController#update` | 后台编辑会更新 MySQL 的 `product` 行。 |
| `catalog-import/README.md` | 定时导入任务另有独立连接，直接批量更新同一张表。 |
| `ProductSearchController#search` | 商品搜索从 Elasticsearch 商品索引读取名称、价格和上下架状态，目前靠手工全量更新索引。 |
| `application.yml`、交付记录 | 项目已接入 MySQL 和 Elasticsearch，RocketMQ 也已用于现有订单消息。当前商品写入路径均没有投递变更。 |
| `db/product.sql`、更新约定 | 三个索引字段都在 `product` 表，同一商品的 `revision` 由两个写入口在各自事务内递增。 |

商品更新后允许几秒才在搜索结果可见。索引服务停机恢复后要能追平，允许重复收到消息，迟到的旧版本不能覆盖更新的价格或让下架商品重新出现。首期要为已有商品建立索引。是否开通读取 binlog 的权限、既有日志保留周期及峰值更新量尚未确认。
