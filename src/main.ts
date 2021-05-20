async function main(): Promise<void> {
  try {
    // artifact-caching //
    const artifactClient = artifact.create()
    const uploadResult = await artifactClient.uploadArtifact(arch[1], files, buildDir)
}