#!/usr/bin/env python

import yaml


from alp.cbc import process_seed_env_deps
from alp.common import ActionAdapter


def main(seed_environment, conda_build_config, channels, skip_first_channel, conda_activate=None):
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
        env_channels = env['channels']
        if skip_first_channel == 'true' or skip_first_channel is True:
            env_channels = env_channels[1:]
        env['channels'] = channels + env_channels

    return env


if __name__ == '__main__':
    ActionAdapter(main)
