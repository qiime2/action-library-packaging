const artifact = require('@actions/artifact');
const glob = require('@actions/glob');
const core = require('@actions/core');

try {
    const filesGlobber = glob.create(`${process.env.BUILD_DIR}/*/**`);
    const files = filesGlobber.glob();

    const artifactClient = artifact.create();
    artifactClient.uploadArtifact(process.env.ARTIFACT_NAME, files, process.env.BUILD_DIR);
} catch (error) {
    core.setFailed(error.message);
}