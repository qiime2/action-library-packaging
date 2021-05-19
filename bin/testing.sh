#!/usr/bin/env bash

set -xev
# todo: uncomment when done developing
# set -e

    if (additionalTests !== '') {
      const envURL = getEnvFileURL(buildTarget)
      await execWrapper('wget', ['-O', 'env.yml', envURL])

      await execWrapper('sudo',
        ['conda', 'env', 'create', '-q', '-p', './testing', '--file', 'env.yml'])

      const packageJSON = await execWrapper('sudo',
        ['conda', 'list', '-p', './testing', `^${packageName}$`, '--json'])
      const packageParsed = JSON.parse(packageJSON)

      if (packageParsed.length === 0) {
        await execWrapper('sudo',
          ['conda', 'install',
           '-p', './testing',
           '-q', '-y',
           '-c', `${buildDir}`,
           '-c', 'conda-forge',
           '-c', 'bioconda',
           '-c', 'defaults',
           '--override-channels',
           '--strict-channel-priority',
           `${packageName}`])
      } else if (packageParsed.length === 1) {
        await execWrapper('sudo',
          ['conda', 'update',
           '-p', './testing',
           '-q', '-y',
           '-c', 'conda-forge',
           '-c', 'bioconda',
           '-c', 'defaults',
           '--override-channels',
           '--strict-channel-priority',
           '--update-deps',
           `${packageName}`])

        await execWrapper('sudo',
          ['conda', 'update',
           '-p', './testing',
           '-q', '-y',
           '-c', `${buildDir}`,
           '-c', 'conda-forge',
           '-c', 'bioconda',
           '-c', 'defaults',
           '--override-channels',
           '--strict-channel-priority',
           '--force-reinstall',
           `${packageName}`])
      } else {
        throw Error('inconsistent env state')
      }

      await execWrapper('sudo',
        ['conda', 'install',
         '-p', './testing',
         '-q', '-y',
         '-c', 'conda-forge',
         '-c', 'bioconda',
         '-c', 'defaults',
         '--override-channels',
         '--strict-channel-priority',
         'pytest'])

      temp.track()
      const stream = temp.createWriteStream({ suffix: '.sh' })
      stream.write(`source "$CONDA/etc/profile.d/conda.sh" && conda activate ./testing && ${additionalTests}`)
      stream.end()
      await execWrapper('bash', [stream.path as string], 'additional tests failed')
    }
