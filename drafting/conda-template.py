#!/usr/bin/env python

# This script reads in a yaml file (qiime2 recipe)
# Pulls the needed data from that file
# And uses that data to write to a secondary yaml file
# Which will be the end result: a conda recipe

import yaml
import os
import sys
from jinja2 import Template

if __name__ == '__main__':
    # Reading the qiime2 recipe file
    try:
        qiime2_recipe = sys.argv[1]
    except:
        raise ValueError('Missing required parameter. QIIME 2 recipe filepath must be provided.')
    
    with open(qiime2_recipe) as qiime2_recipe:
        parsed_recipe = yaml.load(qiime2_recipe, Loader=yaml.FullLoader)

    try:
        filepath = sys.argv[2]
    except:
        raise ValueError('Missing required parameter. conda recipe filename must be provided.')
    
    if os.path.exists(filepath):
        raise FileExistsError('Invalid filename. Recipe file already exists.')

    # Accessing jinja template with recipe key pairs
    with open('jinja-template.j2') as file:
        template = Template(file.read())

    recipe_reqs = template.render(parsed_recipe)
    # print(recipe_reqs)
    conda_recipe = open(filepath, 'w')
    yaml.dump(recipe_reqs, conda_recipe)
    conda_recipe.close

    #TODO: add ABOUT segment from plugin into jinja template
