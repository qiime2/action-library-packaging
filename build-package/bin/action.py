#!/usr/bin/env python

import itertools
import json
import subprocess

from ...src.common import ActionAdapter


def main(recipe_path, conda_build_config, channels, output_channel):
    channels = itertools.chain.from_iterable(
        [('-c', channel) for channel in channels])

    cmd = [
        'sudo', 'conda', 'mambabuild',
        *channels,
        '--override-channels',
        '--quiet',
        '--no-test',
        '--old-build-string',
        '-m', conda_build_config,
        '--stats-file', '__buildstats.json',
        '--output-folder', output_channel,
        recipe_path]

    subprocess.run(cmd, check=True)

    with open('__buildstats.json', 'r') as fh:
        stats = json.load(fh)

    for k in stats:
        if k.startswith('build'):
            name, version = k.rsplit('-', 1)
            name = name[len('build'):]

            return dict(name=name, version=version)

    raise Exception('Could not identify package name')


if __name__ == '__main__':
    ActionAdapter(main)
