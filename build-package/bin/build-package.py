#!/usr/bin/env python

import itertools
import os
import io
import subprocess
import glob
import tempfile

import yaml
import json

from alp.common import ActionAdapter


def head(fh, n):
    lines = []
    for _, line in zip(range(n), fh):
        lines.append(line)
    return io.StringIO(''.join(lines))


def get_pkg_name_and_version(recipe_path):
    if not os.path.isdir(recipe_path):
        raise Exception(f'{recipe_path} is not a directory')

    pip_install_path = os.path.join(recipe_path, '..')

    cmd = [
        'pip', 'install', '--dry-run',
        '--report', 'report.json',
        pip_install_path
    ]

    print(f"Debug: Running command: {cmd}")
    print(f"Debug: Working directory: {os.getcwd()}")
    print(f"Debug: Checking if {pip_install_path} exists..."
          f" {os.path.exists(pip_install_path)}")

    try:
        completed = subprocess.run(
            cmd, check=True, capture_output=True, text=True
        )
        print("Debug: pip install output:", completed.stdout)
        print("Debug: pip install errors:", completed.stderr)
    except subprocess.CalledProcessError as e:
        print("Error: pip install command failed!")
        print("Command:", e.cmd)
        print("Return code:", e.returncode)
        print("Output:", e.stdout)
        print("Error output:", e.stderr)
        raise

    subprocess.run(cmd, check=True, capture_output=True)
    result = subprocess.run(['cat', 'report.json'], check=True,
                            capture_output=True, text=True)

    result_json = json.loads(result.stdout)

    pkg_name = result_json['install'][0]['metadata']['name']
    pkg_version = result_json['install'][0]['metadata']['version']

    return pkg_name, pkg_version


def make_conda_build_cmd(recipe_path, conda_build_config, channels,
                         output_channel, output_only=False):
    cmd = ['conda', 'build']

    if channels:
        cmd.extend(itertools.chain.from_iterable(
            [('-c', channel) for channel in channels]
        ))
        cmd.append('--override-channels')

    cmd.extend(['--quiet', '--no-test'])

    if conda_build_config:
        cmd.extend(['-m', conda_build_config])

    cmd.extend(['--output-folder', output_channel])

    if output_only:
        cmd.append('--output')

    cmd.append(recipe_path)
    return cmd


def normalize_local_path(path):
    if not path:
        return path

    if '://' in path:
        return path

    if os.path.isabs(path):
        return path

    if path.startswith('.'):
        return os.path.abspath(path)

    if path.startswith('~'):
        return os.path.expanduser(path)

    if os.sep in path:
        return os.path.abspath(path)

    return path


def get_output_metadata(recipe_path, conda_build_config, channels,
                        output_channel, env_args):
    recipe_path = normalize_local_path(recipe_path)
    conda_build_config = normalize_local_path(conda_build_config)
    output_channel = normalize_local_path(output_channel)
    channels = [normalize_local_path(channel) for channel in channels]

    with tempfile.TemporaryDirectory() as tmpdir:
        cmd = make_conda_build_cmd(
            recipe_path, conda_build_config, channels, output_channel,
            output_only=True
        )

        try:
            result = subprocess.run(
                cmd, check=True, capture_output=True, text=True, cwd=tmpdir,
                **env_args
            )
        except subprocess.CalledProcessError as e:
            print("Error: conda build --output command failed!")
            print("Command:", e.cmd)
            print("Return code:", e.returncode)
            print("Output:", e.stdout)
            print("Error output:", e.stderr)
            raise

    path = result.stdout.strip().splitlines()[-1]
    output_info = os.path.relpath(path, output_channel)
    subdir, filename = os.path.split(output_info)
    return subdir, filename


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

    if not channels:
        channels = []
    elif isinstance(channels, str):
        channels = [channels]

    cmd = make_conda_build_cmd(
        recipe_path, conda_build_config, channels, output_channel
    )

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
        env_args = {}

    else:
        name, version = get_pkg_name_and_version(recipe_path)
        env = os.environ.copy()
        env['PLUGIN_VERSION'] = version
        # only want to include env arg for pkgs, not metapkg
        env_args = {'env': env}

    if dry_run:
        subdir, filename = get_output_metadata(
            recipe_path, conda_build_config, channels, output_channel, env_args
        )
        name_from_file, version_from_file, build = filename.rsplit('-', 2)
        assert name == name_from_file
        assert version == version_from_file

        build, ext = os.path.splitext(build)
        if ext == '.bz2':
            build, ext = os.path.splitext(build)
            assert ext == '.tar'

    if not dry_run:
        print(f'Running: {" ".join(cmd)}', flush=True)
        subprocess.run(cmd, check=True, **env_args)
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
