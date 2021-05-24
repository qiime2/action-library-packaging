const exec = require('@actions/exec');
const core = require('@actions/core');
const path = require('path');

async function main() {
    try {
        await exec.exec('bash all.sh');
    } catch (error) {
        core.setFailed(error.message);
    }
}

console.log(process.env.PATH);
core.addPath(`${path.resolve(__dirname, '..')}/bin`);
core.addPath(`${path.resolve(__dirname, '..')}/bin/artifact-upload`);
console.log('#########');
console.log(process.env.PATH);
main().catch(core.setFailed);
