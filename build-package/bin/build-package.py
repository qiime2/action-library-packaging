#!/usr/bin/env python

import itertools
import os
import io
import subprocess
import glob

import yaml
import json

from alp.common import ActionAdapter


def head(fh, n):
    lines = []
    for _, line in zip(range(n), fh):
        lines.append(line)
    return io.StringIO(''.join(lines))


def get_setup_info(recipe_path, key):
    if not os.path.isdir(recipe_path):
        raise Exception(f'{recipe_path} is not a directory')

    setup_path = os.path.join(recipe_path, '..', '..', 'setup.py')
    cmd = [
        'python',
        setup_path,
        f'--{key}'
    ]

    result = subprocess.run(cmd, check=True, capture_output=True)
    return result.stdout.decode().strip()


def main(recipe_path, conda_build_config, channels,
         output_channel, conda_activate=None, dry_run=False,
         metapackage=False):

    conda_info = subprocess.run(['conda', 'info', '--json'], check=True,
                                capture_output=True).stdout.decode('utf-8')
    platform = json.loads(conda_info)['platform']

    if type(dry_run) is str:
        dry_run = dry_run == 'true'

    if type(metapackage) is str:
        metapackage = metapackage == 'true'

    channels = itertools.chain.from_iterable(
        [('-c', channel) for channel in channels])
    cmd = [
        'conda', 'mambabuild',
        *channels,
        '--override-channels',
        '--quiet',
        '--no-test',
        '--old-build-string',
        '-m', conda_build_config,
        '--output-folder', output_channel,
        recipe_path]

    print('OR IS PRINTING A DEBUGGING STRATEGY????????????')
    print(channels)

    name = ''
    version = ''
    build = ''
    filename = ''
    subdir = ''

    if metapackage:
        with open(os.path.join(recipe_path, 'meta.yaml')) as fh:
            recipe = yaml.safe_load(head(fh, 4))
        name = recipe['package']['name']
        version = recipe['package']['version']
    else:
        name = get_setup_info(recipe_path, 'name')
        version = get_setup_info(recipe_path, 'version')

    if not dry_run:
        print(f'Running: {" ".join(cmd)}', flush=True)
        subprocess.run(cmd, check=True)
        print('done.', flush=True)

        found = glob.glob(os.path.join(output_channel, platform,
                                       '-'.join([name, version, '*'])))
        path, = found

        output_info = os.path.relpath(path, output_channel)
        subdir, filename = os.path.split(output_info)

        name_from_file, version_from_file, build = filename.rsplit('-', 2)

        assert name == name_from_file
        assert version == version_from_file

        build, ext = os.path.splitext(build)
        if ext == '.bz2':
            # one more time for tar
            build, ext = os.path.splitext(build)
            assert ext == '.tar'
            subdir = ''

    return dict(name=name, version=version, filename=filename,
                build=build, subdir=subdir)


if __name__ == '__main__':
    ActionAdapter(main)


"""
A chronicle of my failures over 7ish (future me: add 6 more) hours:

So. I tried to get `conda [mamba]build` to work, however there is something
about how it is invoked which just DOES NOT WORK with `conda-pack`.

I tried the following configurations:
    - conda run -p <PREFIX> <CMD>
    - <PREFIX>/bin -> $PATH
    - conda init + conda activate -> .bash_profile (this one failed miserably)
       * I could not get conda init to work properly in GH actions which caused
         most everything else to fail.
       * I did not yet try sourcing the base conda setup which may be necessary
         source "$CONDA/etc/profile.d/conda.sh"
       * This doesn't matter because I was able to reproduce this locally and
         using `conda activate` did not help in a local environment.

`conda-pack` is necessary in github actions as the prefix of the environment is
not in a reliable location. What conda-pack does rewrite an environment (using
pkg cache) to create a tar file with all prefixes replaced with their original
form. This is then undone (just like during installation) using `conda-unpack`

I know that I was able to get conda-unpack to work correctly as if I did not
use the command, the CA certificates where completely hosed (showing the
pre-install prefixes) which broke the build.

I was also able to reproduce the issue with `conda [mamba]build` locally.
In a freshly-unpacked prefix we will inevitably get this error during PS1
setup for the build environment:

    +++ export PATH
    +++ '[' -z '' ']'
    +++ PS1=
    +++ conda activate base
    +++ local cmd=activate
    +++ case "$cmd" in
    +++ __conda_activate activate base
    +++ '[' -n '' ']'
    +++ local ask_conda
    ++++ PS1=
    ++++ __conda_exe shell.posix activate base
    ++++ /home/evan/alp3/bin/conda shell.posix activate base
    Traceback (most recent call last):
      File "/home/evan/alp3/bin/conda", line 12, in <module>
        from conda.cli import main
    ModuleNotFoundError: No module named 'conda'
    +++ ask_conda=
    +++ return

    subprocess.CalledProcessError: Command '['/bin/bash', '-x', '-o',
    'errexit', '/home/evan/alp3/conda-bld/q2-feature-table_1681863197065/work
    /conda_build.sh']' returned non-zero exit status 1.

This error DOES NOT OCCUR when using a regular prefix environment (that hasn't
gone through conda-pack). Inspecting differences when using --debug between the
two modes did not reveal anything as the debug output was essentially the same.

---

Given the above, the plan is to continue to use conda-pack, which works well in
every other reasonable situation.

An alternative to that would be to generate a one-stop-shop channel out of the
conda pkg cache post-installation, and cache that channel in github actions
instead of a packed environment. This is slightly less convenient but would
probably work.

"""
