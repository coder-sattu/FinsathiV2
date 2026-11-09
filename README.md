# FinsathiV2 - Health Insurance Claim Intimation Chatbot

AI-powered health insurance claim intimation chatbot with full-stack architecture. Built with FastAPI, React, and Google Gemini to streamline the insurance claims process through conversational AI.

## 🚀 Features

- **Conversational AI Interface** - Natural language processing powered by Google Gemini
- **Automated Claim Processing** - Intelligent validation and processing of insurance claims
- **Document Upload & Management** - Secure document handling and storage
- **Patient Data Management** - Comprehensive patient information handling
- **Real-time Chat Interface** - Modern, responsive UI built with Material-UI
- **PostgreSQL Integration** - Robust database for data persistence

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Relational database
- **Google Gemini API** - AI/ML for natural language processing
- **Pytest** - Testing framework
- **Uvicorn** - ASGI server

### Frontend
- **React** - JavaScript library for building UIs
- **TypeScript** - Type-safe JavaScript
- **Vite** - Next-generation frontend tooling
- **Material-UI (MUI)** - React component library
- **Responsive Design** - Mobile-friendly interface

## 📋 Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- PostgreSQL database
- Google Gemini API key
- Git

## 🏃 Quick Start

### Backend Setup

```bash
cd backend
python -m venv .venv
# On Windows: .venv\Scripts\activate
# On Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8080
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev -- --port 5173
```

### Running Tests

```bash
cd backend
pytest -q
```

## 📁 Project Structure

```
FinsathiV2/
├── backend/              # FastAPI application
│   ├── app/             # Application modules
│   ├── data/            # Database files
│   ├── tests/           # Test suite
│   └── requirements.txt # Python dependencies
├── frontend/            # React application
│   ├── src/            # Source code
│   ├── public/         # Static assets
│   └── package.json    # Node dependencies
├── sample_docs/         # Sample document templates
├── sample_patient_details.txt  # Test data reference
└── commands.txt         # Local setup commands
```

## 🔧 Configuration

1. **Backend Configuration**
   - Copy `backend/.env.example` to `backend/.env`
   - Add your Google Gemini API key
   - Configure PostgreSQL connection string

2. **Frontend Configuration**
   - Update API endpoint in frontend configuration
   - Set environment variables as needed

## 📝 Test Credentials

Refer to `sample_patient_details.txt` in the project root for sample test data and credentials.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is a proof-of-concept demonstration.

## 👥 Authors

- **Your Name** - Initial work

## 🙏 Acknowledgments

- Google Gemini API for AI capabilities
- FastAPI and React communities
- Material-UI for UI components
