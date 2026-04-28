const STORAGE_KEY = 'cloud_file_metadata_v1'

export function readFileMetadataMap() {
  try {
    const rawValue = localStorage.getItem(STORAGE_KEY)
    if (!rawValue) return {}
    const parsed = JSON.parse(rawValue)
    return parsed && typeof parsed === 'object' ? parsed : {}
  } catch {
    return {}
  }
}

export function readFileMetadata(fileId) {
  const metadataMap = readFileMetadataMap()
  return metadataMap[String(fileId)] || {}
}

export function writeFileMetadata(fileId, metadata) {
  const metadataMap = readFileMetadataMap()
  metadataMap[String(fileId)] = {
    displayName: String(metadata?.displayName || '').trim(),
    description: String(metadata?.description || '').trim(),
    updatedAt: new Date().toISOString(),
  }
  localStorage.setItem(STORAGE_KEY, JSON.stringify(metadataMap))
}