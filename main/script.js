const exec = require('@actions/exec');
const core = require('@actions/core');

async function main() {
    try {
        await exec.exec('bash ../bin/all.sh');
    } catch (error) {
        core.setFailed(error.message);
    }
}

main().catch(core.setFailed);