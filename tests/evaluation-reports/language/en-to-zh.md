# 第三方声明检查报告

## 结论与适用范围

受检工程为 case-a 1.0.0。`package.json` 和 `LICENSE` 均声明工程使用 MIT。

本地证据表明，`THIRD_PARTY_NOTICES.md` 这个附加索引遗漏了 widget 内嵌的 mini-lib 2.0.0。但尚不能把这个索引遗漏认定为发布包中的许可声明缺失：`README.md` 说明发布源码和完整的 `node_modules/widget`，保留原许可文件；`publish.json` 包含 `node_modules/widget/**`。按这一发布方式，mini-lib 的声明和许可文本也会随包交付。

在已检查的本地文件中未发现许可声明彼此冲突；这不是最终产物完整合规或上游授权真实性的结论。

## 范围与取证

- npm：检查 `package-lock.json` v3 与实际安装目录，收集 1 个包 widget 1.0.0；锁定版本与 `node_modules/widget/package.json` 的版本一致，均声明 MIT。
- 内嵌组件：另外核对 mini-lib 2.0.0；它由 widget 的原始声明识别，不应因未列为独立 npm 依赖而忽略。
- 收集器 schema_version=1、status=collected，退出码 0；scopes 为 npm `lock_and_installed`，issues 为空。退出码仅表示支持范围内取证完成。
- 没有 Python 取证 scope，本次不提供 Python 环境或依赖完整性结论。
- 收集器跳过 `.cache`、`.git`、`.venv`、`__pycache__`、`node_modules`、`venv` 的工程级遍历；widget 许可文件通过包级取证收集。最终产物、外部二进制、资源清单及所有源码许可头未得到完整验证。

## 发现与证据

| 组件及版本 | 本地证据 | 判断与条件 | 最小建议动作 |
| --- | --- | --- | --- |
| widget 1.0.0 | `package.json`、`package-lock.json`、`node_modules/widget/package.json` 均给出版本或依赖关系；`node_modules/widget/LICENSE` 是 MIT 文本；`THIRD_PARTY_NOTICES.md` 已列 widget 并附该许可文本 | 在这些文件内，widget 的包级许可声明有原文支持，索引已收录 | 发布时保留原许可文件，并核对最终产物 |
| mini-lib 2.0.0 | `node_modules/widget/ThirdPartyNotices.txt` 明确列出该内嵌组件及 MIT，指向 `lib/bundle.js.LICENSE`；`node_modules/widget/lib/bundle.js.LICENSE` 包含 MIT 文本；`THIRD_PARTY_NOTICES.md` 没有 mini-lib 条目 | 附加索引存在组件遗漏。许可原文要求保留版权及许可通知；根据 `README.md` 与 `publish.json`，这些原文按计划会一起发布，因此本地证据不足以确认交付时遗漏该通知 | 在附加索引补充组件和原许可路径，发布后验证相应文件实际存在；本次未修改工程 |

mini-lib 许可文件的版权行原样摘录（`node_modules/widget/lib/bundle.js.LICENSE`）：

> Copyright (c) 2026 Mini Authors

`node_modules/widget/ThirdPartyNotices.txt` 的简略版权声明未列年份，报告摘录以指向的许可原文为准。

## 未确认项

1. 最终交付物尚未生成或核查。若后续打包删除原声明文件，当前关于“通知随包保留”的条件就不成立；需在实际交付物中检查 widget 的 `LICENSE`、`ThirdPartyNotices.txt` 和 `lib/bundle.js.LICENSE`。
2. widget 与 mini-lib 的上游精确版本、授权来源、是否存在本地修改尚未核实。此次仅使用本地证据，未做联网核验，也未给出具体法律兼容性结论。
3. 其他源码许可头、外部二进制和资源未完整识别，不可把本次未发现冲突扩展到全部发布内容。

收集器没有 issues，也未发生执行失败；以上未确认项来自取证范围和发布条件，不能由 status=collected 消除。
