#!/usr/bin/env python
import os
import re

from alp.common import ActionAdapter


def _os_detector(runner):
    if runner == 'ubuntu-latest':
        subdir = 'linux-64'
    elif runner == 'macos-latest':
        subdir = 'osx-64'
    else:
        raise ValueError('Unexpected operating system detected: %s' % runner)
    return subdir


def main(package, channels, runner):
    subdir = _os_detector(runner)
    for channel in channels:
        path = os.path.dirname(os.path.join(channel, subdir))
        for root, _, files in os.walk(path):
            for name in files:
                if re.match(re.escape(package) + r'\-\d+', name):
                    return {'path': (os.path.join(root, name))}


if __name__ == '__main__':
    ActionAdapter(main)
