# Design Patterns Refactor · 跨语言 AI 代码重构 Skill

[中文](README.md) | [English](README.en.md)

[![CI](https://github.com/mengxiangsama/design-patterns-refactor/actions/workflows/ci.yml/badge.svg)](https://github.com/mengxiangsama/design-patterns-refactor/actions/workflows/ci.yml) · [MIT License](LICENSE)

**让 AI 根据真实代码选择重构方案，而不是为了设计模式而设计。**

面向 Codex 的跨语言 Skill，用于遗留代码重构（legacy code refactoring）、设计模式选型、无用代码清理，以及微服务边界与最终一致性评估。适用于 Java/Spring Boot、Go、Python、TypeScript 等项目，优先采用目标语言的函数、接口与组合方式。

- **先找证据**：追踪调用链，给出代码位置、问题和取舍。
- **允许保持简单**：稳定分支不必套模式；只想分析时不改代码。
- **保留行为**：保护异常、金额、事务、顺序和外部副作用，报告验证边界。

当前提供 **Java 和 Python 的可运行对照案例**，不代表所有语言、模式或模型都经过验证。这是编码助手的工作指引，不是独立运行的重构工具。

[快速开始](#快速开始) · [使用场景](#使用场景) · [实际案例](#实际案例) · [安装与更新](#安装与更新) · [常见问题](#常见问题)

## 快速开始

在终端执行，默认安装到 `~/.agents/skills/design-patterns-refactor`：

```bash
git clone https://github.com/mengxiangsama/design-patterns-refactor.git
cd design-patterns-refactor
bash scripts/install.sh
```

需要 Git、Bash 和 tar；仅使用 Skill 不需要 Java、Maven 或 Python。Windows 可用 Git Bash 或 WSL，但应安装在实际运行编码助手的环境中。

然后在 Codex 中打开**你要分析的项目**，发送：

```text
$design-patterns-refactor
分析当前模块的高价值重构点，比较直接简化与设计模式方案。
给出代码证据、收益和代价，遵循项目语言的惯用写法。先不要修改代码。
```

## 使用场景

**Python / Go / TypeScript：不照搬 Java 类层次**

```text
$design-patterns-refactor
分析这个 Python 导出模块，优先考虑函数和组合。
保留迭代求值顺序、异常传播和输出格式。先给方案，不改代码。
```

**无用代码：检查仍在使用的方法内部**

```text
$design-patterns-refactor
清理当前订单模块已确认无用的代码，包括无效赋值和冗余判断。
保留有副作用的调用、动态入口和对外契约，直接修改并运行相关测试。
```

**适配器重构：统一外部接入，保留契约**

```text
$design-patterns-refactor
重构第三方物流接入，统一内部接口。
保留错误映射、单位换算和调用次数，直接修改相关代码并运行回归测试。
```

**跨微服务：边界、分布式事务与消息可靠性**

```text
$design-patterns-refactor
评估订单服务与库存服务的边界和消息一致性。
检查业务提交、投递、幂等、重试与补偿，比较本地事务、Outbox 或 Saga。
基于我提供的仓库给方案和验证计划，先不修改、不部署。
```

跨服务任务按需覆盖拆分/合并、数据归属、Outbox/Saga/TCC、对账补偿，以及消费组、顺序、死信和重放。请指定可访问仓库、参与服务与业务约束；不包含 Kubernetes、网关或监控平台运维，也不推断隐藏仓库的实现。

## 实际案例

导出需要支持“原文、压缩、编码、压缩后编码”四种组合。这里既有 Java 装饰器，也有 Python 函数组合，不要求不同语言使用相同结构。

| 案例 | 重构选择 | 已提供的测试 |
| --- | --- | --- |
| [Java 会员计价](skills/design-patterns-refactor/assets/java-examples/src/main/java/examples/PricingCase.java) | 独立规则 → 策略与注册表 | 金额精度、边界输入、重复注册 |
| [Java 物流接入](skills/design-patterns-refactor/assets/java-examples/src/main/java/examples/ShippingCase.java) | 供应商接口 → 适配器 | 单位、错误映射、副作用调用次数 |
| [Java 导出](skills/design-patterns-refactor/assets/java-examples/src/main/java/examples/ExportCase.java) | 可选处理 → 装饰器 | 组合顺序、字节一致与解码 |
| [Python 导出](skills/design-patterns-refactor/assets/python-examples/README.md) | 可选处理 → 普通函数序列 | 四种组合、单次迭代、异常与执行顺序 |

Python 案例的 `after` 保留先 GZIP、后 Base64 的顺序；测试比较重构前后的字节，并独立解码验证原文。功能长期固定时，保留原来的分支也是合理结论。案例随 Skill 安装，可运行但不连接真实业务服务。

[选型参考](skills/design-patterns-refactor/references/pattern-selection.md) 覆盖 GoF 23 种模式及常见领域/架构候选，**不代表已经实现 23 个案例**。[行为评估](evals/scenarios.md) 另提供 Python 清理、事务恢复和消息拓扑的固定输入与评分依据，不把案例测试当成模型能力证明。

## 安装与更新

### 安装到其他位置

在仓库目录执行，参数是 **skills 父目录**：

```bash
bash scripts/install.sh /path/to/your-project/.agents/skills
```

若客户端使用 `~/.codex/skills`，可传 `"$HOME/.codex/skills"`。不要在多个扫描位置重复安装。目录发现规则参见 [OpenAI 官方说明](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)。

### 通过 skills CLI 安装（可选）

已安装 Node.js/npm 时，也可使用 [skills CLI](https://github.com/vercel-labs/skills)，按提示选择客户端和安装范围：

```bash
npx skills add mengxiangsama/design-patterns-refactor --skill design-patterns-refactor
```

默认项目级安装；全局安装加 `--global`。与 Bash 安装方式二选一，避免同名副本。目录使用方式、遥测和隐私选项由第三方 CLI 管理；它支持多个客户端，不代表本 Skill 已完成所有客户端的行为验证。[skills.sh 收录机制](https://skills.sh/docs/faq) 基于 CLI 安装遥测，不是 GitHub Star 数，也不保证收录时效或排名。

### 更新 Bash 安装的副本

**`git pull` 只更新仓库源码，不会同步更新已经复制安装的 Skill。** 在仓库目录依次执行：

```bash
git pull --ff-only
python3 scripts/update.py --check
python3 scripts/update.py
```

更新器需要 Python 3.9+ 和 Git，无第三方 Python 依赖。自定义安装位置须在两条更新命令后加同一个 skills 父目录，例如 `"$HOME/.codex/skills"`。Windows 没有 `python3` 命令时可使用 `py -3`。

- `--check` 只检查版本，不写文件；正式更新前将已安装内容与仓库历史逐文件比较。
- 仅更新可识别且未经自定义修改的副本；新增、修改、缺失文件或符号链接会阻止更新，没有强制覆盖选项。比较时忽略构建/缓存产物（`target`、`__pycache__`、`.DS_Store`），原副本仍完整备份。
- 原目录备份到 skills 父目录旁的 `skill-backups/`，不放进 skills 扫描目录。切换目录失败或按 Ctrl+C 时尝试恢复；强制结束进程后，检查、更新和安装命令会识别未完成记录并提示恢复。
- 默认检查最近 100 次涉及 Skill 的提交；旧版本可用 `--from-ref <commit-or-tag>` 指定基线，仍须内容完全匹配。未知版本需先人工比较。

**更新中断、安装目录不见了？** 保留备份和隐藏的更新记录，在仓库目录执行：

```bash
python3 scripts/update.py --recover
python3 scripts/update.py --check
python3 scripts/update.py
```

自定义安装位置时，三条命令均加同一个 skills 父目录；Windows 可将 `python3` 换成 `py -3`。`--recover` 会校验记录和文件：旧目录已移走时还原旧版；新版已完整启用时完成收尾，不回滚新版。恢复后再检查、更新即可。文件被手工修改或记录异常时会拒绝覆盖，需人工比较；旧版更新器没有恢复记录的备份也需人工处理。`.update.lock` 锁文件留存是正常现象，锁由操作系统管理，进程退出后会释放，无需删除。

通过 skills CLI 安装的版本，使用其更新命令 `npx skills update design-patterns-refactor`，不要混用本仓库的副本更新器。更新前自行保留本地自定义内容；本仓库的保护规则不等于第三方 CLI 的保证。

## 常见问题

**安装后找不到？** 检查实际安装目录下是否有 `design-patterns-refactor/SKILL.md`，以及客户端是否扫描该父目录。项目级安装要在对应项目中使用；WSL 与 Windows 的用户目录不是同一个位置。刷新 Skill 列表或新开会话，仍不显示再重启客户端。

**提示目录已存在？** 安装器故意拒绝覆盖，避免丢失修改。不要为了重装直接删除目录；先运行上面的更新检查，或确认是否已经通过其他安装器安装。

**我修改过 Skill，怎么更新？** 更新器会停止，不覆盖。对比仓库新版本与自己的副本，人工合并；或先将自定义版本备份到扫描目录外，再决定是否重新安装。源码本身也须与 Git 提交一致，不能把未提交内容当成正式版本更新。

**只想分析，会自动改代码吗？** 指令要求分析请求保持只读、实施请求才修改，但 Skill 不是权限隔离机制，仍需结合客户端权限设置。

**代码会被上传吗？** Skill 本身不内置外部 API 或项目代码上传逻辑；代码访问、模型处理与第三方安装器行为由相应客户端和服务决定。

**用了就更快、更安全吗？** 不保证。设计模式不等于性能优化，生成方案仍需评审与项目自身的测试；Go/TypeScript 等语言目前没有随包可运行案例。

## 开发与验证

在仓库根目录执行（macOS/Linux/WSL）：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/validate.py
.venv/bin/python -B -m unittest discover -s tests -v
.venv/bin/python -B -m unittest discover -s skills/design-patterns-refactor/assets/python-examples -v
.venv/bin/python -B -m unittest discover -s evals/fixtures/python_cleanup -v
.venv/bin/python -B -m unittest discover -s evals/fixtures/order_delivery -v
mvn -B -f skills/design-patterns-refactor/assets/java-examples/pom.xml verify
```

原生 Windows 的虚拟环境 Python 路径为 `.venv\Scripts\python.exe`。Java 案例以 Java 8 字节码为目标，建议用 JDK 17+、Maven 3.8+ 构建；这些不是使用 Skill 的依赖。

CI 在 Ubuntu、macOS、Windows 上检查元数据/本地链接、安装更新、Python 案例及评估夹具基线；Java 案例另用 Ubuntu + JDK 17/21 验证。安装更新测试覆盖 Ctrl+C、三个目录切换阶段的强制退出，以及 `core.autocrlf=true` 的克隆安装；`.gitattributes` 固定文本和 Shell 脚本为 LF。Windows 测试使用 Git Bash，无符号链接权限时仅跳过相应符号链接用例。订单夹具测试**复现原始故障**，不代表问题已修复；模型行为须单独评估，真实 MQ/生产环境未由这些测试验证。

## 贡献与许可

欢迎提供脱敏使用反馈、其他语言案例和有意义的回归测试。阅读 [贡献指南](CONTRIBUTING.md)，在 [Issues](https://github.com/mengxiangsama/design-patterns-refactor/issues) 讨论较大改动；不要提交商业代码、客户信息或凭证。

[变更记录](CHANGELOG.md) · [Skill 正文](skills/design-patterns-refactor/SKILL.md) · [MIT License](LICENSE)
