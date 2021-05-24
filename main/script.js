const exec = require('@actions/exec');
const core = require('@actions/core');

async function main() {
    try {
        await exec.exec('bash all.sh');
    } catch (error) {
        core.setFailed(error.message);
    }
}

core.addPath(`${__dirname}/bin`);
core.addPath(`${__dirname}/bin/artifact-upload`);
main().catch(core.setFailed);
