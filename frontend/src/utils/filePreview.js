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
    const context = canvas.getContext('2d')

    const candidateTimes = []
    const addCandidateTime = (time) => {
      if (!Number.isFinite(time) || time <= 0) return
      const rounded = Math.max(0.05, Number(time.toFixed(2)))
      if (!candidateTimes.includes(rounded)) candidateTimes.push(rounded)
    }

    const isLikelyBlackFrame = () => {
      const sampleWidth = Math.min(canvas.width || 1, 24)
      const sampleHeight = Math.min(canvas.height || 1, 24)
      const sampleCanvas = document.createElement('canvas')
      sampleCanvas.width = sampleWidth
      sampleCanvas.height = sampleHeight
      const sampleContext = sampleCanvas.getContext('2d')
      sampleContext.drawImage(video, 0, 0, sampleWidth, sampleHeight)

      const imageData = sampleContext.getImageData(0, 0, sampleWidth, sampleHeight).data
      let totalLuminance = 0
      let totalVariance = 0
      const pixelCount = imageData.length / 4

      for (let index = 0; index < imageData.length; index += 4) {
        const red = imageData[index]
        const green = imageData[index + 1]
        const blue = imageData[index + 2]
        const luminance = 0.2126 * red + 0.7152 * green + 0.0722 * blue
        totalLuminance += luminance
        totalVariance += Math.abs(red - green) + Math.abs(green - blue) + Math.abs(red - blue)
      }

      const averageLuminance = totalLuminance / pixelCount
      const averageVariance = totalVariance / pixelCount
      return averageLuminance < 18 || averageVariance < 8
    }

    const captureFrameAtCurrentTime = () => {
      canvas.width = video.videoWidth || 1
      canvas.height = video.videoHeight || 1
      context.drawImage(video, 0, 0)
      if (isLikelyBlackFrame()) return null
      return canvas.toDataURL('image/jpeg', 0.8)
    }

    const tryCaptureNextFrame = async () => {
      while (candidateTimes.length > 0) {
        const nextTime = candidateTimes.shift()
        try {
          await new Promise((resolveSeek, rejectSeek) => {
            const onSeeked = () => {
              cleanup()
              resolveSeek()
            }
            const onSeekError = () => {
              cleanup()
              rejectSeek(new Error('Failed to seek video'))
            }
            const cleanup = () => {
              video.removeEventListener('seeked', onSeeked)
              video.removeEventListener('error', onSeekError)
            }
            video.addEventListener('seeked', onSeeked, { once: true })
            video.addEventListener('error', onSeekError, { once: true })
            video.currentTime = nextTime
          })

          const frame = captureFrameAtCurrentTime()
          if (frame) {
            resolve(frame)
            return
          }
        } catch {
          // Keep trying later timestamps.
        }
      }

      reject(new Error('No usable video frame found'))
    }
    
    // Set up video element
    video.preload = 'auto'
    video.muted = true
    video.playsInline = true
    
    video.addEventListener('error', () => {
      reject(new Error('Failed to load video'))
    })
    
    video.addEventListener('loadedmetadata', () => {
      candidateTimes.length = 0
      addCandidateTime(0.25)
      addCandidateTime(0.75)
      addCandidateTime(1.5)
      addCandidateTime(3)
      addCandidateTime(video.duration * 0.05)
      addCandidateTime(video.duration * 0.15)
      addCandidateTime(video.duration * 0.35)
      addCandidateTime(video.duration * 0.6)

      // Try the first frame only as a last resort after the later timestamps.
      candidateTimes.push(0)
      tryCaptureNextFrame()
    }, { once: true })

    video.addEventListener('loadeddata', () => {
      if (candidateTimes.length === 0) {
        candidateTimes.push(0.25, 0.75, 1.5, 3)
        tryCaptureNextFrame()
      }
    }, { once: true })

    // Start loading video
    video.src = videoUrl
  })
}
