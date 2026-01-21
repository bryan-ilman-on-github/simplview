import { useState } from 'react'
import FileUpload from './components/FileUpload'
import ChatInterface from './components/ChatInterface'
import ChartDisplay from './components/ChartDisplay'
import { FileText, MessageSquare, BarChart3 } from 'lucide-react'
import './App.css'

interface SessionData {
  sessionId: string
  filename: string
  rowCount: number
  columns: string[]
}

function App() {
  const [session, setSession] = useState<SessionData | null>(null)
  const [chartData, setChartData] = useState<any>(null)
  const [chartType, setChartType] = useState<string>('none')

  const handleFileUploaded = (data: SessionData) => {
    setSession(data)
    setChartData(null)
    setChartType('none')
  }

  const handleChartUpdate = (data: any, type: string) => {
    setChartData(data)
    setChartType(type)
  }

  const handleReset = () => {
    setSession(null)
    setChartData(null)
    setChartType('none')
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div className="logo">
            <BarChart3 size={28} />
            <h1>Intelligent Data Room</h1>
          </div>
          {session && (
            <button className="reset-btn" onClick={handleReset}>
              New File
            </button>
          )}
        </div>
      </header>

      <main className="app-main">
        {!session ? (
          <div className="upload-section">
            <div className="upload-card">
              <FileText size={48} className="icon-large" />
              <h2>Upload Your Data</h2>
              <p>Upload a CSV or Excel file to start analyzing your data with AI</p>
              <FileUpload onFileUploaded={handleFileUploaded} />
            </div>
          </div>
        ) : (
          <div className="chat-section">
            <div className="chat-container">
              <ChatInterface
                sessionId={session.sessionId}
                onChartUpdate={handleChartUpdate}
              />
            </div>
            {chartData && chartType !== 'none' && (
              <div className="chart-container">
                <ChartDisplay data={chartData} type={chartType} />
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  )
}

export default App
