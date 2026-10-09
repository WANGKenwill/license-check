# Third-party notices review — case-a

## Conclusion and scope

The additional notice index `THIRD_PARTY_NOTICES.md` omits embedded **mini-lib 2.0.0**, but the local release documentation says the complete `node_modules/widget` directory, including its original license files, is distributed. On that stated distribution model, the index omission alone does not establish that required license or copyright notices are missing from the release. Preserve the original files and add mini-lib to the index for completeness. No license conflict is identified in the inspected local evidence; this is not a verified legal-compatibility conclusion or confirmation of the actual release contents.

The project declares MIT in `package.json`, supported by `LICENSE`. `README.md` describes distribution of source and the complete widget directory, with `THIRD_PARTY_NOTICES.md` serving as an additional index. `publish.json` includes `node_modules/widget/**`. Dependency modifications are not established by these files.

## Evidence and findings

| Component | Local evidence | Assessment and minimal action |
| --- | --- | --- |
| widget 1.0.0 | `package.json` and `package-lock.json` declare the dependency; `node_modules/widget/package.json` agrees on version and MIT. `node_modules/widget/LICENSE` contains MIT terms. `THIRD_PARTY_NOTICES.md` reproduces its copyright and permission notice. | No package-level notice omission is apparent locally. Retain its original license when shipping the documented directory. |
| mini-lib 2.0.0 embedded in widget | `node_modules/widget/ThirdPartyNotices.txt` identifies mini-lib, version 2.0.0, MIT, and directs readers to `lib/bundle.js.LICENSE`. `node_modules/widget/lib/bundle.js.LICENSE` supplies the full local MIT text. `THIRD_PARTY_NOTICES.md` lists only widget. | Confirmed omission from the additional index. The documented release preserves the original embedded notices, so local evidence does not establish a distribution notice breach. Add a mini-lib entry pointing to the original license; verify those original files survive packaging. |

Exact copyright line from mini-lib's local license file, `node_modules/widget/lib/bundle.js.LICENSE`:

> Copyright (c) 2026 Mini Authors

The embedded-component summary uses a shorter copyright form without the year. Use the full license file above for the exact excerpt. Widget's package-level MIT declaration does not replace evidence for its embedded component.

The inspected MIT texts state that the copyright and permission notices must accompany copies or substantial portions. This assessment is based on those local texts and the stated release conditions; no official upstream terms were independently verified.

## Collection completeness and unresolved items

- Collector: Python standard-library script `collect.py`, after checking `--help`, run read-only with the absolute project path. Exit code **0**, `status=collected`, schema version 1, **1 npm package** collected, **0 issues**. This indicates evidence collection success, not legal approval. The embedded mini-lib was reviewed separately through widget's collected notice files; it is not a second lockfile package.
- npm scope: `package-lock.json` version 3, lock-and-installed mode. The single locked installed package has matching local version metadata. No Python environment is present in the supplied fixture, and no Python package review is asserted. Installed Python environments, if added, would require separate comparison against project declarations.
- Final release archive was not available. `README.md` and `publish.json` express the intended distribution, but actual inclusion of `node_modules/widget/ThirdPartyNotices.txt` and `node_modules/widget/lib/bundle.js.LICENSE` remains unverified. Inspect the finished archive before claiming release compliance.
- Exact-version upstream provenance and authoritative terms for widget 1.0.0 and mini-lib 2.0.0 remain unresolved; these are synthetic local evidence files. Verify upstream if a legal compatibility or provenance conclusion is needed.
- Dependency modifications, actual runtime use, copied source, all source license headers, external binaries, and resource contents are not fully established or covered by the collector. No claim of exhaustive compliance is made for those areas.

No dependency installation, project-code execution, notice generation, or project modification was performed.
