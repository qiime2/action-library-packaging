#!/usr/bin/env python

import subprocess
import itertools
import io

import yaml


from alp.common import ActionAdapter


def main(conda_prefix, environment_file, package_name, channels, **unused):
    channels = itertools.chain.from_iterable(
        [('-c', channel) for channel in channels])

    cmd = [
        'conda', 'env', 'export', *channels, '--override-channels',
        '--no-builds', '-p', conda_prefix
    ]
    result = subprocess.run(cmd, check=True, capture_output=True)
    stdout = io.BytesIO(result.stdout)

    env = yaml.safe_load(stdout)

    print("=== dependencies debug start ===")
    for i, spec in enumerate(env['dependencies']):
        print(f"[{i}] type={type(spec).__name__} repr={spec!r}")
    print("=== dependencies debug end ===")

    env['dependencies'] = [
        spec for spec in env['dependencies']
        if not (isinstance(spec, str) and spec.startswith(package_name))
    ]

    print("=== filtered dependencies debug start ===")
    for i, spec in enumerate(env['dependencies']):
        print(f"[{i}] type={type(spec).__name__} repr={spec!r}")
    print("=== filtered dependencies debug end ===")

    del env['name']
    del env['prefix']

    with open(environment_file, 'w') as fh:
        yaml.safe_dump(env, fh)


if __name__ == '__main__':
    ActionAdapter(main)
