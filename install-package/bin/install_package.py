#!/usr/bin/env python

import subprocess
import itertools

from alp.common import ActionAdapter


def main(channels, package_name, package_version, conda_prefix):

    channels = itertools.chain.from_iterable(
        [('-c', channel) for channel in channels])

    cmd = [
        'conda', 'install',
        '-p', conda_prefix,
        f'{package_name}={package_version}',
        *channels, '--override-channels',
        '--quiet']

    subprocess.run(cmd, check=True)


if __name__ == '__main__':
    ActionAdapter(main)
