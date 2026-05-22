# Voice Assignment

A voice-agent demo with a Python FastAPI backend and a Vite React frontend.

## Project Structure

- `Backend/`: Python backend service
- `Frontend/`: React + Vite frontend app
- `automated_tests.py`: End-to-end test harness for the backend API
- `voice_agent.db`: Local SQLite database file

## Backend

### Requirements

- Python 3.11+ (or compatible)
- `pip` available
- Virtual environment recommended

### Setup

```bash
cd "C:\Users\kaval\Desktop\Voice Assignment"
.\.venv\Scripts\Activate.ps1
pip install -r Backend/requirements.txt
```

### Run backend

```bash
python -m uvicorn Backend.App.main:app --host 127.0.0.1 --port 8000
```

### Health check

```bash
python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=5).read().decode())"
```

## Frontend

### Setup

```bash
cd Frontend
npm install
```

### Run frontend

```bash
npm run dev
```

Then open the app at `http://localhost:5173`.

## Test the API

Run the automated backend tests:

```bash
python .\automated_tests.py
```

This script sends example booking/cancel/reschedule requests and validates the backend response traces.

## Example `Send` inputs

- `I want to book an appointment with doctor 2 at 2036-06-11T09:00`
- `I want to book an appointment with doctor 2 at 2036-06-11T09:00` (conflict)
- `मैं अपॉइंटमेंट बुक करना चाहता हूँ doctor 2 2036-06-13T09:30`
- `நான் நியமனம் செய்ய விரும்புகிறேன் doctor 2 2036-06-14T11:30`
- `hello what is up`
- `cancel appointment 25`
- `reschedule appointment 30 to 2036-06-15T15:00`

## GitHub

Repository pushed to:

`https://github.com/Sasi-nai/voice_agent.git`

## Notes

- `.env` and local database files are ignored by `.gitignore`
- Use the backend health endpoint before running automated tests
