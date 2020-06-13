import * as temp from 'temp'
import * as os from 'os'

import * as artifact from '@actions/artifact'
import * as core from '@actions/core'
import * as exec from '@actions/exec'
import * as glob from '@actions/glob'
import * as io from '@actions/io'

// Anything we pass as the optional 3rd param to exec.exec must implement the
// ExecOptions interface here https://github.com/actions/toolkit/blob/master/packages/exec/src/interfaces.ts.
// The only piece of that we actually need is the listeners, this class exists to
// give us that.
class ExecOptions {
  public listeners: object = {}
}

// Maybe (if we can get it to work) we have a param for tacking on a new error
// message
async function execWrapper(commandLine: string,
                           args?: string[],
                           errorMessage?: string): Promise<number> {
    let myOutput = ''
    let myError = ''

    let options = new ExecOptions
    options.listeners = {
      stdout: (data: Buffer) => {
        myOutput += data.toString()
      },
      stderr: (data: Buffer) => {
        myError += data.toString()
      }
    }

    try {
      return await exec.exec(commandLine, args, options)
    } catch (error) {
      throw(errorMessage)
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
    const installMinicondaExitCode = await execWrapper('conda', ['install', 'base', '-q', '-y', '-c', 'defaults',
                                                       '--override-channels', 'conda-build', 'conda-verify'],
                                                       'miniconda install failed')
}

async function buildQIIME2Package(buildDir: string) {
    const recipePath: string = core.getInput('recipe-path')
    const buildPackScriptExitCode = await execWrapper('conda', ['build', '-c', 'qiime2-staging/label/r2020.6',
                                                                '-c', 'conda-forge', '-c', 'bioconda',
                                                                '-c', 'defaults', '--override-channels',
                                                                '--output-folder', buildDir,
                                                                '--no-anaconda-upload', recipePath])
    if (buildPackScriptExitCode !== 0) {
      throw Error('package building failed')
    }
}

async function main(): Promise<void> {
  try {
    const homeDir: string | undefined = process.env.HOME
    const buildDir = `${homeDir}/built-package`

    let condaURL = getCondaURL()
    await installMiniconda(homeDir, condaURL)
    await installCondaBuild()
    await buildQIIME2Package(buildDir)

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
      await execWrapper('conda', ['create', '-n', 'testing', '-c', `${buildDir}`, '-c', 'qiime2-staging/label/r2020.6',
                                  '-c', 'conda-forge', '-c', 'bioconda', '-c', 'defaults', `${pluginName}`, 'pytest', '-y'])

      temp.track()
      const stream = temp.createWriteStream({ suffix: '.sh' })
      stream.write(`source activate testing && ${additionalTests}`)
      stream.end()
      const additionalTestsExitCode = await execWrapper('bash', [stream.path as string])

      if (additionalTestsExitCode !== 0) {
        throw Error('additional tests failed')
      }
    }

  } catch (error) {
    core.setFailed(error.message);
  }
}

main();
