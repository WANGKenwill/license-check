中文 | [English](README_EN.md)

# license-check

为 Agent 提供开源许可证检查能力：收集本地依赖许可证据，结合使用和分发方式，分析声明遗漏与待确认事项。

## 安装

取证需要 **Python 3.11+**，无第三方 Python 依赖。使用安装器另需 Node.js 和 npm。

在要检查的项目目录中运行，按提示选择 Agent：

```bash
npx skills add WANGKenwill/license-check --skill license-check
```

加 `--global` 可安装到用户目录。仅安装 `skills/license-check/`，不包含测试和开发文档。

手动安装：下载或克隆仓库，将 `skills/license-check/` 整个目录复制到客户端的技能目录。

## 使用

安装后向 Agent 提出：

> 使用 license-check 检查当前工程。计划公开源码，不交付外部工具的二进制。请列出声明遗漏、证据和未确认项。

按实际情况说明交付方式，例如源码、安装包或容器。报告默认在对话中输出，需要保存时指定位置。

## 支持范围

- npm：package-lock.json v2/v3 与已安装包对照，收集包内第三方声明。
- Python：读取 `.venv`、`venv` 或指定环境的元数据，尚未核对锁文件一致性。
- 取证脚本只读、不联网、不安装依赖、不执行项目代码。

未覆盖最终发布产物、外部二进制和全部源码许可头；取证完成不代表全面合规通过。

## 开发与反馈

在仓库根目录运行测试：

```bash
python3 -m unittest discover -s tests -v
```

[评测记录与案例](tests/evaluation.md) · [反馈问题](https://github.com/WANGKenwill/license-check/issues)

反馈时提供脱敏后的最小案例，避免上传完整扫描 JSON 或私有代码。实测 macOS、Ubuntu CI；Windows 尚未验证。

[MIT License](LICENSE) · Copyright (c) 2026 WANGKenwill
