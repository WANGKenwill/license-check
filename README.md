# license-check

用于 Agent 的开源许可证检查 Skill：Python 脚本收集本地证据，Agent 结合使用和分发方式分析。支持 npm package-lock.json v2/v3 与已安装包对照，以及 Python 虚拟环境元数据检查。

## 安装

运行取证脚本需要 **Python 3.11+**，无第三方 Python 运行依赖。可安装内容在 `skills/license-check/`；测试、评测报告和开发环境不需要安装。

### 使用 Skills 安装器

需要 Node.js 和 npm。在仓库根目录安装本地 Skill：

```bash
npx skills add ./skills/license-check --skill license-check
```

安装器可选择目标 Agent，默认安装到当前项目；加 `--global` 可安装到用户目录。支持的客户端和选项见 [Skills 安装器文档](https://github.com/vercel-labs/skills)。

从 [GitHub 仓库](https://github.com/WANGKenwill/license-check) 安装：

```bash
npx skills add WANGKenwill/license-check --skill license-check
```

### 手动安装

不使用 Node.js 安装器时，下载或克隆仓库，将 `skills/license-check/` 整个目录复制到客户端支持的技能目录，目标目录名保持 `license-check`。只复制该目录，无需复制整个仓库。客户端安装位置及刷新方式以其文档为准。

## 使用

向 Agent 提出：

> 使用 license-check 检查这个工程的开源许可，列出声明遗漏和未确认项。

也可直接运行仓库中的取证脚本：

```bash
python3 skills/license-check/scripts/collect.py --project /absolute/path/project
python3 skills/license-check/scripts/collect.py --project /absolute/path/project --python-env /absolute/path/environment
```

以上相对脚本路径适用于仓库根目录；从其他目录运行时使用脚本的绝对路径。安装后的脚本位于 Skill 目录内的 `scripts/collect.py`。

JSON 输出至 stdout，诊断至 stderr。退出码 0 表示取证完成，1 表示不完整，2 表示执行失败；不代表兼容性认证。Python 优先检查 `.venv`，不存在时检查 `venv`，不运行环境解释器。Python 环境与项目声明的一致性未验证，结果会标记不完整。

默认只读、不联网、不安装项目依赖、不执行项目代码。符号链接跳过并记录。支持收集包内第三方声明，但不识别所有源码许可头，也未验证最终发布产物、外部工具和资源清单。ScanCode、其他锁文件、声明生成暂未接入。

### 完整示例

以下使用仓库内的合成案例 A：工程分发源码和完整的 `widget` 目录，附加声明索引只列出 `widget`，包内还包含 `mini-lib` 的独立声明。

向 Agent 提出：

> 使用 license-check 检查 tests/fixtures/evaluation/case-a 的第三方声明是否遗漏，结合 README.md 和 publish.json 中的分发方式，给出证据、结论及未确认项。

也可在仓库根目录运行取证：

```bash
python3 skills/license-check/scripts/collect.py --project "$PWD/tests/fixtures/evaluation/case-a"
```

关键输出（节选；证据文件路径在实际 JSON 中为绝对路径）：

```json
{
  "schema_version": 1,
  "status": "collected",
  "issues": []
}
```

收集到 `widget 1.0.0` 的包级 MIT 声明，以及包内的 `LICENSE`、`ThirdPartyNotices.txt` 和 `lib/bundle.js.LICENSE`；后两个文件提供 `mini-lib 2.0.0` 的独立许可证据。

预期报告要点：

- **结论：** 按案例声明的分发方式，原始版权和许可文件随完整目录交付，附加索引少列 `mini-lib` 不直接构成已确认的分发义务遗漏；可选补全索引。
- **证据：** `package-lock.json` 与已安装包版本一致；`ThirdPartyNotices.txt` 列出内嵌组件，并指向其完整许可原文；README.md 和 publish.json 说明保留这些文件。
- **未确认项：** 尚未检查最终发布归档是否确实保留上述文件，也未核对真实上游源码；不能把 `collected` 扩大解释为全面合规通过。

完整分析见 [案例 A 报告](tests/evaluation-reports/with-skill/a.md)。这是合成案例的报告示例，Agent 的措辞可能不同。

## 仓库结构

```text
skills/license-check/  # 完整、可独立安装的 Skill
  SKILL.md
  LICENSE
  scripts/
  references/
tests/                 # 自动测试、固定样例和评测记录
README.md              # 安装、使用与开发说明
LICENSE                # 仓库授权
```

Skill 内的脚本直接作为源码维护，安装和发布使用同一份文件。发布 ZIP 时只包含 `skills/license-check/` 的安装内容；无需另外维护产物仓库。

## 开发验证

在仓库根目录运行：

```bash
python3 -m unittest discover -s tests -v
```

测试使用临时合成工程，包含将安装目录复制到独立位置后运行的检查。已有 [评测记录](tests/evaluation.md) 和 [评测用例](tests/evals.json) 可供复测；评测报告中的路径为仓库相对路径。

GitHub Actions 在每次推送和 Pull Request 时使用 Python 3.11、3.14 运行同一组测试，无需安装第三方 Python 依赖。

开发用 `.venv` 和缓存不提交、不随 Skill 安装。PyYAML 仅供已有 Skill 校验工具使用，不是取证脚本的依赖。

项目采用 MIT。根目录与 Skill 安装目录均提供同一份 LICENSE，修改授权时应同步更新；自动测试检查两者一致。
