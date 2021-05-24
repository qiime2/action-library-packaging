const exec = require('@actions/exec');
const core = require('@actions/core');
const path = require('path');

async function main() {
    try {
        await exec.exec('bash alp-7a862f3805c8-all.sh');
    } catch (error) {
        core.setFailed(error.message);
    }
}

core.addPath(`${path.resolve(__dirname, '..')}/bin`);
main().catch(core.setFailed);
