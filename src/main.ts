function getArtifactName(): string {
    let artifactName = ''
    if (os.platform() === 'linux') {
      artifactName = 'linux-64'
    } else if (os.platform() === 'darwin' ) {
      artifactName = 'osx-64'
    } else {
      throw Error('Unsupported OS, must be Linux or Mac')
    }

    return artifactName
}

function getEnvFileURL(buildTarget: string): string {
  let platformName = ''
  if (os.platform() === 'linux') {
    platformName = 'linux'
  } else if (os.platform() === 'darwin' ) {
    platformName = 'osx'
  } else {
    throw Error('Unsupported OS, must be Linux or Mac')
  }

  switch(buildTarget) {
    case 'tested':
      return `https://raw.githubusercontent.com/qiime2/environment-files/master/2021.8/test/qiime2-2021.8-py38-${platformName}-conda.yml`

    case 'staged':
      return `https://raw.githubusercontent.com/qiime2/environment-files/master/2021.8/staging/qiime2-2021.8-py38-${platformName}-conda.yml`

    case 'released':
      return `https://raw.githubusercontent.com/qiime2/environment-files/master/2021.4/release/qiime2-2021.4-py38-${platformName}-conda.yml`

    default:
      return `https://raw.githubusercontent.com/qiime2/environment-files/master/2021.4/release/qiime2-2021.4-py38-${platformName}-conda.yml`
  }
}

async function updateLibrary(payload: any) {
    let urlEncodedDataPairs: any = []
    for (let name in payload) {
        urlEncodedDataPairs.push(`${encodeURIComponent(name)}=${encodeURIComponent(payload[name])}`)
    }

    const urlEncodedData: string = urlEncodedDataPairs.join('&').replace(/%20/g, '+')

    let client: http.HttpClient = new http.HttpClient('library-client', [], {
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
    })

    try {
        let result: any = await client.post(
            'https://library.qiime2.org/api/v1/packages/integrate/',
            urlEncodedData
        )
    } catch (error) {
        core.setFailed(error.toString())
    }
}

async function main(): Promise<void> {
  try {
    // artifact-caching //
    const artifactClient = artifact.create()
    const uploadResult = await artifactClient.uploadArtifact(arch[1], files, buildDir)

    // testing //
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

    // lib-token //
    if (token !== '' && process.env.GITHUB_EVENT_NAME !== 'pull_request') {
        updateLibrary({
            token,
            version: 'unknown',
            package_name: packageName,
            repository: process.env.GITHUB_REPOSITORY,
            run_id: process.env.GITHUB_RUN_ID,
            artifact_name: getArtifactName(),
        })
    }

  } catch (error) {
    core.setFailed(error.message)
  }
}

main()
