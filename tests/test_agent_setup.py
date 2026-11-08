"""Isolated bootstrap regressions: no network, host installs, or real browser cache."""
import os
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
SETUP = ROOT / 'scripts/setup-agent.sh'

# A tiny executable models tool success/failure and records observable setup work.
# Archives contain executable launchers, so the real tar command tests extraction.
FAKE = r'''
import os,sys,json,tarfile,io
from pathlib import Path
name=Path(sys.argv[0]).name; args=sys.argv[1:]; root=Path(os.environ['SETUP_TEST_ROOT'])
state=root/'state'; state.mkdir(exist_ok=True)
with (state/'calls').open('a') as f:f.write(name+' '+repr(args)+'\n')
if name=='git': print(root)
elif name=='uname': print(os.environ.get('SETUP_TEST_OS','Darwin') if args==['-s'] else os.environ.get('SETUP_TEST_ARCH','arm64'))
elif name=='node':
 if 'process.versions' in ' '.join(args):print('22')
 elif 'package.json' in ' '.join(args):print((state/'node-version').read_text() if (state/'node-version').exists() else '1.65.0')
 else:sys.exit(0 if (state/'node-browser').exists() else 1)
elif name=='npm':(state/'node-version').write_text('1.64.1')
elif name=='npx':(state/'node-browser').touch()
elif name in ('python','python3'):
 if args[:2]==['-m','venv']:
  out=root/'.venv/bin';out.mkdir(parents=True,exist_ok=True)
  p=out/'python';p.write_text(Path(sys.argv[0]).read_text());p.chmod(0o755)
 elif args[:3]==['-m','pip','install']:
  if os.environ.get('SETUP_TEST_PIP_FAIL'):sys.exit(17)
  (state/'dependencies').touch()
 elif args[:3]==['-m','pip','check']:sys.exit(0 if (state/'dependencies').exists() else 1)
 elif args[:3]==['-m','playwright','install']:(state/'python-browser').touch()
 elif 'importlib.metadata' in ' '.join(args):print('1.64.1')
 elif 'sync_playwright' in ' '.join(args):sys.exit(0 if (state/'python-browser').exists() else 1)
 else:sys.exit(0 if (state/'dependencies').exists() else 1)
elif name=='quarto':print(os.environ.get('SETUP_TEST_QUARTO_VERSION','1.10.19'))
elif name=='pandoc':
 assert Path(args[-1]).exists(), 'locale probe must exist'
 print('true')
elif name=='curl':
 target=Path(args[args.index('-o')+1]);url=args[-1]
 (state/'archive-url').write_text(url)
 prefix='quarto-1.10.19/' if 'linux' in url else ''
 with tarfile.open(target,'w:gz') as archive:
  for filename,body in [('bin/quarto', '#!/bin/sh\necho 1.10.19\n'),('bin/tools/test/pandoc','#!/bin/sh\ntest -f "$2" || exit 1\necho true\n')]:
   b=body.encode();info=tarfile.TarInfo(prefix+filename);info.mode=0o755;info.size=len(b);archive.addfile(info,io.BytesIO(b))
else:sys.exit('unexpected command '+name)
'''


@pytest.fixture
def setup_tree(tmp_path):
    """Create an existing incomplete venv and stale browser caches for setup to repair."""
    root = tmp_path / 'worktree with spaces'
    bindir = root / 'tools'
    bindir.mkdir(parents=True)
    executable = '#!' + sys.executable + '\n' + FAKE
    for name in ('git', 'node', 'npm', 'npx', 'python3', 'uname', 'curl', 'quarto'):
        p = bindir / name
        p.write_text(executable)
        p.chmod(0o755)
    venv = root / '.venv/bin'
    venv.mkdir(parents=True)
    p = venv / 'python'
    p.write_text(executable)
    p.chmod(0o755)
    (root / 'requirements-test.txt').write_text('playwright==1.64.1\npypdf==7.0.0\n')
    # The old cache wildcard would mistake this incomplete revision for readiness.
    (root / 'stale-cache/chromium_headless_shell-obsolete').mkdir(parents=True)
    doctor = root / 'scripts/hillclimb/hc.sh'
    doctor.parent.mkdir(parents=True)
    doctor.write_text('#!/bin/sh\ntest "$LC_ALL" = C || exit 1\necho "All tools present."\n')
    pandoc = bindir / 'tools/test/pandoc'
    pandoc.parent.mkdir(parents=True)
    pandoc.write_text(executable)
    pandoc.chmod(0o755)
    env = {**os.environ, 'PATH': str(bindir) + ':/usr/bin:/bin',
           'SETUP_TEST_ROOT': str(root), 'PLAYWRIGHT_BROWSERS_PATH': str(root / 'stale-cache')}
    env.pop('QUARTO', None)
    return root, env


