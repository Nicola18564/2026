import json
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

from core import (
    calculate_confidence,
    detect_disease,
    get_red_flags,
    guide_patient,
    predict_risk,
    recommend_doctor,
    suggest_medication,
)
from scenarios import (
    accessibility_support,
    elderly_fall_detection,
    public_health_advice,
    rural_healthcare_advice,
    voice_assistant_prompt,
)
from support import emergency_advice, fitness_recommendations, mental_health_support, monitor_health
from utils import parse_list, parse_symptoms


BASE_DIR = Path(__file__).resolve().parent
INDEX_FILE = BASE_DIR / "index.html"

DEFAULT_FORM = {
    "query": "",
    "symptoms": "",
    "age": 30,
    "bmi": 24.0,
    "conditions": [],
    "region": "",
    "resources": [],
    "challenge": "",
    "case_type": "",
    "event": "",
    "goal": "prevention",
    "mood": "stress",
    "heart_rate": "",
    "blood_pressure": "",
    "temperature": "",
    "oxygen_saturation": "",
}

EXAMPLE_CASES = {
    "rural": {
        "query": "I live in a rural village and have fever, cough, and weakness.",
        "symptoms": "fever, cough, weakness",
        "age": 52,
        "bmi": 27,
        "conditions": ["hypertension"],
        "region": "Rural district",
        "resources": ["mobile clinic", "community nurse"],
        "challenge": "mobility",
        "case_type": "outbreak",
        "event": "",
        "goal": "prevention",
        "mood": "stress",
        "heart_rate": 102,
        "blood_pressure": "148/94",
        "temperature": 38.4,
        "oxygen_saturation": 95,
    },
    "elderly": {
        "query": "My grandfather slipped at home and now feels dizzy with chest discomfort.",
        "symptoms": "dizziness, chest pain, weakness",
        "age": 74,
        "bmi": 26,
        "conditions": ["elderly", "hypertension"],
        "region": "Urban home",
        "resources": ["caregiver"],
        "challenge": "mobility",
        "case_type": "",
        "event": "fall detected",
        "goal": "mobility",
        "mood": "anxiety",
        "heart_rate": 110,
        "blood_pressure": "162/98",
        "temperature": 37.1,
        "oxygen_saturation": 93,
    },
    "wellness": {
        "query": "I feel stressed and want preventive care guidance for staying healthy.",
        "symptoms": "fatigue, stress",
        "age": 29,
        "bmi": 23,
        "conditions": ["sedentary"],
        "region": "Campus",
        "resources": ["telehealth", "fitness center"],
        "challenge": "",
        "case_type": "",
        "event": "",
        "goal": "prevention",
        "mood": "stress",
        "heart_rate": 78,
        "blood_pressure": "118/76",
        "temperature": 36.7,
        "oxygen_saturation": 98,
    },
}


def _normalize_value(value: Any) -> Any:
    if isinstance(value, str):
        normalized = value.strip()
        low = normalized.lower()
        if low in {"true", "false"}:
            return low == "true"
        if normalized.isdigit():
            return int(normalized)
        try:
            return float(normalized)
        except ValueError:
            return normalized
    return value


def _load_json_body(environ: Dict[str, Any]) -> Dict[str, Any]:
    try:
        length = int(environ.get("CONTENT_LENGTH", "0") or "0")
    except ValueError:
        length = 0
    if length <= 0:
        return {}
    body = environ["wsgi.input"].read(length)
    if not body:
        return {}
    try:
        return json.loads(body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}


def _load_query_data(environ: Dict[str, Any]) -> Dict[str, Any]:
    query = parse_qs(environ.get("QUERY_STRING", ""), keep_blank_values=True)
    parsed: Dict[str, Any] = {}
    for key, values in query.items():
        parsed[key] = _normalize_value(values[0]) if len(values) == 1 else [_normalize_value(v) for v in values]
    return parsed


