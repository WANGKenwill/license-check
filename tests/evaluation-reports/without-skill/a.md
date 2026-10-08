# 任务 A：第三方声明遗漏审查

审查日期：2026-10-04。范围：case-a 中全部现有文件、隐藏文件与 node_modules；仅静态只读检查，没有安装依赖、运行工程、构建或修改目标文件。本报告未使用许可证审查 Skill。

## 结论

**当前明确的发布方案下，不需要为满足已发现的 MIT 声明保留义务而修改工程。** 顶层 THIRD_PARTY_NOTICES.md 的索引有遗漏：它只列 widget 1.0.0，没有列 widget 内嵌的 mini-lib 2.0.0。但这不是实际分发材料中的声明缺失，因为工程明确分发完整 widget 目录，内嵌组件的版权与许可全文均在其中。应区分“索引不完整”和“许可证义务不满足”。

如要求该索引自身完整，可以补一行 mini-lib 名称、版本、MIT 与原始许可路径；这是可选的可发现性改善，不应把它判成当前必须修复的发布阻断项。没有对工程做任何修改。

## 本地证据

| 文件及行号（相对 case-a） | 内容与意义 |
| --- | --- |
| package.json:1；package-lock.json:1 | 唯一列明的依赖为 widget 1.0.0，许可证 MIT；元数据不是完整组件清单。 |
| THIRD_PARTY_NOTICES.md:3 | 汇总仅列 widget 1.0.0: MIT。 |
| node_modules/widget/ThirdPartyNotices.txt:1–2 | 明确声明 Embedded components，mini-lib 2.0.0: MIT，版权为 Mini Authors，并指向 lib/bundle.js.LICENSE。 |
| node_modules/widget/lib/bundle.js.LICENSE:1–21 | 包含 MIT 全文及 Copyright (c) 2026 Mini Authors，尤其第 12–13 行的保留要求。 |
| node_modules/widget/LICENSE:1–21 | widget 自身 MIT 全文和版权声明。 |
| README.md:1 | 明确说明分发源码及完整 node_modules/widget，包括原始许可证；顶层通知仅是附加索引，不删依赖文件。 |
| publish.json:1 | 发布文件列表包括 node_modules/widget/**，因此上述两个内嵌声明路径均被涵盖。 |

MIT 要求复制品或实质性部分保留版权与许可声明，没有要求必须集中在单一顶层文件。[OSI MIT 正文](https://opensource.org/license/mit)。上述发布方案保留原始声明的方式满足本次发现的条件，这是基于现有文件与发布配置的判断。

## 验证与未确认事项

1. 已遍历整个给定目录，交叉核对 package/lock、依赖许可证、嵌入声明与发布文件配置，未发现其他第三方组件线索。
2. 未取得实际发布归档，也未运行打包流程；publish.json 只是明确的配置证据，不能证明任意发布工具一定遵守它。发布前应检查实际归档确实含 widget/LICENSE、widget/ThirdPartyNotices.txt 与 widget/lib/bundle.js.LICENSE。
3. 给定目录没有实际 bundle.js 内容，无法验证上游内嵌组件列表是否穷尽全部代码。当前结论仅覆盖已提供的组件声明。
4. 待确认问题：最终发布工序是否按 README/publish.json 保留完整目录？评测无人答复，保留这一事实核验项；它不改变当前指定发布方案下无需修改的结论。

## 工具与局限

使用 exec_command 执行 ls、rg --files -uuu 和 Python 标准库读取文本并加行号；使用 web 官方页面核对 MIT 条款；Python 仅用于读取和写本报告，不执行目标工程代码。未读取主工作区、任何许可证审查 Skill 或 with-skill 目录。审查是限定范围的证据判断，不是对未提供发布物的全量保证。
