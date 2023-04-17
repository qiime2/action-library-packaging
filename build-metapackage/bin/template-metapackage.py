#!/usr/bin/env python

import subprocess
import sys
import os
import jinja2

from alp.common import ActionAdapter
from alp.cbc import process_seed_env_deps


def main(metapackage_name, metapackage_version, seed_environment, recipe_path,
         **ignored):
    GITHUB_ACTION_PATH = os.environ.get('GITHUB_ACTION_PATH')
    if GITHUB_ACTION_PATH is None:
        raise Exception('Expected $GITHUB_ACTION_PATH, not in a github runner')
    TEMPLATE_DIR = os.path.join(GITHUB_ACTION_PATH, 'templates')
    J_ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR))

    with open(seed_environment) as fh:
        env = yaml.safe_load(fh)

    mapping, _ = process_seed_env_deps(env)
    template = J_ENV.get_template('meta.yaml.j2')

    with open(os.path.join(recipe_path, 'meta.yaml'), 'w') as fh:
        fh.write(template.render(
            name=metapackage_name,
            version=metapackage_version,
            packages=mapping
        ))


if __name__ == '__main__':
    recipe_path, = sys.argv[1:]
    ActionAdapter(main, recipe_path=recipe_path)
