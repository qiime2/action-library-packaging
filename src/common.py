import os
import sys
import json


def ActionAdapter(function):
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
    print(' == Using arguments == ')
    print(json.dumps(arguments, indent=2), flush=True)

    print(' == Executing == ', flush=True)
    results = function(**kwargs)

    if results:
        print(' == Outputs == ')
        results = {k.replace('_', '-'): v for k, v in results.items()}
        print(json.dumps(results, indent=2, flush=True))

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
