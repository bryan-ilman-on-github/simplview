/**
 * ChatInterface Component
 *
 * Handles conversation with the multi-agent system.
 * Displays message history and handles user input.
 */
import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Loader2 } from 'lucide-react'
import { apiClient } from '../services/api'
import type { ChatMessage } from '../types'
import './ChatInterface.css'

interface ChatInterfaceProps {
  sessionId: string
  onChartUpdate: (data: any, type: string) => void
}

export default function ChatInterface({ sessionId, onChartUpdate }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Hello! I\'ve loaded your data. Ask me anything about it - I can create charts, analyze trends, find patterns, and answer questions.',
      timestamp: new Date()
    }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!input.trim() || isLoading) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await apiClient.chat(sessionId, input)

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.answer,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, assistantMessage])

      // Update chart data if available
      if (response.chart_data && response.chart_type !== 'none') {
        onChartUpdate(response.chart_data, response.chart_type)
      }
    } catch (err: unknown) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: err instanceof Error ? err.message : 'An error occurred. Please try again.',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h2>Ask about your data</h2>
      </div>

      <div className="messages-container">
        {messages.map(message => (
          <div
            key={message.id}
            className={`message ${message.role === 'user' ? 'user-message' : 'assistant-message'}`}
          >
            <div className="message-avatar">
              {message.role === 'user' ? (
                <User size={18} />
              ) : (
                <Bot size={18} />
              )}
            </div>
            <div className="message-content">
              <p>{message.content}</p>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="message assistant-message loading">
            <div className="message-avatar">
              <Bot size={18} />
            </div>
            <div className="message-content">
              <Loader2 size={18} className="spinner" />
              <span>Analyzing your data...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          className="chat-input"
          placeholder="Ask a question about your data..."
          value={input}
          onChange={e => setInput(e.target.value)}
          disabled={isLoading}
        />
        <button
          type="submit"
          className="send-button"
          disabled={!input.trim() || isLoading}
        >
          {isLoading ? (
            <Loader2 size={20} className="spinner" />
          ) : (
            <Send size={20} />
          )}
        </button>
      </form>

      <div className="suggestions">
        <span className="suggestions-label">Try asking:</span>
        <button
          className="suggestion-chip"
          onClick={() => setInput('Show me total sales by category')}
          disabled={isLoading}
        >
          Sales by category
        </button>
        <button
          className="suggestion-chip"
          onClick={() => setInput('What are the top 5 states by profit?')}
          disabled={isLoading}
        >
          Top 5 states by profit
        </button>
        <button
          className="suggestion-chip"
          onClick={() => setInput('Show me the profit trend over time')}
          disabled={isLoading}
        >
          Profit trend over time
        </button>
      </div>
    </div>
  )
}
