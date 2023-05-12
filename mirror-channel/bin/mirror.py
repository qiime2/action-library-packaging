#!/usr/bin/env python
import yaml
import os
import subprocess

from alp.common import ActionAdapter

SUBDIRS = ['linux-64', 'noarch', 'osx-64']


def write_config(pkgs_in_distro, dest):
    config_yaml = {'blacklist': [{'name': '*'}]}
    whitelist = []

    for pkg, version in pkgs_in_distro.items():
        whitelist.append({'name': pkg, 'version': version})

    config_yaml['whitelist'] = whitelist
    with open(dest, 'w') as fh:
        yaml.safe_dump(config_yaml, fh)


def create_channel(remote_channel, channel_dir, config):
    CMD_TEMPLATE = ('conda-mirror --upstream-channel %s --target-directory %s '
                    '--platform %s --config %s')
    for subdir in SUBDIRS:
        cmd = CMD_TEMPLATE % (remote_channel, channel_dir, subdir, config)
        subprocess.run(cmd.split(), check=True)


def main(packages, remote_channel, local_channel):
    config = os.path.join(local_channel, 'config.yaml')
    write_config(packages, config)
    create_channel(remote_channel, local_channel, config)


if __name__ == '__main__':
    ActionAdapter(main)
