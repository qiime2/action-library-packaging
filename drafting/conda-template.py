#!/usr/bin/env python

# This script reads in a yaml file (qiime2 recipe)
# Pulls the needed data from that file
# And uses that data to write to a secondary yaml file
# Which will be the end result: a conda recipe

import yaml
import os
import sys

if __name__ == '__main__':
    # Reading the qiime2 recipe file
    try:
        qiime2_recipe = sys.argv[1]
    except:
        print('ArgumentError: Missing required parameter. QIIME 2 recipe filepath must be provided.')
        sys.exit(1)
    
    with open(qiime2_recipe) as qiime2_recipe:
        parsed_recipe = yaml.load(qiime2_recipe, Loader=yaml.FullLoader)

    try:
        filepath = sys.argv[2]
    except:
        print('ArgumentError: Missing required parameter. conda recipe filename must be provided.')
        sys.exit(1)
    
    if os.path.exists(filepath):
        raise FileExistsError('Invalid filename. Recipe file already exists.')

    # Extracting the necessary key pairs from the qiime2 recipe
    name = parsed_recipe['name']
    version = parsed_recipe['version']
    build_command = parsed_recipe['build']
    script = build_command.get('command')
    run_reqs = parsed_recipe['requirements']
    qiime_run_reqs = run_reqs.get('qiime2')
    anaconda_run_reqs = run_reqs.get('anaconda')
    qiime2_test = parsed_recipe['test']
    imports = qiime2_test.get('imports')
    commands = qiime2_test.get('commands')

    # PACKAGE
    package = {
        'package': {
            'name': name,
            'version': version
        }
    }
    # SOURCE
    source = {
        'source': {
            'path': '.'
        }
    }
    # BUILD
    build = {
        'build': {
            'script': script
        }
    }
    # REQUIREMENTS
    host = [
        'python {{ python }}',
        'setuptools {{ setuptools }}'
    ]
    run = [
        'python {{ python }}',
        qiime_run_reqs,
        anaconda_run_reqs
    ]
    reqs = {
        'requirements': {
            'host': host,
            'run': run
        }
    }
    # TEST
    test = {
        'test': {
            'imports': imports,
            'commands': commands
        }
    }

    # Opening and writing to new conda recipe file
    recipe_reqs = [package, source, build, reqs, test]
    conda_recipe = open(filepath, 'w')
    yaml.dump(recipe_reqs, conda_recipe)
    conda_recipe.close

    # ABOUT
        # TODO: figure out how to pull this from the actual plugin
