[中文](README.md) | English

# license-check

An open-source license review Skill for agents: collect local dependency license evidence and analyze missing notices and unresolved items in the context of how software is used and distributed.

## Installation

Collection requires **Python 3.11+**, with no third-party Python dependencies. The installer also requires Node.js and npm.

Run from the project directory you want to review, then select your agent:

```bash
npx skills add WANGKenwill/license-check --skill license-check
```

Add `--global` to install into your user directory. Only `skills/license-check/` is installed, excluding tests and development documentation.

Manual installation: download or clone the repository and copy the entire `skills/license-check/` directory into your client's skill directory.

## Usage

After installation, ask your agent:

> Use license-check to review this project. I plan to publish source code without bundling external tool binaries. List missing notices, evidence, and unresolved items.

Describe your actual distribution method, such as source code, an installer, or a container. Reports appear in the conversation by default; specify a destination to save one.

## Supported scope

- npm: compare package-lock.json v2/v3 with installed packages and collect bundled third-party notices.
- Python: read metadata from `.venv`, `venv`, or a specified environment; lockfile consistency is not yet verified.
- The collection script is read-only, uses no network, installs no dependencies, and executes no project code.

Final release artifacts, external binaries, and all source license headers are not covered. Completed collection is not comprehensive compliance approval.

## Development and feedback

Run tests from the repository root:

```bash
python3 -m unittest discover -s tests -v
```

[Evaluation records and examples (Chinese)](tests/evaluation.md) · [Report an issue](https://github.com/WANGKenwill/license-check/issues)

Provide a redacted minimal example when reporting issues; avoid uploading entire scan JSON files or private code. Verified on macOS and Ubuntu CI; Windows has not been verified.

[MIT License](LICENSE) · Copyright (c) 2026 WANGKenwill