def run_setup(root, env, download=False):
    """Run the real main flow with deterministic external tools and no host /opt fallback."""
    command = 'source "$1"; '
    if download:
        # Ignore a host-level /opt install only; other version checks remain real.
        command += '''eval "$(declare -f quarto_ok | sed '1s/quarto_ok/test_quarto_ok/')";
quarto_ok() { case "$1" in /opt/*) return 1;; esac; test_quarto_ok "$1"; }; '''
    command += 'main'
    return subprocess.run(['bash', '-c', command, 'setup-test', str(SETUP)],
                          cwd=root, env=env, capture_output=True, text=True)


def test_existing_venv_stale_cache_and_sourced_locale_are_repaired(setup_tree):
    root, env = setup_tree
    env['LC_ALL'] = 'C'
    result = run_setup(root, env)
    assert result.returncode == 0, result.stdout + result.stderr
    calls = (root / 'state/calls').read_text()
    assert "'pip', 'install'" in calls
    assert 'playwright@1.64.1' in calls
    assert "npx ['--no-install', 'playwright', 'install', 'chromium']" in calls
    assert "python ['-m', 'playwright', 'install', 'chromium']" in calls
    assert 'All tools present.' in result.stdout
    # The env file must safely round-trip a Quarto path containing spaces.
    check = subprocess.run(['bash', '-c', '. "$1"; "$QUARTO" --version; echo "$LC_ALL"',
                            'env-test', str(root / '.autoresearch-tools/env.sh')],
                           env=env, capture_output=True, text=True, check=True)
    assert check.stdout.splitlines() == ['1.10.19', 'C']


def test_pip_failure_stops_before_readiness(setup_tree):
    root, env = setup_tree
    env['SETUP_TEST_PIP_FAIL'] = '1'
    result = run_setup(root, env)
    assert result.returncode != 0
    assert 'All tools present.' not in result.stdout
    assert not (root / '.autoresearch-tools/env.sh').exists()


def test_wrong_explicit_quarto_version_is_rejected(setup_tree):
    root, env = setup_tree
    env.update(QUARTO=str(root / 'tools/quarto'), SETUP_TEST_QUARTO_VERSION='1.9.38')
    result = run_setup(root, env)
    assert result.returncode != 0
    assert 'QUARTO must point to Quarto 1.10.19' in result.stderr


@pytest.mark.parametrize(('system', 'arch', 'asset'), [
    ('Darwin', 'arm64', 'macos'),
    ('Linux', 'x86_64', 'linux-amd64'),
    ('Linux', 'aarch64', 'linux-arm64'),
    ('Linux', 'arm64', 'linux-arm64'),
])
def test_wrong_path_version_downloads_and_extracts_the_pinned_archive(setup_tree, system, arch, asset):
    root, env = setup_tree
    env.update(SETUP_TEST_OS=system, SETUP_TEST_ARCH=arch, SETUP_TEST_QUARTO_VERSION='1.10.18')
    result = run_setup(root, env, download=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert (root / 'state/archive-url').read_text().endswith(f'quarto-1.10.19-{asset}.tar.gz')
    assert (root / '.autoresearch-tools/bin/quarto').is_file()
    assert 'All tools present.' in result.stdout
