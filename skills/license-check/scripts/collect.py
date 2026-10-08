#!/usr/bin/env python3
"""Read local dependency license evidence without executing project code."""
import argparse
import csv
import email.policy
import json
import os
import re
import sys
from email.parser import Parser
from pathlib import Path, PurePosixPath

LICENSE_NAME = re.compile(r'^(?:licen[cs]e|copying|notice)(?:[._-].*)?$|^thirdpartynotices\.txt$|\.license$', re.I)
EXCLUDED = {'.git', '.cache', 'node_modules', '.venv', 'venv', '__pycache__'}


class Collector:
    def __init__(self, project):
        self.project = project
        self.packages = []
        self.issues = []
        self.scopes = []

    def issue(self, code, path, message):
        self.issues.append({'code': code, 'path': str(path), 'message': message})

    def safe(self, path, root):
        path = Path(os.path.abspath(path))
        root = Path(os.path.abspath(root))
        if not path.is_relative_to(root):
            self.issue('outside_scope', path, '路径越过扫描范围')
            return False
        for part in [root, *[root.joinpath(*path.relative_to(root).parts[:i])
                             for i in range(1, len(path.relative_to(root).parts) + 1)]]:
            if part.is_symlink():
                self.issue('symlink_skipped', part, '符号链接未读取')
                return False
        return True

    def read(self, path, root):
        path = Path(os.path.abspath(path))
        if not self.safe(path, root):
            return None
        try:
            return path.read_text(encoding='utf-8')
        except (OSError, UnicodeError) as error:
            self.issue('read_failed', path, str(error))
            return None

    def load_json(self, path, root):
        value = self.read(path, root)
        if value is None:
            return None
        try:
            result = json.loads(value)
            if not isinstance(result, dict):
                raise ValueError('需要 JSON 对象')
            return result
        except (ValueError, TypeError) as error:
            self.issue('invalid_metadata', path, str(error))
            return None

    def walk(self, directory, root, excluded=()):
        if not self.safe(directory, root):
            return
        def onerror(error):
            self.issue('read_failed', error.filename, str(error))
        for current, dirs, files in os.walk(directory, followlinks=False, onerror=onerror):
            base = Path(current)
            dirs[:] = sorted(d for d in dirs if d not in excluded and self.safe(base / d, root))
            for name in sorted(files):
                yield base / name

    def texts(self, directory, root, excluded=()):
        evidence = []
        for path in self.walk(directory, root, excluded):
            if LICENSE_NAME.search(path.name):
                content = self.read(path, root)
                if content is not None:
                    evidence.append({'path': str(path), 'text': content})
        return evidence

    def package(self, ecosystem, name, version, path, source, declared, files, **extra):
        item = {'ecosystem': ecosystem, 'name': name, 'version': version,
                'path': str(path), 'source': str(source), 'declared_license': declared,
                'license_files': sorted(files, key=lambda f: f['path']), **extra}
        self.packages.append(item)
        if not declared:
            self.issue('missing_license_metadata', source, '缺少包级许可声明；需要核对文本')
        if not files:
            self.issue('missing_license_text', path, '未收集到许可文本；元数据不足以完成取证')

    def npm_inventory(self, directory):
        if not directory.exists() and not directory.is_symlink():
            return set()
        if not self.safe(directory, self.project):
            return set()
        try:
            entries = sorted(directory.iterdir())
        except OSError as error:
            self.issue('read_failed', directory, str(error))
            return set()
        found = set()
        for entry in entries:
            if entry.name.startswith('.'):
                continue
            if not self.safe(entry, self.project):
                continue
            if entry.name.startswith('@') and entry.is_dir():
                found.update(self.npm_inventory(entry))
            elif entry.is_dir():
                found.add(entry.relative_to(self.project).as_posix())
                found.update(self.npm_inventory(entry / 'node_modules'))
        return found

    def npm(self):
        lock_path = self.project / 'package-lock.json'
        lock = self.load_json(lock_path, self.project)
        self.scopes.append({'ecosystem': 'npm', 'mode': 'lock_and_installed', 'source': str(lock_path)})
        if lock is None:
            return
        entries = lock.get('packages')
        if lock.get('lockfileVersion') not in (2, 3) or not isinstance(entries, dict):
            self.issue('unsupported_lockfile', lock_path, '仅支持含 packages 的 npm 锁文件 v2/v3')
            return
        expected = set()
        for relative, entry in sorted(entries.items()):
            if not relative:
                continue
            parts = PurePosixPath(relative).parts
            if not isinstance(entry, dict) or '..' in parts or PurePosixPath(relative).is_absolute():
                self.issue('unsupported_dependency', lock_path, f'无效锁定条目：{relative}')
                continue
            if 'node_modules' not in parts or parts[0] != 'node_modules' or entry.get('link'):
                self.issue('unsupported_dependency', lock_path, f'暂不支持 workspace/link/本地目录：{relative}')
                continue
            expected.add(relative)
            path = self.project / relative
            if not self.safe(path, self.project):
                continue
            if not path.is_dir():
                self.issue('missing_package', path, '锁定依赖未安装')
                continue
            metadata = self.load_json(path / 'package.json', self.project)
            if metadata is None:
                continue
            version = metadata.get('version')
            if not entry.get('version') or version != entry['version']:
                self.issue('version_mismatch', path, f"锁定版本 {entry.get('version')}，本地版本 {version}")
            name = metadata.get('name')
            if not isinstance(name, str) or not name or not isinstance(version, str):
                self.issue('invalid_metadata', path / 'package.json', '缺少有效包名或版本')
            self.package('npm', name, version, path, path / 'package.json',
                         metadata.get('license'), self.texts(path, self.project, {'node_modules'}),
                         locked_version=entry.get('version'), lock_path=relative,
                         declared_dependencies=metadata.get('dependencies', {}),
                         development=entry.get('dev', False), optional=entry.get('optional', False))
        for relative in sorted(self.npm_inventory(self.project / 'node_modules') - expected):
            self.issue('extra_package', self.project / relative, '本地包不在受支持的锁定条目中；不认定为发布依赖')

    def python(self, environment):
        self.scopes.append({'ecosystem': 'python', 'mode': 'installed_environment',
                            'source': str(environment), 'lock_consistency_verified': False})
        self.issue('python_lock_unverified', environment, '仅检查已安装环境，未验证与声明或锁文件一致')
        if not self.safe(environment, environment):
            return
        if not environment.is_dir():
            self.issue('missing_environment', environment, 'Python 环境不存在')
            return
        sites = []
        def onerror(error):
            self.issue('read_failed', error.filename, str(error))
        for current, dirs, _ in os.walk(environment, followlinks=False, onerror=onerror):
            base = Path(current)
            if base.name == 'site-packages':
                sites.append(base)
                dirs[:] = []
            else:
                dirs[:] = sorted(d for d in dirs if d not in {'bin', 'Scripts', 'include', '__pycache__'}
                                 and self.safe(base / d, environment))
        if not sites:
            self.issue('missing_site_packages', environment, '未找到 site-packages')
        for site in sorted(sites):
            try:
                entries = sorted(site.iterdir())
            except OSError as error:
                self.issue('read_failed', site, str(error))
                continue
            for info in entries:
                if not self.safe(info, environment):
                    continue
                if info.name.endswith('.egg-info') or info.suffix in {'.egg', '.pth', '.egg-link'}:
                    self.issue('unsupported_python_entry', info, '未解析旧式或路径注入安装；文件未执行')
                if not info.name.endswith('.dist-info') or not info.is_dir():
                    continue
                source = info / 'METADATA'
                raw = self.read(source, environment)
                if raw is None:
                    continue
                meta = Parser(policy=email.policy.default).parsestr(raw)
                name, version = meta.get('Name'), meta.get('Version')
                if not name or not version:
                    self.issue('invalid_metadata', source, '缺少包名或版本')
                files = {f['path']: f for f in self.texts(info, environment)}
                license_paths = list(meta.get_all('License-File', []))
                for relative in license_paths:
                    if PurePosixPath(relative).is_absolute() or '..' in PurePosixPath(relative).parts:
                        self.issue('invalid_license_path', source, f'无效 License-File：{relative}')
                        continue
                    path = info / 'licenses' / relative
                    content = self.read(path, environment)
                    if content is not None:
                        files[str(path)] = {'path': str(path), 'text': content}
                record = info / 'RECORD'
                if record.exists() or record.is_symlink():
                    content = self.read(record, environment)
                    if content is not None:
                        try:
                            for row in csv.reader(content.splitlines(), strict=True):
                                if row and LICENSE_NAME.search(PurePosixPath(row[0]).name):
                                    path = Path(os.path.abspath(site / row[0]))
                                    text = self.read(path, environment)
                                    if text is not None:
                                        files[str(path)] = {'path': str(path), 'text': text}
                        except csv.Error as error:
                            self.issue('invalid_metadata', record, str(error))
                else:
                    self.issue('missing_record', record, '无法核对包文件中的许可文本')
                classifiers = [s for s in meta.get_all('Classifier', []) if s.startswith('License ::')]
                expression, legacy = meta.get('License-Expression'), meta.get('License')
                declared = expression or (legacy if legacy and legacy != 'UNKNOWN' else None) or classifiers or None
                direct_url = info / 'direct_url.json'
                if direct_url.exists() or direct_url.is_symlink():
                    data = self.load_json(direct_url, environment)
                    if data and isinstance(data.get('dir_info'), dict) and data['dir_info'].get('editable'):
                        self.issue('editable_install', direct_url, '可编辑安装的源码未纳入环境取证')
                self.package('python', name, version, info, source, declared, list(files.values()),
                             license_expression=expression, legacy_license=legacy,
                             license_classifiers=classifiers, declared_dependencies=meta.get_all('Requires-Dist', []))

    def run(self, environment=None):
        project_files = self.texts(self.project, self.project, EXCLUDED)
        if (self.project / 'package-lock.json').exists() or (self.project / 'package-lock.json').is_symlink():
            self.npm()
        elif (self.project / 'package.json').exists():
            self.issue('missing_lockfile', self.project, 'npm 缺少受支持的锁文件')
        for filename in ('yarn.lock', 'pnpm-lock.yaml', 'npm-shrinkwrap.json', 'uv.lock', 'poetry.lock',
                         'Pipfile.lock', 'Cargo.lock', 'go.mod'):
            if (self.project / filename).exists():
                self.issue('unsupported_manifest', self.project / filename, '首版未验证此依赖格式')
        if environment is None:
            for name in ('.venv', 'venv'):
                candidate = self.project / name
                if candidate.exists() or candidate.is_symlink():
                    environment = candidate
                    break
        if environment is not None:
            self.python(environment)
        elif any((self.project / name).exists() for name in ('pyproject.toml', 'requirements.txt', 'setup.py', 'setup.cfg', 'Pipfile')):
            self.issue('missing_environment', self.project, 'Python 工程没有可读取的虚拟环境')
        if not self.scopes:
            self.issue('no_supported_scope', self.project, '未发现受支持的依赖取证范围')
        issues = sorted({json.dumps(i, ensure_ascii=False, sort_keys=True): i for i in self.issues}.values(),
                        key=lambda i: (i['path'], i['code'], i['message']))
        return {'schema_version': 1, 'project': str(self.project),
                'status': 'incomplete' if issues else 'collected', 'scopes': self.scopes,
                'limitations': ['不验证法律兼容性', '未验证最终发布产物、外部二进制及资源清单',
                                '文本收集不等于识别所有源码中的许可头'],
                'project_license_files': project_files, 'excluded_project_directories': sorted(EXCLUDED),
                'packages': sorted(self.packages, key=lambda p: (p['ecosystem'], p['path'])), 'issues': issues}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True, type=Path, help='目标工程目录（只读）')
    parser.add_argument('--python-env', type=Path, help='显式指定虚拟环境，直接读取元数据')
    args = parser.parse_args()
    project = Path(os.path.abspath(args.project))
    if not project.is_dir() or project.is_symlink():
        print('工程路径必须是现有的非符号链接目录', file=sys.stderr)
        return 2
    collector = Collector(project)
    if not collector.safe(project, Path(project.anchor)):
        print('工程路径经过符号链接', file=sys.stderr)
        return 2
    environment = Path(os.path.abspath(args.python_env)) if args.python_env else None
    if environment and not collector.safe(environment, Path(environment.anchor)):
        print('环境路径经过符号链接', file=sys.stderr)
        return 2
    try:
        result = collector.run(environment)
    except (OSError, ValueError, TypeError) as error:
        print(f'取证执行失败：{error}', file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    print(f"已收集 {len(result['packages'])} 个包，{len(result['issues'])} 个未完整取证项", file=sys.stderr)
    return 1 if result['status'] == 'incomplete' else 0


if __name__ == '__main__':
    sys.exit(main())
