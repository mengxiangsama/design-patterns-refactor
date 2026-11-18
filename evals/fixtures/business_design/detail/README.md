# 商品后台项目事实

以下是虚拟项目的事实快照。表中的位置标识事实来源，本夹具只提供这份快照。

| 位置 | 当前行为 |
| --- | --- |
| `ProductController#update` | 后台修改名称和展示状态，调用 `ProductService#save` 并返回成功。 |
| `ProductService#save` | 一个本地事务更新 MySQL 主库的 `product` 行。编辑器是唯一写入口。 |
| `ProductController#detail` | 通过同一服务查询同一主库的 `product` 行。当前未配置查询缓存或只读副本。 |
| `application.yml`、依赖清单 | 当前只接入 MySQL。项目没有消息中间件或独立检索服务。 |

运营验收要求：保存成功后重新打开商品详情，立即看到最新名称和状态。这个项目只在后台详情页使用这些字段。
