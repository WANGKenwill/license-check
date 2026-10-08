# 任务 A：第三方声明遗漏检查

## 结论

**按照已提供的分发方式，不需要为了满足 MIT 许可条件修改 THIRD_PARTY_NOTICES.md；该文件作为附加索引，确实少列 mini-lib 2.0.0，可选补全索引。** 这不是已确认的发布包许可义务遗漏：原始内嵌声明和完整许可随整个 widget 目录交付。无需更改工程 MIT 许可证。

工程：tests/fixtures/evaluation/case-a。工程自身 LICENSE 和 package.json 声明 MIT。适用条件：最终发布确实保留 node_modules/widget 下的原始许可及第三方声明，符合 README.md 和 publish.json 描述。

## 证据与判断

| 组件／文件 | 本地证据 | 判断和最小动作 |
|---|---|---|
| widget 1.0.0 | package-lock.json 与 node_modules/widget/package.json 均声明版本 1.0.0、MIT；node_modules/widget/LICENSE 包含完整 MIT 文本及 copyright | THIRD_PARTY_NOTICES.md 已列 widget 1.0.0 并包含对应许可原文。已检查范围内未发现包级义务遗漏。 |
| 内嵌 mini-lib 2.0.0 | node_modules/widget/ThirdPartyNotices.txt 明确列出 mini-lib 2.0.0、MIT、Mini Authors，并指向 lib/bundle.js.LICENSE；后者含完整 MIT 文本及 Copyright (c) 2026 Mini Authors | 包级 widget 的 MIT 不能替代 Mini Authors 的版权声明，但这份独立原文已经存在。附加索引未列 mini-lib，并不意味着原文未交付。若希望索引完整，可增加组件条目与原文路径。 |
| 分发边界 | README.md 声明发布源码及完整 node_modules/widget 目录，包括原始许可文件；THIRD_PARTY_NOTICES.md 只是附加索引，依赖文件不删。publish.json 的 files 包含 node_modules/widget/** | 保留原始声明的发布方案支持无需强制修改索引的判断。不能把两个组件均为 MIT 当作无需保留两个版权主体的理由。 |

MIT 要求软件副本或实质部分包含版权和许可声明，并不要求把所有声明合并到指定名称的单一索引中。[OSI MIT 原文](https://opensource.org/license/mit)。将该条款与本地交付配置结合，本报告推断：只要原始文件按计划随完整组件交付，mini-lib 的条件已有载体满足。

## 未确认项与建议

- 最终压缩包／安装包是否真的包含 ThirdPartyNotices.txt 与 lib/bundle.js.LICENSE？尚无最终产物可核验；发布前按文件清单检查即可。
- 未获得上游实际源码，未证明内嵌组件未被修改或不存在额外组件。当前结论限于本地可见声明，不能扩展到任意打包或精简后的产物。
- 如未来只交付抽取的 bundle 或删除原始许可文件，则必须另保留 mini-lib 的版权及许可原文；届时需要修改分发内容。

## 范围与方法

使用 `skills/license-check/SKILL.md`、其 `references/review-guide.md` 和 `references/report-format.md`；先执行 `python3 scripts/collect.py --help`，再以绝对路径执行 `--project`。只读读取目标工程的源码、元数据、说明和发布配置；未安装依赖、未运行工程代码、未修改工程。未读取 Skill 仓库的 tests、README 或评测产物，也未读取 without-skill。

取证生态为 npm，package-lock.json v3，模式为 lock_and_installed，实际受检安装包 1 个：widget 1.0.0；锁定版本与 node_modules/widget/package.json 一致，声明 MIT，包内 LICENSE 原文为 MIT，未发现包级声明与原文不一致。没有 Python 取证 scope，本报告不证明其他生态或已安装 Python 环境与声明／锁文件一致。本地多余 npm 包不自动视为发布依赖；此次收集未报告多余包。

收集器 schema_version=1，退出码 0、status=collected、issues=[]，表示受支持范围取证完成，不表示法律审查通过。全部 1 个受检包已在报告处理，无未交代 issues。默认跳过 .cache、.git、.venv、__pycache__、node_modules、venv 的工程许可证扫描；node_modules 的受检依赖另行读取。

局限：未验证最终发布产物、外部二进制及资源清单，文本收集不等于识别所有源码许可头。没有精确上游版本的远程包授权核验；widget 的结论依赖提供的本地版本及许可原文。所有报告中的目标文件路径均相对于各自工程根目录。

