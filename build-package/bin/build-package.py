#!/usr/bin/env python

import itertools
import os
import subprocess

from alp.common import ActionAdapter


def main(conda_prefix, recipe_path, conda_build_config, channels,
         output_channel):
    channels = itertools.chain.from_iterable(
        [('-c', channel) for channel in channels])

    cmd = [
        # "activate environment"
        'conda', 'run',
        '-p', conda_prefix,
        # actual command
        'conda', 'mambabuild',
        *channels,
        '--override-channels',
        '--quiet',
        '--no-test',
        '--old-build-string',
        '-m', conda_build_config,
        '--output-folder', output_channel,
        recipe_path]

    subprocess.run(cmd, check=True)

    output = subprocess.run([*cmd[:-1], '--output', cmd[-1]], check=True,
                            capture_output=True)

    output_info = os.path.relpath(output.stdout, output_channel)
    subdir, filename = os.path.split(output_info)

    name, version, build = filename.rsplit('-', 3)

    return dict(name=name, version=version, filename=filename,
                build=build, subdir=subdir)


if __name__ == '__main__':
    ActionAdapter(main)
