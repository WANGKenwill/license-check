# 任务 B：调用 FFmpeg 是否必须改为 GPL

## 结论

**就当前代码和已说明的发布方式，不需要把工程 MIT 许可证改成 GPL。** 本地证据支持工程通过普通命令行及视频数据接口调用用户独立安装的 FFmpeg，发布只包含源码，不打包 FFmpeg，也不链接其库。此结论不是“只要 spawn 就永远免责”，也不是对用户 FFmpeg 安装包的合规认证。

工程：tests/fixtures/evaluation/case-b。LICENSE 与 package.json 声明 MIT。

## 证据与判断

| 对象 | 本地证据 | 判断和建议 |
|---|---|---|
| FFmpeg，版本未知 | src/export.mjs 导入 node:child_process 的 spawn，调用 spawn('ffmpeg',['-f','rawvideo','-i','pipe:0','output.mp4']) | 普通命令行启动独立工具，以 rawvideo 管道和视频文件作为接口；未发现库链接或复杂内部数据结构交换。 |
| 发布内容 | README.md 明确用户自行安装 FFmpeg，仓库 release 仅含源码，工程不打包、不链接 FFmpeg 或其库 | 当前工程不承担交付 FFmpeg 二进制所产生的对应源码和许可提供义务。保持已说明的发布边界即可。最终发布产物仍未验证。 |
| widget 1.0.0／MIT | 锁文件、安装元数据与包 LICENSE 一致 | 在已检查本地证据中未发现兼容性冲突。若交付 widget 副本，保留其版权与许可原文；只发布本工程源码且不复制 widget 时，不要求为尚未交付的 widget 副本提供原文。[MIT 条款](https://opensource.org/license/mit) |

FSF FAQ 说明判断独立程序还是组合程序要看通信机制与通信语义，普通管道和命令行通常用于独立程序，紧密交换内部复杂结构可能导致不同结论。[GNU 官方 FAQ](https://www.gnu.org/licenses/gpl-faq.en.html#MereAggregation)。本报告依据官方搜索摘要与本地源代码作上述推断；FAQ 正文抓取超时，未伪称完整页面核验。

FFmpeg 官方说明其基础授权为 LGPL 2.1-or-later，启用特定 GPL 部分会令 FFmpeg 适用 GPL；不能只凭程序名称认定实际二进制是 GPL。[FFmpeg 官方法律说明](https://ffmpeg.org/legal.html)。官方关于 FFmpeg 库链接的检查清单也不能机械套用到当前独立工具调用。

## 适用条件、变化场景与未确认项

- 当前源码及 README 支持结论；尚未查看最终 release，发布前确认没有自动下载、内嵌或交付 FFmpeg／FFmpeg 库。
- FFmpeg 实际版本、构建选项和内嵌库未知。当前不交付它，因此不阻断此次“是否必须改工程许可证”的回答，也不能认定该 FFmpeg 本身全部合规。
- 如果改为捆绑二进制：核对该精确版本、构建配置、外部库、许可证原文、是否修改以及对应源码／许可提供方案；捆绑不自动等于整个应用改 GPL，需要重新判断组合关系。
- 如果改为库链接、复制 FFmpeg 源码或紧密交换内部结构：重新评估相应 LGPL/GPL 条款和组合程序义务，当前判断不可沿用。
- 待确认问题：最终发布包是否严格保持“仅源码、不含 FFmpeg”的现有说明？按评测要求不请求人工答案，保留为最终产物核验项。

## 范围与方法

使用 `skills/license-check/SKILL.md`、其 `references/review-guide.md` 和 `references/report-format.md`；先执行 `python3 scripts/collect.py --help`，再以绝对路径执行 `--project`。只读读取目标工程的源码、元数据、说明和发布配置；未安装依赖、未运行工程代码、未修改工程。未读取 Skill 仓库的 tests、README 或评测产物，也未读取 without-skill。

取证生态为 npm，package-lock.json v3，模式为 lock_and_installed，实际受检安装包 1 个：widget 1.0.0；锁定版本与 node_modules/widget/package.json 一致，声明 MIT，包内 LICENSE 原文为 MIT，未发现包级声明与原文不一致。没有 Python 取证 scope，本报告不证明其他生态或已安装 Python 环境与声明／锁文件一致。本地多余 npm 包不自动视为发布依赖；此次收集未报告多余包。

收集器 schema_version=1，退出码 0、status=collected、issues=[]，表示受支持范围取证完成，不表示法律审查通过。全部 1 个受检包已在报告处理，无未交代 issues。默认跳过 .cache、.git、.venv、__pycache__、node_modules、venv 的工程许可证扫描；node_modules 的受检依赖另行读取。

局限：未验证最终发布产物、外部二进制及资源清单，文本收集不等于识别所有源码许可头。没有精确上游版本的远程包授权核验；widget 的结论依赖提供的本地版本及许可原文。所有报告中的目标文件路径均相对于各自工程根目录。

