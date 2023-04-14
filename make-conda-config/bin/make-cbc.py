#!/usr/bin/env python

import yaml

import os
import sys
import json


def ActionAdapter(function, **extras):
    """Evaluate a main function in a github action

    * Assumes that sys.stdin contains JSON arguments for `function` (main).
    * The keys will have dashes converted to underscores.
    * `function` may return a dictionary of results in which case they will
      be set as the output for the step using $GITHUB_OUTPUT
    * The keys of the outputs will have underscores converted to dashes

    Typical usage would look like:

    - run: echo ${{ toJSON(inputs) }} | ./script.py

    """
    print(' == Starting == ', flush=True)

    arguments = json.load(sys.stdin)
    kwargs = {k.replace('-', '_'): v for k, v in arguments.items()}
    for key, val in kwargs.items():
        print(key, val, type(val))
        if type(val) is str and (val.startswith('[') or val.startswith('{')):
            try:
                kwargs[key] = json.loads(val)
            except Exception:
                pass


    print(' == Using arguments == ')
    print(json.dumps(arguments, indent=2), flush=True)
    if extras:
        print(json.dumps(extras, indent=2), flush=True)

    print(' == Executing == ', flush=True)
    results = function(**kwargs, **extras)

    if results:
        print(' == Outputs == ')
        results = {k.replace('_', '-'): v for k, v in results.items()}
        print(json.dumps(results, indent=2), flush=True)

        lines = []
        for param, arg in results.items():
            lines.append(f'{param}={arg}\n')

        output_path = os.environ.get('GITHUB_OUTPUT')
        if output_path is None:
            raise Exception('Missing $GITHUB_OUTPUT, not in a github runner.')

        with open(output_path, mode='a') as fh:
            fh.write(''.join(lines))
    else:
        print(' == No outputs == ')

    print(' == Done == ', flush=True)

def process_seed_env_deps(env):
    cbc = {}
    mapping = {}
    for install_spec in env['dependencies']:
        package, version = split_spec(install_spec)

        cbc_package = package.replace('-', '_')
        cbc_version = [version]

        mapping[package] = cbc_package
        cbc[cbc_package] = cbc_version

    return mapping, cbc

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
