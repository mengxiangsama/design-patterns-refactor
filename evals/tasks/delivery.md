# 请求

使用 $design-patterns-refactor 评估这个订单生产与余额消费模块能否在异常、重启和消息重投后恢复。说明事务边界、方案取舍和需要验证的故障场景。只读分析，不接入外部服务、不改文件。

输入：[service.py](../fixtures/order_delivery/service.py)。
