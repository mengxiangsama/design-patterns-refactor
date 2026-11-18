# Go 重构风格与清理

## 先沿用项目约定

- 读取 `go.mod`、必要时的 `go.work`、构建标签、CI 和现有格式/lint 配置，以项目支持的 Go 版本为准；不顺手升级工具链、依赖或引入生成器。
- 优先用普通函数、结构体和组合表达变化；需要可替换行为时再引入贴近调用方需求的小接口，不为每个结构体机械增加接口或照搬 Java 类层次。嵌入会影响方法集与暴露的 API，不能只为少写转发代码而改变契约。
- 命名沿用项目惯例，保持包名、接收者和缩写一致；局部变量在短作用域内可简短，跨较长逻辑应能说明含义。导出名称和签名的改变需单独评估兼容性。
- 用清晰的错误检查和提前返回降低嵌套，但先核查返回值、资源释放和副作用顺序；不为统一外观强拆短函数。参见 [Go Code Review Comments](https://go.dev/wiki/CodeReviewComments) 和 [Effective Go](https://go.dev/doc/effective_go)。

## 删除无用变量与导入

按 [无用代码清理](dead-code-cleanup.md) 核查数据流和副作用，尤其注意：

- 删除已证实无用的局部绑定、被覆盖的赋值及普通 import；右侧调用仍有副作用时保留调用和既有错误处理，不用 `_ = unused` 或伪造引用掩盖未完成的清理。
- 多返回值只丢弃已确认不需要的值。将 `value, err := call()` 改为 `_, err := call()` 时检查同一作用域内 `err` 是否已声明；`:=` 必须至少引入一个新的非空白变量，需要时用赋值 `=`。移动声明或合并分支要检查 `err` 遮蔽、命名返回值与 defer 捕获的变量。
- 不为消除警告把 `err` 改成 `_`、吞掉失败或删掉校验。既有忽略错误若属业务缺陷，单独报告或按用户授权修复；不要混入等价重构。
- `_ "driver/package"` 等空白导入可能承担初始化注册；`var _ Interface = (*Type)(nil)` 可能是编译期接口断言。先确认用途，不能当普通无用 import/变量删除。保留必要的 cgo 导入、构建指令及生成来源。
- 编译器能发现普通未使用 import 和局部变量等问题，但不会证明包级符号、未使用参数或无效赋值都可删除；结合引用、入口与初始化路径判断。不要用 `go mod tidy` 代替源码 import 清理或扩大成依赖整理。

作用域、短变量声明与初始化规则见 [Go 规范](https://go.dev/ref/spec#Declarations_and_scope)；空白导入见 [Import declarations](https://go.dev/ref/spec#Import_declarations)。

## 保留 Go 的错误与生命周期语义

- 沿用返回 `error` 的契约及现有哨兵错误、错误类型和匹配方式。使用 `errors.Is`、`errors.As` 或 `%w` 时核查项目 Go 版本和调用方；包装会影响错误文本、身份及解包结果，不能无条件替换现有返回。参见 [错误包装说明](https://go.dev/blog/go1.13-errors)。
- 抽取函数、改为提前返回或搬动 defer 前，确认参数求值时机、关闭/解锁顺序、命名返回值以及 panic/recover 边界；不要因清理局部变量改变资源生命周期。
- 涉及并发时保留 context 的取消与超时传播、cancel 调用、goroutine 退出条件及 channel 关闭方；不要为重构额外启动 goroutine、替换为 `context.Background()`，或复制包含锁的值。context 规则见 [标准库文档](https://pkg.go.dev/context)。

## 排版与验证

- 对本次修改的 Go 文件运行项目约定的格式命令，至少保持 `gofmt` 格式；不手工对齐空格，不连带格式化无关目录。`gofmt -l` 可检查仍需格式化的文件。
- `gofmt` 负责格式，不负责补齐或删除未使用 import。项目已使用 `goimports`、`gci` 或其他 import 工具时沿用其配置和分组规则，复核自动改动；否则手工清理后运行 `gofmt`，无需为本次重构额外安装工具。参见 [gofmt](https://pkg.go.dev/cmd/gofmt) 与 [goimports](https://pkg.go.dev/golang.org/x/tools/cmd/goimports)。
- 优先运行项目已有检查脚本；无专项脚本时在对应模块按影响范围运行 `go test` 和 `go vet`，必要时扩大到 `go test ./...`、`go vet ./...`。匹配实际 build tags、GOOS/GOARCH 和多模块布局；涉及并发且环境支持时按需运行 `go test -race`。
- `go test` 默认只运行部分 vet 检查；`go vet` 也不能证明行为等价或覆盖全部无用代码。报告实际执行范围、跳过项与环境限制，不把格式通过、编译通过或少量测试通过说成全部行为已验证。参见 [go test](https://pkg.go.dev/cmd/go#hdr-Test_packages) 与 [go vet](https://pkg.go.dev/cmd/vet)。
