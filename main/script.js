const exec = require('@actions/exec');
const core = require('@actions/core');
const path = require('path');

async function main() {
    try {
        await exec.exec(`bash ${path.resolve(__dirname, '..', 'bin', 'all.sh')}`);
    } catch (error) {
        core.setFailed(error.message);
    }
}

main().catch(core.setFailed);
