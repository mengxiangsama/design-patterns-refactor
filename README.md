# Design Patterns Refactor

面向业务代码重构的 **Codex Skill + 可运行案例**。从代码中的职责、变化点和兼容要求出发，选择合适的模式，给出方案或按请求实施重构。

支持不同业务领域和语言，当前可执行案例使用 Java。它不要求每个项目都使用设计模式，也不会仅凭复杂分支就自动改造全仓。

## 能做什么

- 分析实际调用链，区分业务缺陷、维护成本与性能问题。
- 比较直接简化与模式方案，说明采用或放弃理由。
- 按请求生成重构前后案例，或在目标项目中实施最小范围修改。
- 保留已有接口、异常、执行顺序、金额与外部副作用语义。
- 执行相关测试；报告未验证部分和依赖限制。

仅分析时不改代码；明确要求实现时执行修改。Skill 不自动上传目标项目的代码，不内置外部 API 调用；实际代码访问与模型处理由你使用的宿主环境决定。

## 安装

只使用 Skill 不需要 Java、Maven 或 Python 依赖。以下安装脚本需要 Bash 和 tar（macOS/Linux；Windows 可用 Git Bash 或 WSL）。

```bash
git clone https://github.com/mengxiangsama/design-patterns-refactor.git
cd design-patterns-refactor
bash scripts/install.sh
```

默认安装到 `~/.agents/skills/design-patterns-refactor`。若已存在同名目录，脚本拒绝覆盖。

项目级安装，把下方路径替换为你实际项目的路径：

```bash
bash scripts/install.sh /path/to/your-project/.agents/skills
```

如宿主环境使用 `~/.codex/skills`，可将该目录作为参数传入。不要在多个扫描位置重复安装同名 Skill。

这是独立 Skill 目录的安装方式，路径和发现机制参见 [OpenAI 官方说明](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)。安装后在 Codex 中查看 Skill 列表；没有显示时重启客户端。

仓库发布后，也可以让内置安装器按仓库与路径安装：

```text
$skill-installer
从 mengxiangsama/design-patterns-refactor 安装 skills/design-patterns-refactor。
```

## 使用

**先分析：**

```text
$design-patterns-refactor
分析当前模块中耦合、重复逻辑和扩展问题。
比较直接简化与设计模式方案，给出代码证据、收益和代价，先不要修改。
```

**直接重构：**

```text
$design-patterns-refactor
重构第三方物流接入，统一内部接口并保留现有错误和单位换算语义。
直接修改相关代码并运行回归测试。
```

**生成案例：**

```text
$design-patterns-refactor
基于当前导出模块生成重构前后案例，说明是否适合装饰器，
包含组合顺序、异常处理和可运行测试。
```

**保持简单：**

```text
$design-patterns-refactor
这两个稳定的业务分支是否值得抽象？如果收益不足，请保留直接实现。
```

## 模式范围

[选型参考](skills/design-patterns-refactor/references/pattern-selection.md) 包含 GoF 23 种模式，以及规格、仓储、领域事件等常见领域/架构候选。每种都说明适用信号和不适用条件。

| 类别 | 模式 |
| --- | --- |
| 创建型（5） | 工厂方法、抽象工厂、建造者、原型、单例 |
| 结构型（7） | 适配器、桥接、组合、装饰器、门面、享元、代理 |
| 行为型（11） | 责任链、命令、解释器、迭代器、中介者、备忘录、观察者、状态、策略、模板方法、访问者 |

模式清单是选型知识，**不代表仓库已经实现了 23 个可运行案例**。以下三个案例已经提供代码和测试：

| 案例 | 重构方式 | 验证重点 |
| --- | --- | --- |
| 会员计价 | 分支 → 策略 + 注册表 | 金额精度、边界输入、重复注册 |
| 物流接入 | 供应商接口 → 适配器 | 单位、错误映射、副作用调用次数 |
| 导出处理 | 可选功能分支 → 装饰器 | 压缩/编码组合、顺序、字节一致 |

案例位于 [java-examples](skills/design-patterns-refactor/assets/java-examples/README.md)，随 Skill 一起安装。它们不依赖原来的 design Demo，也不连接真实物流或支付系统。

## 开发与验证

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/validate.py
.venv/bin/python -m unittest discover -s tests -v
mvn -B -f skills/design-patterns-refactor/assets/java-examples/pom.xml verify
```

Java 案例以 Java 8 语法/字节码为目标，构建使用 JDK 17+、Maven 3.8+；Maven 的作用仅是运行案例测试，不是使用 Skill 的必要条件。

CI 执行包结构/链接校验、安装回归和 Java 测试。[行为评估场景](evals/scenarios.md) 用于观察 Skill 在真实请求中的判断，结构校验通过并不证明所有模型都能正确选型。

## 项目结构

```text
skills/design-patterns-refactor/
  SKILL.md                 工作流与资源路由
  agents/openai.yaml       展示名与调用提示
  references/              选型、Java 注意事项、案例索引
  assets/                  交付模板和带测试的 Java 案例
scripts/                   安装与包校验
tests/                     安装行为回归
evals/                     模型行为评估场景
.github/workflows/         自动验证
```

## 贡献与许可

新增案例时提供问题证据、简化方案、选型理由、Before/After 和行为测试。不要为了凑齐模式数量增加没有实际变化点的示例。修复行为与结构重构应分别说明。

本仓库原创内容使用 [MIT License](LICENSE)；案例依赖保留各自许可证。
