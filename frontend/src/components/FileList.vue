<template>
  <div class="file-list-card">
    <h2>My Files</h2>

    <div v-if="files.loading" class="loading">Loading…</div>

    <div v-else-if="files.files.length === 0" class="empty">
      No files found. Upload one to get started!
    </div>

    <table v-else class="file-table">
      <thead>
        <tr>
          <th>Name</th>
          <th>Size</th>
          <th>Tags</th>
          <th>Uploaded</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="file in files.files" :key="file.id">
          <td class="filename">{{ file.original_filename }}</td>
          <td>{{ formatSize(file.size) }}</td>
          <td>
            <span
              v-for="tag in file.tags"
              :key="tag.id"
              class="tag-chip"
              @click="files.setTagFilter(tag.name)"
            >
              {{ tag.name }}
            </span>
            <span v-if="file.tags.length === 0" class="no-tags">—</span>
          </td>
          <td>{{ formatDate(file.uploaded_at) }}</td>
          <td>
            <button class="btn-delete" @click="handleDelete(file.id)">🗑</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { useFilesStore } from '../stores/files.js'

const files = useFilesStore()

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 ** 2) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 ** 2).toFixed(1)} MB`
}

function formatDate(iso) {
  return new Date(iso).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

async function handleDelete(id) {
  if (!confirm('Delete this file?')) return
  await files.remove(id)
}
</script>

<style scoped>
.file-list-card {
  background: #fff;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.08);
}

h2 {
  font-size: 1.1rem;
  margin-bottom: 1rem;
  color: #333;
}

.loading,
.empty {
  color: #888;
  padding: 1.5rem 0;
  text-align: center;
}

.file-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.file-table th {
  text-align: left;
  padding: 0.5rem 0.75rem;
  border-bottom: 2px solid #eee;
  color: #666;
  font-size: 0.8rem;
  text-transform: uppercase;
}

.file-table td {
  padding: 0.65rem 0.75rem;
  border-bottom: 1px solid #f0f0f0;
  vertical-align: middle;
}

.filename {
  font-weight: 500;
  max-width: 220px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tag-chip {
  display: inline-block;
  padding: 0.2rem 0.55rem;
  margin: 0.1rem;
  background: #e8f0fe;
  color: #1a73e8;
  border-radius: 12px;
  font-size: 0.78rem;
  cursor: pointer;
}

.tag-chip:hover {
  background: #1a73e8;
  color: #fff;
}

.no-tags {
  color: #ccc;
}

.btn-delete {
  background: none;
  border: none;
  font-size: 1.1rem;
  cursor: pointer;
  opacity: 0.6;
  transition: opacity 0.15s;
}

.btn-delete:hover {
  opacity: 1;
}
</style>
