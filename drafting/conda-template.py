#!/usr/bin/env python

# This script reads in a yaml file (qiime2 recipe)
# Pulls the needed data from that file
# And uses that data to write to a secondary yaml file
# Which will be the end result: a conda recipe

import yaml
import os
import sys
from jinja2 import Template

def validate_params(cli_args):
    try:
        qiime2_recipe = cli_args[1]
    except:
        raise ValueError('Missing required parameter. QIIME 2 recipe filepath must be provided.')

    try:
        filepath = cli_args[2]
    except:
        raise ValueError('Missing required parameter. conda recipe filename must be provided.')
    
    if os.path.exists(filepath):
        raise FileExistsError('Invalid filename. Recipe file already exists.')

    return qiime2_recipe, filepath

def _yaml_parsing(qiime2_recipe):
    with open(qiime2_recipe) as fh:
        parsed_recipe = yaml.load(fh, Loader=yaml.FullLoader)

    return parsed_recipe

def write_recipe(j2, filepath, parsed_recipe):
    with open(j2) as fh:
        template = Template(fh.read())

    recipe_reqs = template.render(parsed_recipe)

    with open(filepath, 'w') as fh:
        fh.write(recipe_reqs)

if __name__ == '__main__':

    j2 = 'jinja-template.j2'
    input_fp, output_fp = validate_params(sys.argv)
    parsed_recipe = _yaml_parsing(input_fp)
    write_recipe(j2, output_fp, parsed_recipe)

#TODO: add ABOUT segment from plugin into jinja template
