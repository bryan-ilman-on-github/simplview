# Intelligent Data Room

A multi-agent web application that allows users to "talk" to their data using AI. Built with Python, FastAPI, React, and Google Gemini API.

## Overview

This application implements a two-agent workflow:
- **Agent 1 (The Planner)**: Analyzes user questions and data schema to create execution plans
- **Agent 2 (The Executor)**: Uses PandasAI + Gemini API to execute plans and generate insights

## Tech Stack

### Backend
- Python 3.12+
- FastAPI (web framework)
- PandasAI (AI-powered data analysis)
- Google Gemini API (LLM for agent reasoning)
- Pandas (data manipulation)

### Frontend
- React 18 + TypeScript
- Vite (build tool)
- Recharts (data visualization)
- Axios (HTTP client)

## Features

- CSV/XLSX file upload (max 10MB)
- Natural language queries about data
- Automatic chart generation (bar, line, pie, scatter)
- Context retention for follow-up questions (last 5 messages)
- Multi-agent reasoning system

## Setup Instructions

### Prerequisites

- Python 3.12+
- Node.js 18+
- Google Gemini API key

### Getting a Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate a virtual environment:
```bash
# Windows
py -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the backend directory:
```bash
cp .env.example .env
```

5. Edit `.env` and add your Gemini API key:
```
GEMINI_API_KEY=your_actual_api_key_here
```

6. Start the backend server:
```bash
python -m app.main
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. (Optional) Create a `.env` file for custom API URL:
```bash
cp .env.example .env
```

4. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## Usage

1. Open the application in your browser
2. Upload a CSV or Excel file
3. Ask questions about your data in natural language

### Example Queries

- "Show me total sales by category"
- "What are the top 5 states by profit?"
- "Create a pie chart of sales by region"
- "How has profit changed over time?"
- "Which sub-categories are unprofitable?"

## Project Structure

```
simplview/
├── backend/
│   ├── app/
│   │   ├── agents/        # Multi-agent system
│   │   ├── api/           # FastAPI routes
│   │   ├── models/        # Pydantic schemas
│   │   ├── services/      # Context & data management
│   │   ├── config.py      # Configuration
│   │   └── main.py        # Application entry
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── services/      # API client
│   │   └── types/         # TypeScript types
│   ├── package.json
│   └── .env.example
├── Sample_Superstore.csv  # Sample dataset
└── README.md
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/upload` | POST | Upload data file |
| `/api/chat` | POST | Ask a question |
| `/api/session/{id}` | GET | Get session info |
| `/api/reset` | POST | Clear session |

## License

This project was created as a technical challenge for Simplview.
