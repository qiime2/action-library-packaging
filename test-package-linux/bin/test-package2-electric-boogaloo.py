#!/usr/bin/env python

import subprocess
import tarfile
import yaml
import tempfile
import os

from alp.common import ActionAdapter


def find_tests(package_path):
    with tarfile.open(package_path, mode='r:bz2') as fh:
        recipe_fh = fh.extractfile('info/recipe/meta.yaml')
        tests = yaml.safe_load(recipe_fh).get('test')

        selenium = False
        if 'requires' in tests:
            for req in tests['requires']:
                if 'selenium' in req:
                    selenium = True
                    break

    return tests, selenium

def run_commands(commands, selenium):
    env = os.environ.copy()

    if selenium:
        tmp_root = tempfile.mkdtemp(prefix='selenium-tmp-')

        env["HOME"] = os.path.join(tmp_root, 'home')
        env["XDG_CONFIG_HOME"] = os.path.join(tmp_root, 'config')
        env["XDG_CACHE_HOME"] = os.path.join(tmp_root, 'cache')
        env["XDG_RUNTIME_DIR"] = os.path.join(tmp_root, 'runtime')
        env["TMPDIR"] = os.path.join(tmp_root, 'tmp')
        env["TMP"] = env["TMPDIR"]
        env["TEMP"] = env["TMPDIR"]
        env["SELENIUM_MANAGER_CACHE_PATH"] = os.path.join(tmp_root,
                                                          'selenium-manager')

        for dir in (env["HOME"], env["XDG_CONFIG_HOME"], env["XDG_CACHE_HOME"],
                    env["TMPDIR"], env["SELENIUM_MANAGER_CACHE_PATH"]):
            os.makedirs(dir, exist_ok=True)

        os.chmod(env["XDG_RUNTIME_DIR"], 0o700)

    for cmd in commands:
        if selenium:
            subprocess.run('pkill -f chromium || true', shell=True)
            subprocess.run('pkill -f chrome || true', shell=True)
            subprocess.run('pkill -f firefox || true', shell=True)

        print(f'Running: {cmd}', flush=True)
        subprocess.run(cmd, shell=True, check=True, env=env)

def main(package_path, channels, conda_activate):
    tests, selenium = find_tests(package_path)
    print(tests, flush=True)
    if 'commands' in tests:
        run_commands(tests['commands'], selenium)


if __name__ == '__main__':
    ActionAdapter(main)
