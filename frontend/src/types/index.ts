/**
 * TypeScript type definitions for the frontend.
 */

export interface SessionData {
  sessionId: string
  filename: string
  rowCount: number
  columns: string[]
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

export interface ChartData {
  labels: string[]
  values: number[]
  additional_series?: Array<{
    name: string
    data: number[]
  }>
}

export interface ChatResponse {
  success: boolean
  answer: string
  plan?: {
    analysis: string
    steps: string[]
    visualization: string
    visualization_config?: {
      x_axis?: string
      y_axis?: string
      title?: string
    }
  }
  chart_data?: ChartData
  chart_type: string
  insights: string[]
  error?: string
}

export interface UploadResponse {
  success: boolean
  message: string
  session_id: string
  file_info?: {
    filename: string
    row_count: number
    columns: string[]
    file_size: number
  }
}
