<template>
  <div class="child-tag-form-overlay" @click="handleBackdropClick">
    <div class="child-tag-form" @click.stop>
      <h3>{{ isRootTag ? 'Create New Tag' : `Add child tag to "${parentTag.name}"` }}</h3>

      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="child-tag-input">{{ isRootTag ? 'Tag Name' : 'Child Tag Name' }}</label>
          <input
            id="child-tag-input"
            v-model.trim="tagName"
            type="text"
            :placeholder="isRootTag ? 'e.g. Electronics, Devices' : 'e.g. iPhone, MacBook'"
            :disabled="loading"
            @keyup.esc="handleCancel"
            autofocus
          />
        </div>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <div class="form-actions">
          <button type="submit" class="btn-create" :disabled="!tagName || loading">
            {{ loading ? 'Creating...' : 'Create' }}
          </button>
          <button
            type="button"
            class="btn-cancel"
            @click="handleCancel"
            :disabled="loading"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  parentTag: {
    type: Object,
    default: null,
  },
  isRootTag: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['create', 'cancel'])

const tagName = ref('')
const loading = ref(false)
const error = ref('')

const isRootTag = computed(() => props.isRootTag || !props.parentTag)

async function handleSubmit() {
  if (!tagName.value.trim()) {
    error.value = 'Tag name cannot be empty'
    return
  }

  loading.value = true
  error.value = ''

  try {
    emit('create', tagName.value)
  } catch (err) {
    error.value = err.message || 'Failed to create tag'
  } finally {
    loading.value = false
  }
}

function handleCancel() {
  emit('cancel')
}

function handleBackdropClick(e) {
  if (e.target === e.currentTarget) {
    handleCancel()
  }
}
</script>

<style scoped>
.child-tag-form-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.child-tag-form {
  background: #fff;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  width: 100%;
  max-width: 400px;
  animation: slideUp 0.2s ease;
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

h3 {
  margin: 0 0 1rem 0;
  color: #333;
  font-size: 1.1rem;
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.4rem;
  color: #555;
  font-size: 0.9rem;
  font-weight: 500;
}

input[type='text'] {
  width: 100%;
  padding: 0.6rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
  box-sizing: border-box;
  transition: border-color 0.15s ease;
}

input[type='text']:focus {
  outline: none;
  border-color: #4a90e2;
  box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.1);
}

input[type='text']:disabled {
  background-color: #f5f5f5;
  color: #999;
  cursor: not-allowed;
}

.error-message {
  padding: 0.6rem;
  margin-bottom: 1rem;
  background-color: #ffebee;
  border: 1px solid #ffcdd2;
  border-radius: 4px;
  color: #d32f2f;
  font-size: 0.85rem;
}

.form-actions {
  display: flex;
  gap: 0.8rem;
  justify-content: flex-end;
}

button {
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 4px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-create {
  background-color: #4a90e2;
  color: #fff;
}

.btn-create:hover:not(:disabled) {
  background-color: #357abd;
}

.btn-create:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.btn-cancel {
  background-color: #f0f0f0;
  color: #333;
}

.btn-cancel:hover:not(:disabled) {
  background-color: #e0e0e0;
}

.btn-cancel:disabled {
  color: #999;
  cursor: not-allowed;
}
</style>
