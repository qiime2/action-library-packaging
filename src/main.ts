import * as temp from 'temp'
import * as os from 'os'

import * as artifact from '@actions/artifact'
import * as core from '@actions/core'
import * as exec from '@actions/exec'
import * as glob from '@actions/glob'
import * as io from '@actions/io'

async function main(): Promise<void> {
  try {
    const homeDir: string | undefined = process.env.HOME
    const buildDir = `${homeDir}/built-package`
    const minicondaDir = `${homeDir}/miniconda`
    const minicondaBinDir = `${minicondaDir}/bin`
    const channels = '-c qiime2-staging/label/r2020.6 -c conda-forge -c bioconda -c defaults'

    core.addPath(minicondaBinDir);

    // TODO: fix these hacks
    core.addPath('../../_actions/qiime2/action-library-packaging/alpha1')
    core.addPath('.')

    let condaURL = ''
    if (os.platform() === 'linux') {
      condaURL = 'https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh'
    } else if (os.platform() === 'darwin' ) {
      condaURL = 'https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh'
    } else {
      throw Error('Unsupported OS, must be Linux or Mac')
    }

    await exec.exec('wget', ['-O', 'miniconda.sh', condaURL])
    await exec.exec('chmod', ['+x', 'miniconda.sh'])

    await exec.exec('./miniconda.sh', ['-b', '-p', minicondaDir])

    await exec.exec('conda', ['upgrade', '-n', 'base', '-q', '-y', '-c', 'defaults', '--override-channels', 'conda'])
    const installMinicondaExitCode = await exec.exec('conda', ['n', 'base', '-q', '-y', '-c', 'defaults', '--override-channels', 'conda-build', 'conda-verify'])
    if (installMinicondaExitCode !== 0) {
      throw Error('miniconda install failed')
    }

    const recipePath: string = core.getInput('recipe-path')
    const buildPackScriptExitCode = await exec.exec(`conda build ${channels}`, ['--override-channels',
                                                                                '--output-folder', buildDir,
                                                                                '--no-anaconda-upload', recipePath])
    if (buildPackScriptExitCode !== 0) {
      throw Error('package building failed')
    }

    const filesGlobber: glob.Globber = await glob.create(`${buildDir}/*/**`)
    const files: string[] = await filesGlobber.glob()

    const pluginName: string = core.getInput('plugin-name')
    const artifactGlobber: glob.Globber = await glob.create(`${buildDir}/*/${pluginName}*`)
    const artifactName: string[] = await artifactGlobber.glob()

    if (artifactName === null || artifactName.length !== 1) {
      throw Error(`Error finding base artifactName: ${JSON.stringify(artifactName)}`)
    }

    const regex: RegExp = new RegExp(`${buildDir}\/(.*?)\/${pluginName}`)
    const arch: RegExpMatchArray | null = artifactName[0].match(regex)

    if (arch === null) {
      throw Error(`Error finding arch: ${JSON.stringify(arch)}.`)
    }

    const artifactClient = artifact.create()
    const uploadResult = await artifactClient.uploadArtifact(arch[1], files, buildDir)
    core.debug(JSON.stringify(uploadResult))

    const additionalTests: string = core.getInput('additional-tests')
    if (additionalTests !== '') {
      await exec.exec(`conda create -n testing -c ${buildDir} ${channels} ${pluginName} pytest -y`)

      temp.track()
      const stream = temp.createWriteStream({ suffix: '.sh' })
      stream.write(`source activate testing && ${additionalTests}`)
      stream.end()
      const additionalTestsExitCode = await exec.exec('bash', [stream.path as string])

      if (additionalTestsExitCode !== 0) {
        throw Error('additional tests failed')
      }
    }

  } catch (error) {
    core.setFailed(error.message);
  }
}

main();
