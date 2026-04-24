<template>
  <div class="page">
    <nav class="navbar">
      <div class="navbar-brand">☁ Cloud Distributions</div>
      <div class="navbar-links">
        <router-link to="/cloud" class="nav-link">Cloud</router-link>
        <router-link to="/settings" class="nav-link">Settings</router-link>
        <router-link to="/" class="nav-link">Home</router-link>
      </div>
    </nav>

    <header class="header">
      <h1>Edit Cloud Item</h1>
      <p>Update the file name, description, and attached tags.</p>
    </header>

    <section class="form-card">
      <form @submit.prevent="handleSave" class="item-form">
        <label for="description">Item Description</label>
        <textarea
          id="description"
          v-model.trim="description"
          rows="4"
          placeholder="Describe this file..."
          required
        ></textarea>

        <label for="fileName">File Name</label>
        <input
          id="fileName"
          v-model.trim="fileName"
          type="text"
          placeholder="Enter display file name"
          required
        />

        <div class="tags-block">
          <p class="label-like">Tags</p>
          <div class="tag-entry-row">
            <input
              v-model.trim="pendingTag"
              type="text"
              class="tag-input"
              placeholder="Type a tag and store it"
              list="existing-tags"
              @keydown.enter.prevent="storePendingTag"
            />
            <button type="button" class="store-tag-btn" @click="storePendingTag">
              Store
            </button>
          </div>

          <datalist id="existing-tags">
            <option v-for="tag in availableTags" :key="tag.id" :value="tag.name" />
          </datalist>

          <div v-if="tagsLoading" class="tags-status">Loading tag suggestions...</div>
          <div v-else-if="tagsError" class="tags-status error">{{ tagsError }}</div>

          <div v-if="stagedTags.length === 0" class="tags-status">
            No tags stored yet.
          </div>

          <div v-else class="staged-tags-list">
            <div v-for="tag in stagedTags" :key="tag" class="staged-tag-item">
              <span>{{ tag }}</span>
              <button
                type="button"
                class="remove-tag-btn"
                aria-label="Remove tag"
                @click="removeTag(tag)"
              >
                ×
              </button>
            </div>
          </div>
        </div>

        <div class="actions">
          <button type="button" class="btn-secondary" @click="goBack" :disabled="saving || loading">
            Cancel
          </button>
          <button type="submit" class="btn-primary" :disabled="saving || loading">
            {{ saving ? 'Saving...' : 'Save Changes' }}
          </button>
        </div>

        <p v-if="error" class="message error">{{ error }}</p>
        <p v-if="success" class="message success">{{ success }}</p>
      </form>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getFile, listTags, updateFileTags } from '../api.js'
import { readFileMetadata, writeFileMetadata } from '../utils/fileMetadata.js'

const route = useRoute()
const router = useRouter()

const fileId = Number(route.params.id)

const loading = ref(false)
const saving = ref(false)
const error = ref('')
const success = ref('')

const description = ref('')
const fileName = ref('')
const pendingTag = ref('')
const stagedTags = ref([])

const availableTags = ref([])
const tagsLoading = ref(false)
const tagsError = ref('')

onMounted(async () => {
  if (!Number.isFinite(fileId) || fileId <= 0) {
    error.value = 'Invalid file id.'
    return
  }

  loading.value = true
  tagsLoading.value = true
  error.value = ''
  tagsError.value = ''

  try {
    const [fileResponse, tagsResponse] = await Promise.all([getFile(fileId), listTags()])
    const file = fileResponse?.data || {}
    const metadata = readFileMetadata(fileId)

    fileName.value = String(metadata.displayName || file.original_filename || '').trim()
    description.value = String(metadata.description || '').trim()

    stagedTags.value = (Array.isArray(file.tags) ? file.tags : [])
      .map((tag) => String(tag?.name || '').trim().toLowerCase())
      .filter(Boolean)

    availableTags.value = Array.isArray(tagsResponse?.data) ? tagsResponse.data : []
  } catch (e) {
    const detail = e?.response?.data?.detail
    if (typeof detail === 'string') {
      error.value = detail
    } else {
      error.value = 'Failed to load item details.'
    }
  } finally {
    loading.value = false
    tagsLoading.value = false
  }
})

