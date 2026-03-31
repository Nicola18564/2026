# MediAssist OpenEnv

AI Healthcare Decision & Monitoring System with unified features:
- Disease detection from symptoms
- Step-by-step guidance
- Medication suggestions
- Doctor recommendation
- Risk prediction
- Mental health support
- Fitness and preventive care
- Health monitoring with vitals
- Rural healthcare, accessibility, and public health scenarios
- Elderly fall detection
- Voice assistant simulation

## Repo Entry Points

- `app.py`: primary project app. It supports both:
  - `python app.py` for the built-in WSGI server
  - `uvicorn app:app --reload` for ASGI/FastAPI-style serving
- `app_web.py`: extended Flask-based demo interface on port `5000`
- `index.html`: standalone UI template used by `app.py`
- `frontend/`: additional static frontend assets copied with the project

## Run

```bash
pip install -r requirements.txt
python app.py
```

Open: `http://127.0.0.1:8000`

Optional ASGI run:

```bash
uvicorn app:app --reload
```

Optional Flask demo:

```bash
python app_web.py
```

Open: `http://127.0.0.1:5000`

## API Endpoints

- `GET /api/health`: service status
- `POST /api/ai`: full healthcare assessment response
- `GET /api/examples`: example scenario payloads

## Important Note

This project is for educational and demo use only. It is not a replacement for licensed medical care.
