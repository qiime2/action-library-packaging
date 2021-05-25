const exec = require('@actions/exec');
const core = require('@actions/core');
const path = require('path');

async function main() {
    try {
        await exec.exec('alp-1c8c84a3-all.sh');
    } catch (error) {
        core.setFailed(error.message);
    }
}

core.addPath(path.resolve(__dirname, '..', 'bin'));
core.addPath(path.resolve(__dirname, '..', 'bin', 'artifact-upload'));

main().catch(core.setFailed);
