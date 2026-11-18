# Maven 检测与清理

## 先复现实际构建

从受影响的 `pom.xml`、父 POM、子模块、`.mvn/` 和 CI 找到真实入口。优先用项目的 `./mvnw` 或 `mvnw.cmd`。记录 Maven/JDK 版本、构建参数和启用的 profile。多模块项目在 reactor 根目录按模块选择，必要时用 `-pl :artifactId -am` 一起构建所需模块。继续检查使用该模块的下游。

以下命令以有 Wrapper 的项目为例。按项目实际情况追加与 CI 一致的 `-P`、`-pl` 和 `-f` 等参数。先检查目标插件版本是否提供对应 goal。

```bash
./mvnw help:active-profiles
./mvnw help:effective-pom -Dverbose
./mvnw dependency:tree
./mvnw clean dependency:analyze
./mvnw dependency:analyze-duplicate
./mvnw dependency:analyze-exclusions
```

`dependency:analyze` 会先执行到 `test-compile`，因此会产生编译产物及项目绑定的其他构建输出。把它的字节码诊断作为核查线索。 [依赖分析](https://maven.apache.org/plugins/maven-dependency-plugin/analyze-mojo.html) · [重复声明](https://maven.apache.org/plugins/maven-dependency-plugin/analyze-duplicate-mojo.html) · [排除项检查](https://maven.apache.org/plugins/maven-dependency-plugin/analyze-exclusions-mojo.html)

## 核对候选，再删 POM

| 线索 | 核查与处理 |
| --- | --- |
| `Unused declared` | 检查主代码、测试、资源、启动和打包。Spring Starter、自动配置、反射、ServiceLoader、JDBC 驱动、日志实现、测试引擎、JNI 及注解处理器都可能在字节码引用之外生效。确认用途不存在才删除。 |
| `Used undeclared` | 查依赖树和实际用法。项目直接使用传递依赖的 API 时，通常应在实际使用模块显式声明并用合适 scope，版本沿用 BOM 或现有管理。依赖集合由 Starter 或聚合模块有意管理时，先核对其契约。 |
| 重复声明、无效 `exclusion` 或闲置版本属性 | 通过依赖树、有效 POM 和来源注释判断实际选中的版本、scope 和归属。检查属性是否在子模块、profile、插件、CI 或资源过滤中使用。确认排除项移除前后实际依赖图符合预期，尤其留意对其他 profile 或版本的约束。 |
| 疑似没用的插件、execution 或 profile | 查默认生命周期、有效配置、Maven Wrapper 参数、CI 与打包发布脚本是否会触发。检查 `pluginManagement` 和 `dependencyManagement` 是否供子模块消费，BOM 和父 POM 也要考虑外部消费者。单次构建未激活的配置仍可能用于发布或集成测试。 |

注解处理器、插件依赖、构建扩展检查其独立配置与实际执行阶段。保留契约所需的依赖、模块和 profile。已有证据只覆盖部分环境时，说明验证边界并保留用途未确认的项。 [依赖机制与 scope](https://maven.apache.org/guides/introduction/introduction-to-dependency-mechanism.html) · [有效 POM 与来源](https://maven.apache.org/plugins/maven-help-plugin/effective-pom-mojo.html)

## 验证清理与持续检测

1. 分批删已确认的声明，再比较前后的有效 POM、依赖树及分析结果，重点检查运行时 classpath、生成源码、测试数量和打包内容。运行项目对应的 `clean verify` 与实际受影响的 profile。若改动影响运行时加载，执行对应启动或集成测试。
2. 项目需要 CI 持续检测时，固定兼容的 Maven Dependency Plugin 版本，在测试编译之后执行 `analyze-only`，例如绑定到 `verify`。先核验基线，再按需要开启 `failOnWarning`。只对有证据的运行时用法按依赖坐标配置例外，并写明原因，例如测试引擎由 Surefire 自动发现。 [生命周期中的 analyze-only](https://maven.apache.org/plugins/maven-dependency-plugin/analyze-only-mojo.html)
3. 交付时说明具体删除或保留的 POM 条目、用途证据、已验证的模块和 profile。构建成功应能看到预期的测试被执行，对运行时有影响的改动还应核对对应行为。
