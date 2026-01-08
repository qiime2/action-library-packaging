#!/usr/bin/env python

import subprocess
import itertools

from alp.common import ActionAdapter


def main(conda_prefix, package_name, package_version, channels, **unused):
    channels = list(itertools.chain.from_iterable(
        [('-c', c) for c in channels]))

    cmd = [
        'conda', 'create', '-p', conda_prefix, '-y', '-q', *channels,
        f'{package_name}={package_version}'
    ]

    subprocess.run(cmd, check=True)


if __name__ == '__main__':
    ActionAdapter(main)
