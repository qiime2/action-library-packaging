import os
import subprocess

from alp.common import ActionAdapter


def main(package_name, package_version, distro, build_target, artifact):
    library_token = os.environ['LIBRARY_TOKEN']
    gh_repo = os.environ['GITHUB_REPOSITORY']
    gh_run_id = os.environ['GITHUB_RUN_ID']

    response = subprocess.run([
        'curl',
        '--silent',
        '--include',
        '--data', f'token={library_token}',
        '--data', f'repository={gh_repo}',
        '--data', f'run_id={gh_run_id}',
        '--data', f'package_name={package_name}',
        '--data-urlencode', f'version={package_version}',
        '--data', f'distro={distro}',
        '--data', f'build_target={build_target}',
        '--data', f'artifact_name={artifact}',
        '--header', 'Content-Type: application/x-www-form-urlencoded',
        '--request', 'POST',
        'https://library.qiime2.org/api/v2/packages/integrate/',
    ])

    if response.returncode != 0:
        raise Exception('Connection to the Library was unsuccessful.')


if __name__ == '__main__':
    ActionAdapter(main)
