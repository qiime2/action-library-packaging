#!/usr/bin/env python
import os

from alp.common import ActionAdapter


def _os_detector(runner):
    if runner == 'ubuntu-latest':
        subdir = 'linux-64'
    elif runner == 'macos-latest':
        subdir = 'osx-64'
    else:
        raise ValueError('Unexpected operating system detected: %s' % runner)
    return subdir


def main(pkg, channel, runner):
    subdir = _os_detector(runner)
    path = os.path.dirname(os.path.join(channel, subdir))
    for root, _, files in os.walk(path):
        for name in files:
            if name.startswith(pkg):
                return {'path': (os.path.join(root, pkg))}


if __name__ == '__main__':
    ActionAdapter(main)
