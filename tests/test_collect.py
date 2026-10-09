import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SKILL = Path(__file__).resolve().parents[1] / 'skills' / 'license-check'
SCRIPT = SKILL / 'scripts' / 'collect.py'
spec = importlib.util.spec_from_file_location('collect', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CollectTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()

    def write(self, relative, content):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        return path

    def npm(self, version=3):
        packages = {'': {}, 'node_modules/direct': {'version': '1.0'},
                    'node_modules/direct/node_modules/transitive': {'version': '2.0'}}
        self.write('package-lock.json', json.dumps({'lockfileVersion': version, 'packages': packages}))
        for name, v, path in [('direct', '1.0', 'node_modules/direct'),
                              ('transitive', '2.0', 'node_modules/direct/node_modules/transitive')]:
            self.write(path + '/package.json', json.dumps({'name': name, 'version': v, 'license': 'MIT OR Apache-2.0'}))
            self.write(path + '/LICENSE', '许可原文\n')
        return packages

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), '--project', str(self.root), *args],
                              cwd='/', capture_output=True, text=True)

    def codes(self, result):
        return {i['code'] for i in result['issues']}

    def test_nested_notices_readonly_and_deterministic(self):
        for version in (2, 3):
            self.npm(version)
            self.write('node_modules/direct/ThirdPartyNotices.txt', '内嵌组件')
            self.write('node_modules/direct/lib/deep/bundle.js.LICENSE', '其他许可')
            before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
            first, second = self.run_cli(), self.run_cli()
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(first.stdout, second.stdout)
            data = json.loads(first.stdout)
            direct = data['packages'][0]
            self.assertEqual(direct['declared_license'], 'MIT OR Apache-2.0')
            self.assertEqual(len(direct['license_files']), 3)
            self.assertEqual(len(data['packages']), 2)
            after = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
            self.assertEqual(before, after)

    def test_missing_mismatch_and_extra(self):
        self.npm()
        self.write('node_modules/direct/package.json', json.dumps({'name': 'direct', 'version': '9', 'license': 'MIT'}))
        (self.root / 'node_modules/direct/LICENSE').unlink()
        (self.root / 'node_modules/direct/node_modules/transitive/package.json').unlink()
        self.write('node_modules/extra/package.json', '{}')
        result = self.run_cli()
        self.assertEqual(result.returncode, 1)
        self.assertTrue({'version_mismatch', 'missing_license_text', 'read_failed', 'extra_package'} <= self.codes(json.loads(result.stdout)))

    def test_missing_package_and_unsupported(self):
        self.write('package-lock.json', json.dumps({'lockfileVersion': 3, 'packages': {
            'node_modules/missing': {'version': '1'}, 'node_modules/work': {'link': True},
            '../escape': {'version': '1'}}}))
        data = json.loads(self.run_cli().stdout)
        self.assertTrue({'missing_package', 'unsupported_dependency'} <= self.codes(data))
        self.write('package-lock.json', '{"lockfileVersion":1}')
        self.assertIn('unsupported_lockfile', self.codes(json.loads(self.run_cli().stdout)))

    def test_symlink_not_followed(self):
        self.npm()
        secret = self.write('outside/secret', 'DO NOT READ')
        (self.root / 'node_modules/direct/NOTICE').symlink_to(secret)
        (self.root / 'node_modules/direct/linked').symlink_to(secret.parent, target_is_directory=True)
        result = self.run_cli()
        self.assertEqual(result.returncode, 1)
        self.assertIn('symlink_skipped', self.codes(json.loads(result.stdout)))
        self.assertNotIn('DO NOT READ', result.stdout)

    def test_invalid_text_and_permission_failure(self):
        self.npm()
        license_path = self.root / 'node_modules/direct/LICENSE'
        license_path.write_bytes(b'\xff')
        self.assertIn('read_failed', self.codes(json.loads(self.run_cli().stdout)))
        original = Path.read_text
        def deny(path, *args, **kwargs):
            if path.name == 'package.json':
                raise PermissionError('denied')
            return original(path, *args, **kwargs)
        with patch.object(Path, 'read_text', deny):
            data = module.Collector(self.root).run()
        self.assertIn('read_failed', self.codes(data))

    def python_env(self, env='.venv', name='demo'):
        base = f'{env}/lib/python3.11/site-packages'
        info = f'{base}/{name}-1.dist-info'
        self.write(info + '/METADATA', f'Name: {name}\nVersion: 1\nLicense-Expression: MIT AND Apache-2.0 WITH LLVM-exception\nLicense-File: CUSTOM\nRequires-Dist: child>=2; python_version >= "3.11"\n\n')
        self.write(info + '/licenses/CUSTOM', 'custom original')
        self.write(base + f'/{name}/NOTICE', 'bundled original')
        self.write(info + '/RECORD', f'{name}/NOTICE,,\n{name}-1.dist-info/licenses/CUSTOM,,\n')
        return info

    def test_python_metadata_record_and_priority(self):
        self.python_env()
        self.python_env('venv', 'ignored')
        data = json.loads(self.run_cli().stdout)
        self.assertEqual([p['name'] for p in data['packages']], ['demo'])
        self.assertIn('python_lock_unverified', self.codes(data))
        pkg = data['packages'][0]
        self.assertEqual(len(pkg['license_files']), 2)
        self.assertEqual(pkg['license_expression'], 'MIT AND Apache-2.0 WITH LLVM-exception')
        self.assertEqual(len(pkg['declared_dependencies']), 1)
        self.assertFalse(data['scopes'][0]['lock_consistency_verified'])

    def test_python_fallback_explicit_and_old_entries(self):
        self.python_env('venv')
        self.write('venv/lib/python3.11/site-packages/load.pth', 'raise Exception("never execute")')
        data = json.loads(self.run_cli().stdout)
        self.assertIn('unsupported_python_entry', self.codes(data))
        self.assertEqual(len(data['packages']), 1)
        self.python_env('custom', 'explicit')
        data = json.loads(self.run_cli('--python-env', str(self.root / 'custom')).stdout)
        self.assertEqual([p['name'] for p in data['packages']], ['explicit'])

    def test_python_missing_metadata_and_record_escape(self):
        info = self.python_env()
        self.write(info + '/METADATA', 'Name: demo\nVersion: 1\n')
        self.write(info + '/RECORD', '../../../../../../outside/LICENSE,,\n')
        data = json.loads(self.run_cli().stdout)
        self.assertTrue({'outside_scope', 'missing_license_metadata'} <= self.codes(data))
        (self.root / info / 'METADATA').unlink()
        self.assertIn('read_failed', self.codes(json.loads(self.run_cli().stdout)))

    def test_no_scope_missing_environment_and_other_lock(self):
        self.assertEqual(self.run_cli().returncode, 1)
        self.write('pyproject.toml', '[project]\nname="sample"')
        self.write('pnpm-lock.yaml', 'lockfileVersion: 9')
        codes = self.codes(json.loads(self.run_cli().stdout))
        self.assertTrue({'missing_environment', 'unsupported_manifest', 'no_supported_scope'} <= codes)
        self.write('package-lock.json', '{invalid')
        self.assertIn('invalid_metadata', self.codes(json.loads(self.run_cli().stdout)))

    def test_cache_excluded_and_linked_package(self):
        self.npm()
        self.write('.cache/NOTICE', 'cached unrelated license')
        nested = self.root / 'node_modules/direct/node_modules/transitive'
        import shutil
        shutil.rmtree(nested)
        outside = self.root / 'outside'
        outside.mkdir()
        nested.symlink_to(outside, target_is_directory=True)
        result = self.run_cli()
        self.assertEqual(result.returncode, 1)
        data = json.loads(result.stdout)
        self.assertIn('symlink_skipped', self.codes(data))
        self.assertIn('.cache', data['excluded_project_directories'])
        self.assertNotIn('cached unrelated license', result.stdout)

    def test_python_license_path_and_missing_record(self):
        info = self.python_env()
        self.write(info + '/METADATA', 'Name: demo\nVersion: 1\nLicense-File: ../../escape\n')
        (self.root / info / 'RECORD').unlink()
        data = json.loads(self.run_cli().stdout)
        self.assertTrue({'invalid_license_path', 'missing_record'} <= self.codes(data))

    def test_install_directory_runs_independently(self):
        import shutil
        import re
        self.npm()
        installed = self.root / 'installed' / 'license-check'
        shutil.copytree(SKILL, installed, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        self.assertEqual({p.name for p in installed.iterdir()}, {'SKILL.md', 'LICENSE', 'scripts', 'references'})
        self.assertEqual({p.relative_to(installed).as_posix() for p in installed.rglob('*') if p.is_file()},
                         {'SKILL.md', 'LICENSE', 'scripts/collect.py',
                          'references/report-format.md', 'references/review-guide.md'})
        self.assertEqual((installed / 'LICENSE').read_bytes(), (SKILL.parents[1] / 'LICENSE').read_bytes())
        for relative in re.findall(r'\]\(([^)]+)\)', (installed / 'SKILL.md').read_text()):
            self.assertTrue((installed / relative).is_file(), relative)
        result = subprocess.run([sys.executable, str(installed / 'scripts/collect.py'),
                                 '--project', str(self.root)], cwd='/', capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(json.loads(result.stdout)['packages']), 2)

    def test_help_and_invalid_project(self):
        help_result = subprocess.run([sys.executable, str(SCRIPT), '--help'], capture_output=True)
        self.assertEqual(help_result.returncode, 0)
        result = subprocess.run([sys.executable, str(SCRIPT), '--project', str(self.root / 'missing')], capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, b'')


if __name__ == '__main__':
    unittest.main()
