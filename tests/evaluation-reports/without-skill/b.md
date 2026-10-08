# 任务 B：调用 FFmpeg 是否必须改为 GPL

审查日期：2026-10-04。范围：case-b 全部现有文件。仅静态只读检查；不安装依赖、不执行工程或 FFmpeg、不修改工程，未使用许可证审查 Skill。

## 结论

**按当前证据，不需要把本工程的 MIT 许可证改成 GPL。** 工程使用 child_process.spawn 启动用户独立安装的 FFmpeg，通过普通命令行与标准输入传入原始视频；没有链接 FFmpeg 库，也不随发布物携带 FFmpeg。仅调用外部命令不能直接推出整个工程必须改许可证。

这个结论只针对当前调用和发布方式，不等于对任何 FFmpeg 构建、任何未来打包方式均已合规的保证。

## 本地证据

| 文件及行号（相对 case-b） | 内容与意义 |
| --- | --- |
| src/export.mjs:1 | 导入 node:child_process 的 spawn。 |
| src/export.mjs:2 | spawn('ffmpeg', ['-f','rawvideo','-i','pipe:0','output.mp4'])：独立进程、通用命令行、媒体数据输入。没有共享地址空间函数调用或 FFmpeg 库导入。 |
| README.md:1 | 用户独立安装 FFmpeg；仓库发布仅含源码；工程不打包、不链接 FFmpeg 或其库。 |
| package.json:1；package-lock.json:1 | 项目 MIT，唯一列明依赖 widget 1.0.0，MIT；没有 FFmpeg 二进制依赖包。 |
| LICENSE:1–21 | 本工程 MIT 许可全文。 |
| node_modules/widget/LICENSE:1–21 | widget MIT 全文存在。 |

完整目录检查没有找到 FFmpeg 二进制、libav 库、FFmpeg 构建配置或额外链接代码。该阴性证据只覆盖给定目录；README 对发布方式的明确说明是判断的重要依据。

## 条款依据与推理

FFmpeg 官方说明，其默认许可为 LGPL 2.1 或后续版本，启用部分 GPL 组件后整个 FFmpeg 才采用 GPL。因此，不能把“FFmpeg”这个名称一律视为 GPL 构建。[FFmpeg 官方许可说明](https://ffmpeg.org/legal.html)。

GNU FAQ 认为命令行和管道通常是独立程序之间的通信方式，同时提醒要结合交换信息的语义判断，紧密交换内部复杂结构仍可能构成组合程序。[GNU FAQ：聚合与组合](https://www.gnu.org/licenses/gpl-faq.en.html#MereAggregation)。

本例仅传递普通 rawvideo 媒体数据与输出路径，结合独立安装、无链接、无随包分发的明确说明，可合理判断为独立程序交互。这是结合工程事实的推断，并非“只要 spawn 就绝对豁免”的规则。当前也没有本工程分发 FFmpeg 二进制而触发其对应分发义务的证据。

## 建议动作与未确认项

- 保留项目 MIT，无需为本问题更改 LICENSE/package.json。
- 继续保持并保留 README 中独立安装及不打包、不链接的描述，发布实现应与其一致。
- 如未来随应用、安装器、镜像或自动下载流程提供 FFmpeg，需要重新确认实际版本、构建选项、第三方编解码库及相应声明/源码义务；随包分发本身也不自动等同于整个工程必须 GPL。
- 待确认问题：最终发布物是否确实只含仓库源码，是否有目录之外的安装器或下载渠道由项目提供 FFmpeg？目前没有相反证据，按 README 事实作结论。用户安装的 FFmpeg 具体构建不在本次项目改许可证问题的已知范围内。
- widget 的源目录有 MIT 全文；本任务不是全量发布审批，未验证其最终发布材料。

## 工具与局限

使用 exec_command 的 ls、rg --files -uuu 和 Python 标准库静态读取文本并加行号；使用 web 访问 FFmpeg、GNU 官方许可资料。GNU FAQ 原始地址两次抓取失败后，使用官方英文页面的搜索索引内容支持结论；没有使用非官方法律解释作为依据。未运行构建、检查系统 FFmpeg 或下载二进制。未读取主工作区、许可证审查 Skill 或 with-skill 目录。
