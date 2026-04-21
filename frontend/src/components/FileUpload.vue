<template>
  <div class="upload-card">
    <h2>Upload File</h2>
    <form @submit.prevent="handleUpload">
      <div
        class="drop-zone"
        :class="{ dragging }"
        @dragover.prevent="dragging = true"
        @dragleave.prevent="dragging = false"
        @drop.prevent="onDrop"
        @click="fileInput.click()"
      >
        <span v-if="!selectedFile">Click or drag a file here</span>
        <span v-else class="file-name">📄 {{ selectedFile.name }}</span>
        <input
          ref="fileInput"
          type="file"
          style="display: none"
          @change="onFileChange"
        />
      </div>

      <label>Tags (comma-separated)</label>
      <input v-model="tags" type="text" placeholder="e.g. work, photos, 2024" />

      <button
        type="submit"
        class="btn-upload"
        :disabled="!selectedFile || uploading"
      >
        {{ uploading ? 'Uploading…' : 'Upload' }}
      </button>

      <p v-if="error" class="error">{{ error }}</p>
      <p v-if="success" class="success">✓ File uploaded successfully</p>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useFilesStore } from '../stores/files.js'

const emit = defineEmits(['uploaded'])
const files = useFilesStore()

const fileInput = ref(null)
const selectedFile = ref(null)
const tags = ref('')
const uploading = ref(false)
const error = ref('')
const success = ref(false)
const dragging = ref(false)

function onFileChange(e) {
  selectedFile.value = e.target.files[0] || null
}

function onDrop(e) {
  dragging.value = false
  selectedFile.value = e.dataTransfer.files[0] || null
}

async function handleUpload() {
  if (!selectedFile.value) return
  error.value = ''
  success.value = false
  uploading.value = true
  try {
    await files.upload(selectedFile.value, tags.value)
    success.value = true
    selectedFile.value = null
    tags.value = ''
    if (fileInput.value) fileInput.value.value = ''
    emit('uploaded')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Upload failed'
  } finally {
    uploading.value = false
  }
}
</script>

<style scoped>
.upload-card {
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

form {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.drop-zone {
  border: 2px dashed #1a73e8;
  border-radius: 6px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  color: #1a73e8;
  transition: background 0.15s;
}

.drop-zone.dragging {
  background: #e8f0fe;
}

.drop-zone:hover {
  background: #f1f8ff;
}

.file-name {
  font-weight: 600;
  color: #333;
}

label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #555;
}

input[type='text'] {
  padding: 0.5rem 0.8rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.btn-upload {
  padding: 0.65rem;
  background: #1a73e8;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
}

.btn-upload:hover:not(:disabled) {
  background: #1558b0;
}

.btn-upload:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.error {
  color: #d32f2f;
  font-size: 0.875rem;
}

.success {
  color: #388e3c;
  font-size: 0.875rem;
}
</style>
