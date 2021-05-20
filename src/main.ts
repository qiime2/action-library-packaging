async function updateLibrary(payload: any) {
    let urlEncodedDataPairs: any = []
    for (let name in payload) {
        urlEncodedDataPairs.push(`${encodeURIComponent(name)}=${encodeURIComponent(payload[name])}`)
    }

    const urlEncodedData: string = urlEncodedDataPairs.join('&').replace(/%20/g, '+')

    let client: http.HttpClient = new http.HttpClient('library-client', [], {
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
    })

    try {
        let result: any = await client.post(
            'https://library.qiime2.org/api/v1/packages/integrate/',
            urlEncodedData
        )
    } catch (error) {
        core.setFailed(error.toString())
    }
}

async function main(): Promise<void> {
  try {
    // artifact-caching //
    const artifactClient = artifact.create()
    const uploadResult = await artifactClient.uploadArtifact(arch[1], files, buildDir)

    // lib-token //
    if (token !== '' && process.env.GITHUB_EVENT_NAME !== 'pull_request') {
        updateLibrary({
            token,
            version: 'unknown',
            package_name: packageName,
            repository: process.env.GITHUB_REPOSITORY,
            run_id: process.env.GITHUB_RUN_ID,
            artifact_name: getArtifactName(),
        })
    }

  } catch (error) {
    core.setFailed(error.message)
  }
}

main()