def _safe_number(value: Any, fallback: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def _safe_int(value: Any, fallback: int) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return fallback


def _parse_vitals(payload: Dict[str, Any]) -> Dict[str, Any]:
    vitals: Dict[str, Any] = {
        "heart_rate": _safe_int(payload.get("heart_rate"), 0) or None,
        "temperature": _safe_number(payload.get("temperature"), 0.0) or None,
        "oxygen_saturation": _safe_int(payload.get("oxygen_saturation"), 0) or None,
    }
    blood_pressure = payload.get("blood_pressure")
    if isinstance(blood_pressure, str) and "/" in blood_pressure:
        try:
            systolic, diastolic = blood_pressure.split("/", 1)
            vitals["blood_pressure"] = (int(systolic.strip()), int(diastolic.strip()))
        except ValueError:
            vitals["blood_pressure"] = None
    else:
        vitals["blood_pressure"] = None
    return vitals


def _build_triage(confidence: int, risk: Dict[str, Any], red_flags: List[str], monitoring: List[str]) -> Dict[str, str]:
    if red_flags or risk["level"] == "High":
        return {
            "status": "Urgent attention",
            "message": "Possible high-risk pattern detected. Escalate to a doctor or emergency care quickly.",
        }
    if confidence >= 70 or monitoring != ["All monitored values are within a typical range. Continue healthy habits."]:
        return {
            "status": "Medical review suggested",
            "message": "This looks actionable. Follow the guidance and schedule a consultation if symptoms continue.",
        }
    return {
        "status": "Monitor at home",
        "message": "Current inputs suggest a lower-risk pattern, but keep tracking symptoms.",
    }


def build_response(payload: Dict[str, Any]) -> Dict[str, Any]:
    merged = {**DEFAULT_FORM, **payload}
    symptoms_value = merged.get("symptoms") or merged.get("query") or ""
    symptoms = parse_symptoms(symptoms_value) if isinstance(symptoms_value, str) else [str(x).strip().lower() for x in symptoms_value]
    disease = str(merged.get("disease", "")).strip().lower() or detect_disease(symptoms) or "general checkup"
    age = _safe_int(merged.get("age"), 30)
    bmi = _safe_number(merged.get("bmi"), 24.0)
    conditions = parse_list(merged.get("conditions", []))
    region = str(merged.get("region", "")).strip() or "your area"
    resources = parse_list(merged.get("resources", []))
    challenge = str(merged.get("challenge", ""))
    case_type = str(merged.get("case_type", ""))
    event = str(merged.get("event", ""))
    goal = str(merged.get("goal", "prevention"))
    mood = str(merged.get("mood", "stress"))
    query = str(merged.get("query", "")).strip()

    confidence = calculate_confidence(symptoms, disease)
    risk = predict_risk(age, bmi, conditions, symptoms)
    monitoring = monitor_health(_parse_vitals(merged))
    red_flags = get_red_flags(disease, symptoms)
    triage = _build_triage(confidence, risk, red_flags, monitoring)

    return {
        "patient_profile": {"age": age, "bmi": bmi, "conditions": conditions, "region": region},
        "analysis": {
            "query": query,
            "symptoms": symptoms,
            "disease": disease,
            "confidence": confidence,
            "summary": f"Possible condition detected: {disease}. {triage['message']}",
            "triage": triage,
            "red_flags": red_flags,
        },
        "care_plan": {
            "step_by_step_guidance": guide_patient(disease),
            "medication_suggestions": suggest_medication(disease),
            "doctor_recommendation": recommend_doctor(disease, region),
            "risk_prediction": risk,
            "monitoring_alerts": monitoring,
        },
        "health_support": {
            "mental_health": mental_health_support(mood),
            "fitness_and_prevention": fitness_recommendations(goal),
        },
        "scenarios": {
            "rural_healthcare": rural_healthcare_advice(region, resources),
            "accessibility": accessibility_support(challenge),
            "public_health": public_health_advice(case_type),
            "elderly_fall_detection": elderly_fall_detection(event),
            "voice_assistant": voice_assistant_prompt(query or symptoms_value),
        },
        "emergency": emergency_advice(),
    }


def render_html_homepage() -> str:
    html = INDEX_FILE.read_text(encoding="utf-8")
    return html.replace("__EXAMPLES__", json.dumps(EXAMPLE_CASES))


def _json_response(start_response, payload: Dict[str, Any], status: str = "200 OK"):
    body = json.dumps(payload, indent=2).encode("utf-8")
    start_response(status, [("Content-Type", "application/json; charset=utf-8"), ("Access-Control-Allow-Origin", "*")])
    return [body]


def wsgi_app(environ, start_response):
    try:
        method = environ.get("REQUEST_METHOD", "GET").upper()
        path = environ.get("PATH_INFO", "/") or "/"
        if method == "OPTIONS":
            start_response("204 No Content", [("Access-Control-Allow-Origin", "*"), ("Access-Control-Allow-Methods", "GET, POST, OPTIONS"), ("Access-Control-Allow-Headers", "Content-Type")])
            return [b""]
        if path in {"/", ""}:
            html = render_html_homepage().encode("utf-8")
            start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
            return [html]
        if path == "/api/ai":
            payload = _load_json_body(environ) if method == "POST" else _load_query_data(environ)
            return _json_response(start_response, build_response(payload))
        if path == "/api/examples":
            return _json_response(start_response, EXAMPLE_CASES)
        if path == "/api/health":
            return _json_response(start_response, {"status": "ok", "service": "MediAssist OpenEnv"})
        start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
        return [b"Not found"]
    except Exception as exc:
        body = json.dumps({"error": str(exc), "type": type(exc).__name__}, indent=2).encode("utf-8")
        start_response("500 Internal Server Error", [("Content-Type", "application/json; charset=utf-8"), ("Access-Control-Allow-Origin", "*")])
        return [body]


def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    print(f"Starting MediAssist OpenEnv at http://{host}:{port}")
    with make_server(host, port, wsgi_app) as server:
        server.serve_forever()


# Export `app` for ASGI servers like uvicorn when FastAPI is available.
try:
    import importlib

    fastapi_module = importlib.import_module("fastapi")
    wsgi_middleware_module = importlib.import_module("fastapi.middleware.wsgi")
    asgi_app = fastapi_module.FastAPI()
    asgi_app.mount("/", wsgi_middleware_module.WSGIMiddleware(wsgi_app))
    app = asgi_app
except Exception:
    app = wsgi_app


if __name__ == "__main__":
    run()