function storePendingTag() {
  const normalized = pendingTag.value.trim().toLowerCase()
  if (!normalized) return
  if (!stagedTags.value.includes(normalized)) {
    stagedTags.value = [...stagedTags.value, normalized]
  }
  pendingTag.value = ''
}

function removeTag(tagName) {
  stagedTags.value = stagedTags.value.filter((tag) => tag !== tagName)
}

async function handleSave() {
  error.value = ''
  success.value = ''

  if (!fileName.value.trim()) {
    error.value = 'File name is required.'
    return
  }

  if (!description.value.trim()) {
    error.value = 'Item description is required.'
    return
  }

  saving.value = true
  try {
    await updateFileTags(fileId, stagedTags.value)
    writeFileMetadata(fileId, {
      displayName: fileName.value,
      description: description.value,
    })

    success.value = 'Item updated successfully. Redirecting to cloud page...'
    setTimeout(() => {
      router.push('/cloud')
    }, 700)
  } catch (e) {
    error.value = e?.response?.data?.detail || 'Failed to save item changes.'
  } finally {
    saving.value = false
  }
}

function goBack() {
  router.push('/cloud')
}
</script>

<style scoped>
.page {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 24px 24px;
  font-family: Arial, sans-serif;
  background: #f7f9fc;
  min-height: 100vh;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  margin-bottom: 16px;
}

.navbar-brand {
  font-size: 1.35rem;
  font-weight: 700;
  color: #1f2937;
}

.navbar-links {
  display: flex;
  align-items: center;
  gap: 10px;
}

.nav-link {
  text-decoration: none;
  color: #1d4ed8;
  font-weight: 600;
  padding: 8px 10px;
  border-radius: 8px;
}

.nav-link:hover,
.nav-link.router-link-active {
  background: #dbeafe;
}

.header {
  text-align: center;
  margin-bottom: 22px;
}

.header h1 {
  margin-bottom: 8px;
  color: #222;
}

.header p {
  color: #555;
}

.form-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 20px;
}

.item-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

label,
.label-like {
  font-size: 14px;
  font-weight: 600;
  color: #334155;
}

textarea,
input[type='text'] {
  width: 100%;
  box-sizing: border-box;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 10px;
  font-size: 15px;
  background: #fff;
}

textarea:focus,
input[type='text']:focus {
  outline: 2px solid #93c5fd;
  border-color: #2563eb;
}

.tags-block {
  margin-top: 4px;
}

.tag-entry-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
  margin-top: 6px;
}

.store-tag-btn {
  border: none;
  background: #2563eb;
  color: white;
  border-radius: 8px;
  padding: 0 14px;
  font-weight: 600;
  cursor: pointer;
}

.store-tag-btn:hover {
  background: #1d4ed8;
}

.tags-status {
  margin-top: 8px;
  font-size: 0.9rem;
  color: #64748b;
}

.tags-status.error {
  color: #b91c1c;
}

.staged-tags-list {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.staged-tag-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 1px solid #bfdbfe;
  background: #eff6ff;
  color: #1e40af;
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 0.86rem;
}

.remove-tag-btn {
  border: none;
  background: transparent;
  color: inherit;
  cursor: pointer;
  font-size: 14px;
  line-height: 1;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 8px;
}

.btn-primary,
.btn-secondary {
  border: none;
  border-radius: 8px;
  padding: 10px 14px;
  font-weight: 600;
  cursor: pointer;
}

.btn-primary {
  background: #2563eb;
  color: #fff;
}

.btn-primary:hover:not(:disabled) {
  background: #1d4ed8;
}

.btn-secondary {
  background: #e2e8f0;
  color: #1f2937;
}

.btn-secondary:hover:not(:disabled) {
  background: #cbd5e1;
}

.btn-primary:disabled,
.btn-secondary:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.message {
  margin-top: 8px;
  font-size: 0.92rem;
}

.message.error {
  color: #b91c1c;
}

.message.success {
  color: #166534;
}
</style>
