# 参与贡献 / Contributing

欢迎贡献文档、脱敏反馈、测试和其他语言的重构案例。普通贡献者可以 Fork 仓库，在自己的分支提交修改，再向本仓库发起 Pull Request。

Documentation, sanitized feedback, tests, and language-native examples are welcome. Fork the repository, commit changes on your own branch, and open a pull request.

## 适合开始的方向 / Where to start

- 修正文档、翻译和失效链接 / Fix documentation, translations, or broken links.
- 提供“无需设计模式”的反例 / Add cases where direct simplification is better.
- 提出 Go、Python 或 TypeScript 案例方案 / Propose idiomatic Go, Python, or TypeScript examples.
- 补充边界、异常和兼容性测试 / Improve boundary, error, and compatibility coverage.

增加模式、依赖或修改工作流前，请先开 Issue 说明实际问题。不要仅为了覆盖所有模式添加案例。

Discuss new patterns, dependencies, or workflow changes in an issue first. Do not add examples solely to complete a pattern checklist.

## 提交要求 / PR checklist

- 解释实际问题、最简单替代方案、采用或放弃模式的理由。
- 保持修改聚焦；业务行为修复与结构重构分开说明。
- 案例需说明输入、返回、错误、执行顺序与副作用，并提供回归测试。
- 更新相关中英文文档；仅修改根目录文档时不必修改技能正文。
- 说明运行过的检查以及未验证内容，不把静态检查当作运行验证。
- 不提交真实业务代码、客户数据、凭证、日志中的个人信息或无法授权公开的内容。

Explain the problem, simpler alternatives, and pattern trade-offs. Keep changes focused, separate behavior fixes from refactoring, and include meaningful regression tests. Update relevant documentation and state verification limits. Never submit confidential code, credentials, or personal data.

## 验证 / Verification

Follow the development commands in [README](README.md). Documentation changes should pass the metadata/local-link validator; installer changes need installation tests; Java example changes need Maven verification. New language examples must document their toolchain and runnable tests without requiring production services.

使用反馈请描述任务、预期行为、实际行为、宿主环境及可公开的最小复现。不要为了提供复现泄露商业代码。

For feedback, describe the task, expected and actual behavior, host environment, and a safe minimal reproduction.
