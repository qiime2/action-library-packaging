#!/usr/bin/env bash    
    
# build
# run conda-build
sudo conda build \
    -c q2Channel \
    -c conda-forge \
    -c bioconda \
    -c defaults \
    --override-channels \
    --output-folder $BUILD_DIR \
    --no-anaconda-upload \
    $RECIPE_PATH


const filesGlobber: glob.Globber = await glob.create(`${buildDir}/*/**`)
const files: string[] = await filesGlobber.glob()
# ${buildDir} = $BUILD_DIR
# searching for $BUILD_DIR environment variable
# files-grep = grep $BUILD_DIR$
# string[] = 


const artifactGlobber: glob.Globber = await glob.create(`${buildDir}/*/${packageName}*`)
const artifactName: string[] = await artifactGlobber.glob()

core.info(artifactName[0])

if [ -z "artifactName" ] && [ artifactName.length -ne 1 ]; then
printf '%s/n' "Error finding base artifactName: ${JSON.stringify(artifactName)}" >&2
exit 1
fi

const regex: RegExp = new RegExp(`${buildDir}\/(.*?)\/${packageName}`)
const arch: RegExpMatchArray | null = artifactName[0].match(regex)

if [ -z arch ]; then
printf '%s/n' "Error finding arch: ${JSON.stringify(arch)}." >&2
exit 1
fi