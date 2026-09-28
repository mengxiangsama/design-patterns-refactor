# Python：用函数组合重构导出 / Function composition

Python 3.9+，仅使用标准库。在本目录运行：

```bash
python3 -B -m unittest discover -s . -p 'test_*.py' -v
```

[export_case.py](export_case.py) 包含 `before` 和 `after`：输入字符串迭代器，输出 UTF-8 字节，可选 GZIP 压缩后再 Base64 编码。`after` 将变换组织为函数序列，没有引入 Java 式接口或类层次。只有需要独立组合/扩展变换时才值得这样改；功能长期固定时，`before` 仍是合理实现。

[test_export_case.py](test_export_case.py) 验证四种组合、空值与 Unicode 输入、迭代器消费次数、错误传播和变换执行顺序。压缩固定 `mtime=0`，同一运行环境内比较前后结果；不承诺不同 Python/zlib 版本产生完全相同的 GZIP 字节。

The example uses Python functions instead of a class hierarchy. Tests cover byte equality, independent decoding, single-pass iteration, exceptions, and transform order. This is a teaching example, not a benchmark or proof that an agent can refactor arbitrary Python projects.
