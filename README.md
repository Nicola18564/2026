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

## Final Entry Point

Use `app.py` as the final project application.

It supports both of these run modes:
- `python app.py` for the built-in server at `http://127.0.0.1:8000`
- `uvicorn app:app --reload` for ASGI serving

## Optional Demo Surface

`app_web.py` is kept as an optional extended Flask demo UI. It is not the primary entrypoint for the final project.

## Main Files

- `app.py`: primary backend and UI host
- `index.html`: primary frontend template used by `app.py`
- `core.py`, `support.py`, `scenarios.py`, `utils.py`: healthcare logic modules
- `frontend/`: extra static frontend assets retained from the imported project

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
