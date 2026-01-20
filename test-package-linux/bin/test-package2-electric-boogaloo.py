#!/usr/bin/env python

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
    for cmd in commands:
        print(f'Running: {cmd}', flush=True)
        subprocess.run(cmd, shell=True, check=True)

def main(package_path, channels, conda_activate):
    tests = find_tests(package_path)
    print(tests, flush=True)
    if 'commands' in tests:
        run_commands(tests['commands'])


if __name__ == '__main__':
    ActionAdapter(main)
