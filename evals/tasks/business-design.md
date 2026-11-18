# 请求

在当前项目中显式调用 `$design-patterns-refactor`，发送以下请求：

```text
要一个商品更新同步
```

分别用 [项目 A](../fixtures/business_design/detail/README.md) 和 [项目 B](../fixtures/business_design/search/README.md) 独立运行。每次只将对应项目的 README 复制到一个新的临时项目根目录，打开该项目并使用新会话。两次都发送同一条业务请求，除 Skill 调用外无需再提供技术路线或组件名。

另开一次临时项目会话，发送同一句话但不选择 Skill，记录客户端是否自动加载它。通过客户端的调用记录或上下文加载记录核对触发情况。若没有这类记录，将触发检查标为未验证。
