import axios from 'axios'
import { useAuthStore } from './stores/auth.js'

const base = import.meta.env.VITE_API_BASE || '/api'

const api = axios.create({
  baseURL: base,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle authentication errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const auth = useAuthStore()
      auth.logout()
      // Redirect to login if available
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// ── Auth ──────────────────────────────────────────────────────────────────────

export const register = (username, email, password) =>
  api.post('/auth/register', { username, email, password })

export const login = (username, password) => {
  const params = new URLSearchParams()
  params.append('username', username)
  params.append('password', password)
  return api.post('/auth/token', params)
}

export const getMe = () => api.get('/auth/me')

// ── Files ─────────────────────────────────────────────────────────────────────

export const listFiles = (tags = null) => {
  const params = tags ? { tags } : {}
  return api.get('/files/', { params })
}

export const uploadFile = (file, tags = '', tagParents = null) => {
  const form = new FormData()
  form.append('file', file)
  if (tags) form.append('tags', tags)
  if (tagParents && Object.keys(tagParents).length > 0) {
    form.append('tag_parents', JSON.stringify(tagParents))
  }
  return api.post('/files/', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export const deleteFile = (id) => api.delete(`/files/${id}`)

export const getFile = (id) => api.get(`/files/${id}`)

export const downloadFile = (id) =>
  api.get(`/files/${id}/download`, { responseType: 'blob' })

export const updateFileTags = (id, tagNames, tagParents = null) => {
  if (tagParents && Object.keys(tagParents).length > 0) {
    return api.patch(`/files/${id}/tags`, { tags: tagNames, tag_parents: tagParents })
  }
  return api.patch(`/files/${id}/tags`, tagNames)
}

// ── Tags ──────────────────────────────────────────────────────────────────────

export const listTags = () => api.get('/tags/')

export const getTagsHierarchy = () => api.get('/tags/hierarchy')

export const createTag = (name, parentId = null) => {
  if (parentId) {
    return api.post(`/tags/${parentId}/children`, { name })
  }
  return api.post('/tags/', { name, parent_id: parentId })
}

export const createChildTag = (parentId, name) =>
  api.post(`/tags/${parentId}/children`, { name })

export const updateTagParent = (tagId, parentId) =>
  api.patch(`/tags/${tagId}/parent`, { parent_id: parentId })

export const deleteTag = (id) => api.delete(`/tags/${id}`)
