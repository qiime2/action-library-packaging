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
    for spec in env['dependencies']:
        print(spec)
    # isinstance(spec, str) ensures we are only retaining conda package specs
    # and omitting structured dependency entries such as pip blocks, etc.
    # this was added in response to rpy2>=3.6.0, which is now a namespace pkg
    # and pulls in rpy2-rinterface & rpy2-robjects as pip dependencies
    # changelog xref:
    # https://rpy2.github.io/doc/latest/html/changes.html#id3
    env['dependencies'] = [
        spec for spec in env['dependencies']
        if isinstance(spec, str) and not spec.startswith(package_name)
    ]

    del env['name']
    del env['prefix']

    with open(environment_file, 'w') as fh:
        yaml.safe_dump(env, fh)


if __name__ == '__main__':
    ActionAdapter(main)
