#!/usr/bin/env python

import yaml
from packaging.version import parse

from alp.common import ActionAdapter
from alp.cbc import split_spec


def load_env(environment_file):
    with open(environment_file) as fh:
        env = yaml.safe_load(fh)

    return env


def versions_to_env(versions_file):
    new_env = {}
    with open(versions_file) as fh:
        updates = [line.strip() for line in fh]

    new_env['dependencies'] = updates

    return new_env


def main(conda_activate, environment_file, versions_file,
         mask_environment_file):
    env = load_env(environment_file)
    deps = env['dependencies']
    package_versions = dict(split_spec(d) for d in deps)
    package_order = {split_spec(d)[0]: idx for idx, d in enumerate(deps)}

    if versions_file != '':
        mask = versions_to_env(versions_file)
    elif mask_environment_file != '':
        mask = load_env(mask_environment_file)
    else:
        raise Exception('neither versions_file or mask_environment_file'
                        ' were provided')

    mask_deps = mask['dependencies']
    for (pkg, new_version), spec in zip(map(split_spec, mask_deps), mask_deps):
        if pkg in package_order:
            idx = package_order[pkg]
            version = package_versions[pkg]
            if parse(new_version) > parse(version):
                deps[idx] = spec
        else:
            deps.append(spec)

    with open(environment_file, 'w') as fh:
        yaml.safe_dump(env, fh, default_flow_style=False)


if __name__ == '__main__':
    ActionAdapter(main)
