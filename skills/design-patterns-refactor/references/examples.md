# 可运行 Java 案例

代码随 Skill 一起分发，位置：[assets/java-examples](../assets/java-examples/README.md)。只在需要教学或重构参考时读相关案例。

| 案例 | 问题与选择 | 验证点 |
| --- | --- | --- |
| PricingCase | 会员计价规则独立变化，switch → Strategy + 注册表 | 相同输入金额一致、舍入、非法输入、重复注册 |
| ShippingCase | 物流 SDK 接受克数和供应商状态码 → Adapter | 单位换算、错误码、返回合同、调用次数 |
| ExportCase | 输出压缩/编码组合分支 → Decorator | 字节一致、解码恢复、组合顺序 |

每个文件含 Before 与 After。它们是可执行教学对照，不意味着真实系统必须长期保留两套实现。
三个案例只是样例覆盖；选型参考覆盖 23 种模式，不代表都有代码实现。
