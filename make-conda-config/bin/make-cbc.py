#!/usr/bin/env python

import yaml

from ...src.common import ActionAdapter
from ...src.cbc import process_seed_env_deps


def split_spec(install_spec):
    # incomplete and lazy, but matches what we assume for now
    return install_spec.split('=')


def main(seed_environment, conda_build_config, channels):
    with open(seed_environment) as fh:
        env = yaml.safe_load(fh)

    _, cbc = process_seed_env_deps(env)

    with open(conda_build_config, 'w') as fh:
        yaml.safe_dump(cbc, fh, default_flow_style=False)

    if 'extras' not in env:
        env['extras'] = {}

    if 'channels' not in env:
        env['channels'] = channels
    else:
        env['channels'] += channels

    return env


if __name__ == '__main__':
    ActionAdapter(main)
