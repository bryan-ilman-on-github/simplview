/**
 * API client for communicating with the backend.
 */
import axios from 'axios'
import type { ChatResponse, UploadResponse } from '../types'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const apiClient = {
  /**
   * Check API health
   */
  async healthCheck() {
    const response = await api.get('/health')
    return response.data
  },

  /**
   * Upload a file (CSV/XLSX)
   */
  async uploadFile(file: File): Promise<UploadResponse> {
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post<UploadResponse>('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    return response.data
  },

  /**
   * Send a chat message/question
   */
  async chat(sessionId: string, question: string): Promise<ChatResponse> {
    const response = await api.post<ChatResponse>('/chat', {
      session_id: sessionId,
      question,
    })

    return response.data
  },

  /**
   * Get session information
   */
  async getSessionInfo(sessionId: string) {
    const response = await api.get(`/session/${sessionId}`)
    return response.data
  },

  /**
   * Reset a session
   */
  async resetSession(sessionId: string) {
    const response = await api.post('/reset', {
      session_id: sessionId,
    })
    return response.data
  },
}
