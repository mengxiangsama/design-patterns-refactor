# 重构前后案例

Java 8 语法，建议用 JDK 17+ 和 Maven 3.8+ 执行测试：

```bash
mvn -B -f skills/design-patterns-refactor/assets/java-examples/pom.xml verify
```

也可以进入本目录执行 `mvn verify`。测试使用 JUnit 5，不启动 Spring、不访问外部服务。

- [PricingCase](src/main/java/examples/PricingCase.java)：策略将独立计价规则分开，注册表只负责选择；若只有两个长期稳定的规则，Before 也完全合理。
- [ShippingCase](src/main/java/examples/ShippingCase.java)：适配器将供应商克数/错误码转换为业务千克/运单结果；供应商是注入的测试桩。
- [ExportCase](src/main/java/examples/ExportCase.java)：装饰器组合 GZIP 和 Base64。使用者显式决定顺序。

[回归测试](src/test/java/examples/RefactoringTest.java) 比较 Before/After 和独立预期结果，检查错误、边界及副作用次数。这些示例不连接支付、物流或数据库，也不声称是完整生产实现。
