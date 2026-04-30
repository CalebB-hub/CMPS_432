<template>
  <div class="file-preview">
    <!-- Image preview -->
    <img
      v-if="fileType === 'image' && imageBlobUrl"
      :src="imageBlobUrl"
      :alt="file.original_filename"
      class="preview-image"
    />
    
    <!-- Video preview (first frame) -->
    <div
      v-else-if="fileType === 'video' && !videoExtractFailed"
      class="video-preview"
    >
      <img
        v-if="videoFrame"
        :src="videoFrame"
        :alt="file.original_filename"
        class="preview-image"
      />
      <div v-else class="preview-loading">
        <svg class="spinner" viewBox="0 0 50 50">
          <circle cx="25" cy="25" r="20" fill="none" stroke="#999" stroke-width="4" />
        </svg>
      </div>
      <div class="video-badge">▶</div>
    </div>
    
    <!-- Icon for text, audio, unknown, etc. -->
    <div v-else class="preview-icon">
      <!-- Text/PDF Icon -->
      <svg v-if="fileType === 'text' || fileType === 'pdf'" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
        <rect x="8" y="4" width="48" height="56" rx="2" fill="#f5f5f5" stroke="#999" stroke-width="2"/>
        <line x1="12" y1="14" x2="52" y2="14" stroke="#666" stroke-width="1.5"/>
        <line x1="12" y1="22" x2="52" y2="22" stroke="#666" stroke-width="1.5"/>
        <line x1="12" y1="30" x2="52" y2="30" stroke="#666" stroke-width="1.5"/>
        <line x1="12" y1="38" x2="42" y2="38" stroke="#666" stroke-width="1.5"/>
        <line x1="12" y1="46" x2="46" y2="46" stroke="#666" stroke-width="1.5"/>
      </svg>
      
      <!-- Audio Icon -->
      <svg v-else-if="fileType === 'audio'" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
        <rect x="8" y="4" width="48" height="56" rx="2" fill="#fff3e0" stroke="#ff9800" stroke-width="2"/>
        <circle cx="32" cy="32" r="8" fill="none" stroke="#ff9800" stroke-width="2"/>
        <path d="M 22 32 Q 22 24 32 24 Q 42 24 42 32" fill="none" stroke="#ff9800" stroke-width="1.5"/>
        <path d="M 18 32 Q 18 20 32 20 Q 46 20 46 32" fill="none" stroke="#ff9800" stroke-width="1.5"/>
      </svg>
      
      <!-- Video Icon -->
      <svg v-else-if="fileType === 'video'" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
        <rect x="8" y="4" width="48" height="56" rx="2" fill="#f3e5f5" stroke="#7b1fa2" stroke-width="2"/>
        <polygon points="32,22 48,32 32,42" fill="#7b1fa2"/>
        <circle cx="28" cy="32" r="4" fill="none" stroke="#7b1fa2" stroke-width="2"/>
      </svg>
      
      <!-- Document Icon (default) -->
      <svg v-else viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
        <rect x="8" y="4" width="48" height="56" rx="2" fill="#e3f2fd" stroke="#1976d2" stroke-width="2"/>
        <path d="M 48 4 L 48 16 Q 48 20 44 20 L 8 20" fill="#e8eaf6" stroke="#1976d2" stroke-width="1"/>
      </svg>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { getFileType, extractVideoFrame, fetchImageBlob } from '../utils/filePreview.js'

const props = defineProps({
  file: {
    type: Object,
    required: true,
  },
})

const videoFrame = ref(null)
const videoExtractFailed = ref(false)
const imageBlobUrl = ref(null)
const videoBlobUrl = ref(null)
const fileType = computed(() => getFileType(props.file.content_type))

// Get the preview URL - either from download_url (S3) or construct from file ID
const previewUrl = computed(() => {
  if (props.file.download_url) return props.file.download_url
  // Fallback to API download endpoint
  const apiBase = import.meta.env.VITE_API_BASE || '/api'
  return `${apiBase}/files/${props.file.id}/download`
})

onMounted(async () => {
  // Fetch image as blob if it's an image
  if (fileType.value === 'image') {
    try {
      imageBlobUrl.value = await fetchImageBlob(props.file.id)
    } catch (error) {
      console.error('Failed to fetch image:', error)
    }
  }
  
  // For videos, fetch as blob and extract frame
  if (fileType.value === 'video') {
    try {
      // Fetch video as blob to get a URL we can use for extraction
      const response = await fetch(previewUrl.value, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      })
      if (!response.ok) throw new Error('Failed to fetch video')
      const blob = await response.blob()
      videoBlobUrl.value = URL.createObjectURL(blob)
      videoFrame.value = await extractVideoFrame(videoBlobUrl.value)
    } catch (error) {
      console.error('Failed to extract video frame:', error)
      videoExtractFailed.value = true
    }
  }
})

// Clean up blob URLs when component unmounts
onBeforeUnmount(() => {
  if (imageBlobUrl.value) URL.revokeObjectURL(imageBlobUrl.value)
  if (videoBlobUrl.value) URL.revokeObjectURL(videoBlobUrl.value)
})
</script>

<style scoped>
.file-preview {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  border-radius: 4px;
  background: #f5f5f5;
  position: relative;
  flex-shrink: 0;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 4px;
}

.preview-icon {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
  box-sizing: border-box;
}

.preview-icon svg {
  width: 100%;
  height: 100%;
}

.video-preview {
  position: relative;
  width: 100%;
  height: 100%;
}

.video-badge {
  position: absolute;
  bottom: 2px;
  right: 2px;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}

.preview-loading {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.spinner {
  width: 30px;
  height: 30px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
