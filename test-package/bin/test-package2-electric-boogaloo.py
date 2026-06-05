#!/usr/bin/env python
import os
import subprocess
import tarfile
import yaml

from alp.common import ActionAdapter


def find_tests(package_path):
    with tarfile.open(package_path, mode='r:bz2') as fh:
        recipe_fh = fh.extractfile('info/recipe/meta.yaml')
        tests = yaml.safe_load(recipe_fh).get('test')
    return tests


def run_commands(commands):
    conf_src = os.path.join(os.path.dirname(__file__), 'conftest.py')
    conf_dest = os.path.join(os.getcwd(), 'conftest.py')

    try:
        with open(conf_src) as src, open(conf_dest, 'w') as dest:
            dest.write(src.read())

        for cmd in commands:
            print(f'Running: {cmd}', flush=True)
            subprocess.run(cmd, shell=True, check=True,
                           env={**os.environ, 'PY_COLORS': '1'})

    finally:
        if os.path.exists(conf_dest):
            os.remove(conf_dest)


def main(package_path, channels, conda_activate):
    tests = find_tests(package_path)
    print(tests, flush=True)
    if 'commands' in tests:
        run_commands(tests['commands'])


if __name__ == '__main__':
    ActionAdapter(main)
