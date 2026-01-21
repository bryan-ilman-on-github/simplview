/**
 * FileUpload Component
 *
 * Handles drag-and-drop and file selection for CSV/XLSX files.
 */
import { useState, useCallback } from 'react'
import { Upload, FileSpreadsheet, AlertCircle, Check } from 'lucide-react'
import { apiClient } from '../services/api'
import type { SessionData } from '../types'
import './FileUpload.css'

interface FileUploadProps {
  onFileUploaded: (data: SessionData) => void
}

const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB
const ALLOWED_EXTENSIONS = ['.csv', '.xlsx', '.xls']

export default function FileUpload({ onFileUploaded }: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  const validateFile = (file: File): { valid: boolean; error?: string } => {
    const ext = '.' + file.name.split('.').pop()?.toLowerCase()

    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      return {
        valid: false,
        error: `Invalid file type. Please upload ${ALLOWED_EXTENSIONS.join(', ')}`
      }
    }

    if (file.size > MAX_FILE_SIZE) {
      return {
        valid: false,
        error: `File too large. Maximum size is ${MAX_FILE_SIZE / (1024 * 1024)}MB`
      }
    }

    return { valid: true }
  }

  const handleFile = useCallback(async (file: File) => {
    const validation = validateFile(file)

    if (!validation.valid) {
      setError(validation.error || 'Invalid file')
      return
    }

    setError(null)
    setSelectedFile(file)
    setIsUploading(true)

    try {
      const response = await apiClient.uploadFile(file)

      if (response.success && response.file_info) {
        onFileUploaded({
          sessionId: response.session_id,
          filename: response.file_info.filename,
          rowCount: response.file_info.row_count,
          columns: response.file_info.columns
        })
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to upload file'
      setError(message)
      setSelectedFile(null)
    } finally {
      setIsUploading(false)
    }
  }, [onFileUploaded])

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)

    const file = e.dataTransfer.files[0]
    if (file) {
      handleFile(file)
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      handleFile(file)
    }
  }

  return (
    <div className="file-upload">
      <div
        className={`upload-zone ${isDragging ? 'dragging' : ''} ${error ? 'error' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input
          type="file"
          id="file-input"
          className="file-input"
          accept={ALLOWED_EXTENSIONS.join(',')}
          onChange={handleFileSelect}
          disabled={isUploading}
        />

        {isUploading ? (
          <div className="upload-state uploading">
            <div className="spinner" />
            <p>Uploading and processing your file...</p>
          </div>
        ) : selectedFile ? (
          <div className="upload-state success">
            <Check size={48} className="icon-success" />
            <p>{selectedFile.name}</p>
            <p className="file-size">
              {(selectedFile.size / 1024).toFixed(1)} KB
            </p>
          </div>
        ) : (
          <label htmlFor="file-input" className="upload-label">
            <FileSpreadsheet size={48} className="icon-upload" />
            <p className="upload-text">
              Drag & drop your file here, or click to browse
            </p>
            <p className="upload-hint">
              Supports CSV, XLSX, XLS (max 10MB)
            </p>
            <button type="button" className="upload-btn">
              <Upload size={18} />
              Choose File
            </button>
          </label>
        )}
      </div>

      {error && (
        <div className="upload-error">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}
    </div>
  )
}
