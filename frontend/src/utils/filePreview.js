/**
 * Utilities for file type detection and preview generation
 */

import axios from 'axios'

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

export function getFileType(contentType) {
  if (!contentType) return 'unknown'
  
  if (contentType.startsWith('image/')) return 'image'
  if (contentType.startsWith('video/')) return 'video'
  if (contentType.startsWith('audio/')) return 'audio'
  if (contentType.startsWith('text/')) return 'text'
  if (contentType === 'application/pdf') return 'pdf'
  if (contentType === 'application/json') return 'text'
  
  return 'unknown'
}

/**
 * Fetch an image from the API and return a blob URL
 */
export async function fetchImageBlob(fileId) {
  try {
    const response = await api.get(`/files/${fileId}/download`, {
      responseType: 'blob',
    })
    return URL.createObjectURL(response.data)
  } catch (error) {
    console.error('Failed to fetch image blob:', error)
    throw error
  }
}

/**
 * Extract the first frame of a video file
 * Returns a Promise that resolves with a canvas image data URL
 */
export async function extractVideoFrame(videoUrl) {
  return new Promise((resolve, reject) => {
    const video = document.createElement('video')
    const canvas = document.createElement('canvas')
    
    // Set up video element
    video.crossOrigin = 'use-credentials'
    video.addEventListener('loadedmetadata', () => {
      // Set canvas size to match video
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      
      // Draw first frame
      const ctx = canvas.getContext('2d')
      ctx.drawImage(video, 0, 0)
      
      // Get image data URL
      const dataUrl = canvas.toDataURL('image/jpeg', 0.8)
      resolve(dataUrl)
    })
    
    video.addEventListener('error', () => {
      reject(new Error('Failed to load video'))
    })
    
    // Start loading video
    video.src = videoUrl
  })
}
