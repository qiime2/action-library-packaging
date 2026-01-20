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
    if selenium:
        tmp_root = tempfile.mkdtemp(prefix='selenium-tmp-')
        env = os.environ.copy()
        env["HOME"] = os.path.join(tmp_root, 'home')
        env["XDG_CONFIG_HOME"] = os.path.join(tmp_root, 'config')
        env["XDG_CACHE_HOME"] = os.path.join(tmp_root, 'cache')
        env["TMPDIR"] = os.path.join(tmp_root, 'tmp')
        for dir in (env["HOME"], env["XDG_CONFIG_HOME"],
                    env["XDG_CACHE_HOME"], env["TMPDIR"]):
            os.makedirs(dir, exist_ok=True)

    for cmd in commands:
        print(f'Running: {cmd}', flush=True)
        subprocess.run(cmd, shell=True, check=True, env=env)

def main(package_path, channels, conda_activate):
    tests, selenium = find_tests(package_path)
    print(tests, flush=True)
    if 'commands' in tests:
        run_commands(tests['commands'], selenium)


if __name__ == '__main__':
    ActionAdapter(main)
