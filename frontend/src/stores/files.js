import { defineStore } from 'pinia'
import { ref } from 'vue'
import { listFiles, uploadFile, deleteFile, updateFileTags } from '../api.js'

export const useFilesStore = defineStore('files', () => {
  const files = ref([])
  const loading = ref(false)
  const activeTagFilter = ref('')

  async function fetchFiles() {
    loading.value = true
    try {
      const res = await listFiles(activeTagFilter.value || null)
      files.value = res.data
    } finally {
      loading.value = false
    }
  }

  async function upload(file, tags) {
    await uploadFile(file, tags)
    await fetchFiles()
  }

  async function remove(id) {
    await deleteFile(id)
    files.value = files.value.filter((f) => f.id !== id)
  }

  async function setTags(id, tagNames) {
    await updateFileTags(id, tagNames)
    await fetchFiles()
  }

  function setTagFilter(tag) {
    activeTagFilter.value = tag
    fetchFiles()
  }

  return { files, loading, activeTagFilter, fetchFiles, upload, remove, setTags, setTagFilter }
})
