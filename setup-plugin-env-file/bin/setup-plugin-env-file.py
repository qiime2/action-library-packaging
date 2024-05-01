#!/usr/bin/env python

import os
import yaml

from alp.common import ActionAdapter

def main(environment_fp, pip_spec, epoch, distro):
    if os.path.exits(environment_fp):
        with open(environment_fp, 'r') as f:
            env = yaml.safe_load(f)
    else:
        env = {'channels': [
                'replace-me',
                'conda-forge',
                'bioconda'],
               'dependencies': [
                   f'qiime2-{distro}',
                   'pip',
                   {'pip': [pip_spec]}
               ]}
    channel = f'https://packages.qiime2.org/qiime2/{epoch}/{distro}/passed'
    env['channels'][0] = channel
    with open(environment_fp, 'w') as f:
        yaml.safe_dump(env, f, default_flow_style=False)

if __name__ == '__main__':
    ActionAdapter(main)