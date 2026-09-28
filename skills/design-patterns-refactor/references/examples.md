# 可运行案例

代码随 Skill 一起分发。Java/Spring 任务可看 [Java 案例](../assets/java-examples/README.md)，需要函数组合的非 Java 对照时看 [Python 案例](../assets/python-examples/README.md)。只读与当前任务有关的代码，不用示例的结构限制目标语言。

| 案例 | 问题与选择 | 验证点 |
| --- | --- | --- |
| PricingCase | 会员计价规则独立变化，switch → Strategy + 注册表 | 相同输入金额一致、舍入、非法输入、重复注册 |
| ShippingCase | 物流 SDK 接受克数和供应商状态码 → Adapter | 单位换算、错误码、返回合同、调用次数 |
| ExportCase | 输出压缩/编码组合分支 → Decorator | 字节一致、解码恢复、组合顺序 |
| Python export_case | 输出变换组合 → 普通函数序列，不引入类层次 | 四种组合、单次迭代、异常传播、执行顺序 |

每个案例含重构前后实现。它们是可执行教学对照，不意味着真实系统必须长期保留两套实现。
案例测试只覆盖所列契约；选型参考覆盖 23 种模式，不代表都有代码实现，也不证明模型在所有语言上的判断质量。
