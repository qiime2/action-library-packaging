#!/usr/bin/env python

import yaml

from alp.common import ActionAdapter
from alp.cbc import split_spec


def main(conda_activate, environment_file, versions_file):
    with open(environment_file) as fh:
        env = yaml.safe_load(fh)

    with open(versions_file) as fh:
        updates = [line.strip() for line in fh]
        split_updates = [split_spec(u)[0] for u in updates]

    deps = env['dependencies']
    split_deps = [split_spec(d)[0] for d in deps]

    for name, spec in zip(split_updates, updates):
        try:
            idx = split_deps.index(name)
            deps[idx] = spec
        except ValueError:
            deps.append(spec)

    with open(environment_file, 'w') as fh:
        yaml.safe_dump(env, fh, default_flow_style=False)


if __name__ == '__main__':
    ActionAdapter(main)
