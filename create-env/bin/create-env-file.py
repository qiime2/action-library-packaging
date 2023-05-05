#!/usr/bin/env python

import subprocess
import os
import io
import itertools

import yaml


from alp.common import ActionAdapter


def main(conda_prefix, environment_file, package_name, **unused):
    cmd = [
        'conda', 'env', 'export', '--no-builds', '-p', conda_prefix
    ]
    result = subprocess.run(cmd, check=True, capture_output=True)
    stdout = io.BytesIO(result.stdout)

    env = yaml.safe_load(stdout)
    env['dependencies'] = [
        spec for spec in env['dependencies']
        if not spec.startswith(package_name)
    ]

    del env['name']
    del env['prefix']

    with open(environment_file, 'w') as fh:
        yaml.safe_dump(env, fh)


if __name__ == '__main__':
    ActionAdapter(main)



