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
    const channels = '-c conda-forge -c bioconda -c qiime2 -c defaults'

    core.addPath(minicondaBinDir);

    // TODO: fix these hacks
    core.addPath('../../_actions/thermokarst/busywork2_action_playground/master')
    core.addPath('.')

    const installMinicondaScript: string = await io.which('install_miniconda.sh', true)
    await exec.exec(`sh ${installMinicondaScript}`, [minicondaDir])
    // TODO: how to error if the exec above fails?

    const recipePath: string = core.getInput('recipe-path')
    const buildPackScript: string = await io.which('build_package.sh', true)
    await exec.exec(`sh ${buildPackScript}`, [recipePath, buildDir, channels])
    // TODO: how to error if the exec above fails?

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
      // TODO: if tests fail this still reports a success
      await exec.exec(`conda run -n testing ${additionalTests}`)
    }

  } catch (error) {
    core.setFailed(error.message);
  }
}

main();
