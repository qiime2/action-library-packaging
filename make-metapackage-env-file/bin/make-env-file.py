#!/usr/bin/env python

import subprocess
import os
import io
import itertools

import yaml


from alp.common import ActionAdapter


def main(conda_activate, conda_prefix, package_name, package_version,
         channels, environment_file):
    channels = list(itertools.chain.from_iterable(
        [('-c', c) for c in channels]))

    cmd = [
        'conda', 'create', '-p', conda_prefix, '-y', '-q', *channels,
        f'{package_name}={package_version}'
    ]

    subprocess.run(cmd, check=True)

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

    env['dependencies'].append('conda-pack=0.7.0')

    del env['name']
    del env['prefix']

    with open(environment_file, 'w') as fh:
        yaml.safe_dump(env, fh)


if __name__ == '__main__':
    ActionAdapter(main)



