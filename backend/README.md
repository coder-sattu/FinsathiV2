# Health Insurance Claim Intimation Chatbot (POC)

Proof of concept chatbot for intimate health insurance claims built with FastAPI, PostgreSQL, Google Gemini, and React + MUI.

## Setup and Running

```bash
cd backend
python -m venv .venv
# On Windows: .venv\Scripts\activate
# On Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8080
```

## Running Tests

```bash
pytest -q
```
