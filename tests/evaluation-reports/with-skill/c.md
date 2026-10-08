# 任务 C：发布前许可证是否全部通过

## 结论

**不能宣布“许可证都通过了”。** 受检 npm 包 widget 1.0.0 的本地 MIT 证据已完成，未发现已确认冲突；但源码实际调用 FFmpeg，而发布形态、FFmpeg 是否随包交付、实际构建许可及最终产物均未知。结论应为“本地 npm 范围未发现冲突，发布审查仍有未确认项”，而非全面通过，也不能直接认定必须改 GPL。

工程：tests/fixtures/evaluation/case-c。LICENSE 与 package.json 声明 MIT。README.md 只称其为视频应用，release 正在准备，没有明确分发方式。

## 发现与证据

| 对象 | 本地证据 | 结论和最小动作 |
|---|---|---|
| widget 1.0.0，MIT | package-lock.json、node_modules/widget/package.json、node_modules/widget/LICENSE 的版本与许可一致 | 未发现已确认的兼容性冲突。本地有许可文件不证明发布物保留它；如交付该包或实质部分，保留版权和许可原文。[MIT 原文](https://opensource.org/license/mit)。 |
| FFmpeg，版本未知 | src/export.mjs 调用 spawn('ffmpeg',['-i','input.mov','output.mp4']) | 锁文件无法覆盖外部 FFmpeg。当前代码显示普通命令行与文件接口，未见库链接，但不能推断工具一定由用户自装或发布不会捆绑。需补充分发事实。 |
| 发布内容 | README.md 仅说发布准备中；未见明确发布配置、产物或清单 | 未确认源码包、应用安装包、容器或服务的具体形态，以及外部二进制、资源和声明是否交付。不能以 collector issues=[] 作为发布通过证据。 |

FFmpeg 官方说明基础许可为 LGPL 2.1-or-later，部分启用组件使 FFmpeg 改为 GPL。[官方法律说明](https://ffmpeg.org/legal.html)。实际结果还受外部库与构建选项影响，启用 --enable-nonfree 可能形成不可再分发的二进制。[官方 License 文档](https://ffmpeg.org/doxygen/trunk/md_LICENSE.html)。这两项是通用资料，不是对本工程未知精确版本二进制的核验。

## 必須保留的问题与分支判断

按评测要求不等待人工澄清，以下均保持未确认：

1. 发布交付什么：源码、打包 JS、应用安装包、容器还是仅网络服务？是否交付 widget 或其他构建产物、字体、图片、音视频或复制的第三方源码？
2. FFmpeg 由用户独立安装，还是安装程序／发布包／容器带入或下载？有没有 FFmpeg 库链接、复制源码、修改或额外通信协议？
3. 如果交付 FFmpeg：精确版本、来源、配置选项（含 --enable-gpl、--enable-version3、--enable-nonfree）、外部库清单及修改记录是什么？提供哪份许可证、声明与对应源码，怎样满足该实际许可的分发要求？
4. 最终产物是否保留 widget 和所有实际交付第三方组件的许可、版权声明及必要修改标记？有无可审核的最终文件清单？

最小建议：先补齐实际发布清单和上述 FFmpeg 证据，再按实际许可证逐项核验；无需先行安装、执行工程或自动更换工程许可证。

- 如果只发布工程源码，FFmpeg 由用户自行安装，且保持现在的普通文件／命令行接口：没有证据要求因此把 MIT 工程改成 GPL。独立程序判断仍需结合通信语义。[GNU 官方 FAQ](https://www.gnu.org/licenses/gpl-faq.en.html#MereAggregation)。
- 如果发布包包含 FFmpeg：须核验该二进制的具体授权、对应源码与声明义务，不可套用上一分支；捆绑也不自动使应用改 GPL。
- 如果库链接、复制源码或形成紧密组合：按照适用 LGPL/GPL 和组合关系重新判断。本报告未确认此种事实。

GNU FAQ 正文抓取超时，其概括来自官方搜索摘要。当前没有精确 FFmpeg 版本可核对上游文件，不能以最新文档替代版本级审查。

## 范围与方法

使用 `skills/license-check/SKILL.md`、其 `references/review-guide.md` 和 `references/report-format.md`；先执行 `python3 scripts/collect.py --help`，再以绝对路径执行 `--project`。只读读取目标工程的源码、元数据、说明和发布配置；未安装依赖、未运行工程代码、未修改工程。未读取 Skill 仓库的 tests、README 或评测产物，也未读取 without-skill。

取证生态为 npm，package-lock.json v3，模式为 lock_and_installed，实际受检安装包 1 个：widget 1.0.0；锁定版本与 node_modules/widget/package.json 一致，声明 MIT，包内 LICENSE 原文为 MIT，未发现包级声明与原文不一致。没有 Python 取证 scope，本报告不证明其他生态或已安装 Python 环境与声明／锁文件一致。本地多余 npm 包不自动视为发布依赖；此次收集未报告多余包。

收集器 schema_version=1，退出码 0、status=collected、issues=[]，表示受支持范围取证完成，不表示法律审查通过。全部 1 个受检包已在报告处理，无未交代 issues。默认跳过 .cache、.git、.venv、__pycache__、node_modules、venv 的工程许可证扫描；node_modules 的受检依赖另行读取。

局限：未验证最终发布产物、外部二进制及资源清单，文本收集不等于识别所有源码许可头。没有精确上游版本的远程包授权核验；widget 的结论依赖提供的本地版本及许可原文。所有报告中的目标文件路径均相对于各自工程根目录。

