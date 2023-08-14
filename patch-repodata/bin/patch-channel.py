#!/usr/bin/env python

import json
import subprocess
from collections import defaultdict
import copy
import os

from alp.common import ActionAdapter
from alp.cbc import split_spec

SUBDIRS = ['linux-64', 'noarch', 'osx-64']


def main(conda_activate, channel, rev_deps, versions_file):
    with open(rev_deps) as fh:
        rev_deps = json.load(fh)

    with open(versions_file) as fh:
        updates = [line.strip() for line in fh]
        new_versions = dict([split_spec(u) for u in updates])

    patch_channels(channel_dir=channel, rev_deps=rev_deps,
                   new_versions=new_versions)


def _patch_repodata(repodata, instructions, changes):
    packages = repodata['packages']

    for updated, downstream in changes.items():
        updated_pkg, new_version = updated
        for pkg, info in packages.items():
            if info['name'] in downstream:
                deps = info['depends']
                for idx, dep in enumerate(deps):
                    if updated_pkg == dep.split()[0]:
                        if instructions['packages'].get(pkg, None) is None:
                            instructions['packages'][pkg] = {}
                            instructions['packages'][pkg]['depends'] = \
                                copy.deepcopy(packages[pkg]['depends'])
                        instructions['packages'][pkg]['depends'][idx] = \
                            f'{updated_pkg} {new_version}'
                        break

    return instructions


def patch_channels(channel_dir, rev_deps, new_versions):
    patch_instructions = {}

    versioned_revdeps = {(pkg, version): rev_deps[pkg]
                         for pkg, version in new_versions.items()}

    for subdir in SUBDIRS:
        if not os.path.exists(os.path.join(channel_dir, subdir)):
            continue

        with open(os.path.join(channel_dir,
                               subdir, 'repodata.json'), 'r') as fh:
            repodata = json.load(fh)
        patch_path = os.path.join(
            channel_dir, subdir, 'patch_instructions.json')
        if os.path.exists(patch_path):
            with open(patch_path) as fh:
                instructions = json.load(fh)
        else:
            instructions = {
                'patch_instructions_version': 1,
                'packages': {},
                'revoke': [],
                'remove': [],
            }

        patch_instructions = _patch_repodata(repodata, instructions,
                                             versioned_revdeps)
        with open(patch_path, 'w') as fh:
            json.dump(patch_instructions, fh, indent=2,
                      sort_keys=True, separators=(",", ": "))

    subprocess.run(['conda', 'index', channel_dir], check=True)


if __name__ == '__main__':
    ActionAdapter(main)
