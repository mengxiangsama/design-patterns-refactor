# 公开方案资料索引

从业务目标出发选读相关原始资料。每条记录可借鉴的办法和落到项目时要核对的边界。厂商文档描述其产品或参考实现。项目的部署状态、实际约束和验证结果需要单独取证。

## 商品同步与搜索投影

| 原始资料 | 适用场景与核对项 |
| --- | --- |
| [Microsoft Azure Architecture Center · CQRS](https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs) | 读写模型有明显差异时，可将检索、排序和聚合交给独立读模型。也可以在同一数据存储里分离读写模型。先核对现有查询能否满足需求，以及独立投影的可见延迟、修复成本和权威数据来源。 |
| [Debezium · MySQL 快照与变更捕获](https://debezium.io/documentation/reference/stable/connectors/mysql.html#mysql-snapshots) | 需要首次全量与持续增量时，参考一致性快照和对应 binlog 起点的衔接。核对所用连接器版本、锁和权限、主从切换、位点存储及日志保留。演练回填期间并发写入和位点过期后的重建。 |
| [Elasticsearch · 文档写入与外部版本](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-index) | 多次更新可能重复或乱序时，用稳定文档 ID 和单调版本保护投影。`external` 对已存在文档只接受严格更高版本。核对全量与增量是否遵循同一版本规则，演练旧的上架消息在下架后重放。物理删除要另核对删除版本保留。 |
| [Elasticsearch · 用别名切换索引](https://www.elastic.co/docs/manage-data/data-store/aliases) | 重建搜索索引时先构建新索引、回放到切换水位并对账，再用别名切换读写指向。核对操作结果与别名实际指向。索引回切时仍需确认旧索引数据是否追平。 |
| [Discord 工程团队 · 搜索索引迁移实践](https://discord.com/blog/how-discord-indexes-trillions-of-messages) | 搜索服务需要在重建期间继续读写时，可参考按目标索引分批写入，以及新旧索引并行接收增量、历史回填完成后切换查询的做法。验证单个写入目标故障时其他批次的进度，以及双写部分成功的恢复方式。 |

## 订单超时、补偿与支付确认

| 原始资料 | 适用场景与核对项 |
| --- | --- |
| [Apache RocketMQ · 延时消息](https://rocketmq.apache.org/docs/featureBehavior/02delaymessage/) | 已有支持延时投递的 MQ 且要求接近到期处理时，用消息触发关单检查。文档描述的 5.x 模式使用目标投递时间，并列出范围和 Topic 类型限制。核对实际 Broker、客户端和集中到期时的延迟。消费时以数据库截止时间和状态做条件更新，覆盖消息提前到达、延后或重复。 |
| [Amazon SQS · 消息计时器](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-message-timers.html) | 选择按条延时前先查队列类型与时长限制。SQS 的单条消息计时器最长 15 分钟，FIFO 队列不支持单条计时器。用实际订单支付窗口验证能力，再选择定时扫描、调度器或其他延时机制。 |
| [Kubernetes · CronJob 的创建限制](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/#job-creation) | 定时扫描可作为主要触发，也可用来补延时消息的漏单。CronJob 文档明确允许特定条件下漏建或重复创建 Job。以持久化截止时间为扫描条件，验证跳过一个周期、停机跨过截止时间和任务重叠。消息消费者与扫描任务可以复用同一关单方法。 |
| [Temporal · 持久化计时器](https://docs.temporal.io/develop/java/workflows/timers) | 项目已有工作流引擎，且流程需要反复等待、恢复或接收业务信号时，可比较持久化计时器。计时器由工作流持久化，服务与 Worker 恢复后继续执行。核对停机积压、工作流升级和到期后的外部操作幂等。 |
| [Stripe · 取消 PaymentIntent](https://docs.stripe.com/api/payment_intents/cancel) | 支付与关单有竞态时，从实际渠道文档确认可撤销状态、未知结果的查单方式和终态。Stripe 示例中，能否取消取决于 PaymentIntent 的状态及对应接入流程。查单显示暂未支付时，仍需核对在途支付能否成功。确认订单可按未支付关单后，再按业务规则释放资源。 |

## 可靠投递与消费

| 原始资料 | 适用场景与核对项 |
| --- | --- |
| [AWS Prescriptive Guidance · 事务 Outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html) | 写入业务数据后必须可靠发布事件时，把业务记录与待发记录放在同一本地事务，提交后由投递器轮询或通过 CDC 推送。发送成功但投递记录尚未更新时可能重发。验证回滚、重启、确认丢失及乱序，按业务事件 ID 或版本去重。消费副作用和去重标记写同一数据库时，用同一事务提交。 |
