<template>
  <div class="home-page">
    <div class="sidebar">
      <h3>Filter by Tag</h3>
      <button
        :class="['tag-btn', files.activeTagFilter === '' ? 'active' : '']"
        @click="files.setTagFilter('')"
      >
        All Files
      </button>
      <button
        v-for="tag in availableTags"
        :key="tag.id"
        :class="['tag-btn', files.activeTagFilter === tag.name ? 'active' : '']"
        @click="files.setTagFilter(tag.name)"
      >
        {{ tag.name }}
      </button>
    </div>

    <div class="main-content">
      <FileUpload @uploaded="onUploaded" />
      <FileList />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useFilesStore } from '../stores/files.js'
import { listTags } from '../api.js'
import FileUpload from '../components/FileUpload.vue'
import FileList from '../components/FileList.vue'

const files = useFilesStore()
const availableTags = ref([])

async function loadTags() {
  const res = await listTags()
  availableTags.value = res.data
}

async function onUploaded() {
  await loadTags()
}

onMounted(async () => {
  await files.fetchFiles()
  await loadTags()
})
</script>

<style scoped>
.home-page {
  display: flex;
  gap: 1.5rem;
  padding: 1.5rem 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.sidebar {
  width: 180px;
  flex-shrink: 0;
}

.sidebar h3 {
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #888;
  margin-bottom: 0.75rem;
}

.tag-btn {
  display: block;
  width: 100%;
  text-align: left;
  padding: 0.45rem 0.75rem;
  margin-bottom: 0.4rem;
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.15s;
}

.tag-btn:hover,
.tag-btn.active {
  background: #1a73e8;
  color: #fff;
  border-color: #1a73e8;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
</style>
