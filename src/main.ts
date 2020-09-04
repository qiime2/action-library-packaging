import * as temp from 'temp'
import * as os from 'os'

import * as artifact from '@actions/artifact'
import * as core from '@actions/core'
import * as exec from '@actions/exec'
import * as glob from '@actions/glob'
import * as io from '@actions/io'

class ExecOptions {
  public listeners: object = {}
}

async function execWrapper(commandLine: string,
                           args?: string[],
                           errorMessage?: string) {
    let output = ''
    let error = ''

    let options = new ExecOptions
    options.listeners = {
      stdout: (data: Buffer) => {
        output += data.toString()
      },
      stderr: (data: Buffer) => {
        error += data.toString()
      }
    }

    try {
      await exec.exec(commandLine, args, options)
    } catch (error) {
      core.setFailed(error.message + `\n\n${errorMessage}`);
    }
}

function getCondaURL(): string {
    let condaURL = ''
    if (os.platform() === 'linux') {
      condaURL = 'https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh'
    } else if (os.platform() === 'darwin' ) {
      condaURL = 'https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh'
    } else {
      throw Error('Unsupported OS, must be Linux or Mac')
    }

    return condaURL
}

async function installMiniconda(homeDir: string | undefined, condaURL: string) {
    const minicondaDir = `${homeDir}/miniconda`
    const minicondaBinDir = `${minicondaDir}/bin`

    core.addPath(minicondaBinDir);

    await execWrapper('wget', ['-O', 'miniconda.sh', condaURL])
    await execWrapper('chmod', ['+x', 'miniconda.sh'])

    await execWrapper('./miniconda.sh', ['-b', '-p', minicondaDir])

    await execWrapper('conda', ['upgrade', '-n', 'base', '-q', '-y', '-c', 'defaults', '--override-channels', 'conda'])
}

async function installCondaBuild() {
    const installMinicondaExitCode = await execWrapper('conda', ['install', '-n', 'base', '-q', '-y', '-c', 'defaults',
                                                       '--override-channels', 'conda-build', 'conda-verify'],
                                                       'miniconda install failed')
}

function getQIIME2Channel(buildTarget: string) {
  switch(buildTarget) {
    case 'staging':
      return 'qiime2-staging/label/r2020.11'

    case 'release':
    default:
      return 'qiime2/label/r2020.8'
  }
}

async function buildQIIME2Package(buildDir: string, recipePath: string, q2Channel: string) {
    return await execWrapper('conda',
      ['build',
       '-c', q2Channel,
       '-c', 'conda-forge',
       '-c', 'bioconda',
       '-c', 'defaults',
       '--override-channels',
       '--output-folder', buildDir,
       '--no-anaconda-upload',
       recipePath], 'package building failed')
}

async function main(): Promise<void> {
  try {
    const homeDir: string | undefined = process.env.HOME
    const buildDir = `${homeDir}/built-package`
    const recipePath: string = core.getInput('recipe-path')
    const buildTarget: string = core.getInput('build-target')
    const condaURL = getCondaURL()
    const q2Channel = getQIIME2Channel(buildTarget)

    await installMiniconda(homeDir, condaURL)
    await installCondaBuild()
    await buildQIIME2Package(buildDir, recipePath, q2Channel)

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
      await execWrapper('conda', ['create', '-n', 'testing', '-c', `${buildDir}`, '-c', q2Channel,
                                  '-c', 'conda-forge', '-c', 'bioconda', '-c', 'defaults', `${pluginName}`, 'pytest', '-y'])

      temp.track()
      const stream = temp.createWriteStream({ suffix: '.sh' })
      stream.write(`source activate testing && ${additionalTests}`)
      stream.end()
      const additionalTestsExitCode = await execWrapper('bash', [stream.path as string], 'additional tests failed')
    }

  } catch (error) {
    core.setFailed(error.message);
  }
}

main();
