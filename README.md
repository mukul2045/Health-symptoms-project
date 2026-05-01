# Symptom Checker API

A lightweight FastAPI project that maps user-entered symptoms to likely conditions using a transparent rule-based scoring system.

This project is for learning/demo purposes only and is **not** a medical diagnosis tool.

## Features

- FastAPI backend with Swagger docs
- Rule-based condition matching with weighted symptom overlap
- Supports both `POST /check` and `GET /check`
- Includes symptom normalization and common alias handling
- Simple test suite to verify API behavior

## Project Structure

- `main.py` - FastAPI app and endpoints
- `symptom_mapper.py` - condition profiles, parsing, scoring logic
- `test_main.py` - API and mapper tests
- `requirements.txt` - project dependencies

## Requirements

- Python 3.10+ (tested with Python 3.12)

## Setup

```bash
python -m venv .venv
```

Activate the environment:

- Windows PowerShell:

```bash
.venv\Scripts\Activate.ps1
```

- macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Run the API

```bash
uvicorn main:app --reload
```

Open:

- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Health check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

## Example Requests

### POST `/check`

```bash
curl -X POST "http://127.0.0.1:8000/check" \
  -H "Content-Type: application/json" \
  -d "{\"symptoms\": \"fever, cough, fatigue\", \"top_k\": 3}"
```

### GET `/check`

```bash
curl "http://127.0.0.1:8000/check?symptoms=fever,cough,fatigue&top_k=3"
```

### GET `/conditions`

```bash
curl "http://127.0.0.1:8000/conditions"
```

## Run Tests

```bash
python -m pytest -q
```

## Notes

- Match scores are heuristic values from `0` to `1`.
- Better symptom wording gives better suggestions.
- Always consult a qualified clinician for real medical decisions.

