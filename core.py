from typing import Dict, List, Optional, Sequence, Set


DISEASE_DATABASE: Dict[str, Dict[str, object]] = {
    "common cold": {
        "symptoms": {"cough", "sore throat", "runny nose", "sneezing", "mild fever", "congestion"},
        "medications": ["rest", "warm fluids", "paracetamol", "saline spray"],
        "specialty": "general physician",
        "guidance": [
            "Stay hydrated and rest well.",
            "Use steam inhalation or saline rinse for congestion.",
            "Seek care if symptoms worsen or last more than a week.",
        ],
        "risk_flags": ["persistent fever", "shortness of breath"],
    },
    "flu": {
        "symptoms": {"high fever", "body ache", "headache", "fatigue", "cough", "chills", "weakness"},
        "medications": ["acetaminophen", "rest", "fluids", "medical review for antivirals"],
        "specialty": "general physician",
        "guidance": [
            "Rest, isolate if contagious symptoms are present, and drink plenty of fluids.",
            "Track fever and breathing comfort every few hours.",
            "Consult a doctor early if you are elderly, pregnant, or high-risk.",
        ],
        "risk_flags": ["shortness of breath", "chest pain", "dehydration"],
    },
    "covid-19": {
        "symptoms": {"fever", "cough", "fatigue", "sore throat", "loss of taste", "loss of smell", "breathing difficulty"},
        "medications": ["rest", "fluids", "fever reducers", "medical evaluation if high risk"],
        "specialty": "pulmonologist",
        "guidance": [
            "Limit close contact, rest, and monitor oxygen if available.",
            "Use mask precautions when around others.",
            "Escalate quickly if breathing worsens or oxygen drops.",
        ],
        "risk_flags": ["oxygen below 95", "shortness of breath", "confusion"],
    },
    "dehydration": {
        "symptoms": {"dry mouth", "thirst", "dark urine", "dizziness", "weakness"},
        "medications": ["oral rehydration salts", "electrolyte drinks", "rest"],
        "specialty": "general physician",
        "guidance": [
            "Drink oral rehydration solutions in small frequent sips.",
            "Avoid excess heat and strenuous activity.",
            "Seek urgent help if confusion or fainting appears.",
        ],
        "risk_flags": ["fainting", "confusion", "unable to drink"],
    },
    "hypertension": {
        "symptoms": {"headache", "dizziness", "chest discomfort", "fatigue", "high blood pressure"},
        "medications": ["blood pressure monitoring", "reduced salt diet", "medical review for antihypertensives"],
        "specialty": "cardiologist",
        "guidance": [
            "Recheck blood pressure after resting quietly for a few minutes.",
            "Reduce salt intake and avoid smoking.",
            "Book a cardiology review if readings stay elevated.",
        ],
        "risk_flags": ["severe headache", "chest pain", "vision loss"],
    },
    "diabetes": {
        "symptoms": {"excessive thirst", "frequent urination", "fatigue", "blurred vision", "high blood sugar"},
        "medications": ["blood sugar monitoring", "dietary changes", "medical review for metformin or insulin"],
        "specialty": "endocrinologist",
        "guidance": [
            "Check blood glucose regularly if equipment is available.",
            "Limit refined sugar and follow balanced meals.",
            "Seek medical care for persistent high readings or sudden weakness.",
        ],
        "risk_flags": ["confusion", "vomiting", "severe weakness"],
    },
    "migraine": {
        "symptoms": {"headache", "nausea", "light sensitivity", "sound sensitivity", "vomiting"},
        "medications": ["pain relief", "hydration", "rest in a dark room"],
        "specialty": "neurologist",
        "guidance": [
            "Move to a dark, quiet room and limit screen exposure.",
            "Hydrate and note possible triggers like lack of sleep or stress.",
            "Seek care if headache is sudden, severe, or unusual.",
        ],
        "risk_flags": ["sudden severe headache", "weakness", "confusion"],
    },
    "asthma flare": {
        "symptoms": {"wheezing", "cough", "shortness of breath", "chest tightness"},
        "medications": ["quick-relief inhaler", "rest", "medical review"],
        "specialty": "pulmonologist",
        "guidance": [
            "Use prescribed inhaler if available and sit upright.",
            "Avoid smoke, dust, or known triggers.",
            "Seek urgent care if speaking becomes difficult.",
        ],
        "risk_flags": ["blue lips", "severe shortness of breath", "unable to speak"],
    },
    "food poisoning": {
        "symptoms": {"vomiting", "diarrhea", "stomach pain", "nausea", "fever"},
        "medications": ["oral fluids", "oral rehydration salts", "light meals", "medical review if severe"],
        "specialty": "gastroenterologist",
        "guidance": [
            "Focus on hydration and avoid oily or spicy food temporarily.",
            "Rest and monitor signs of dehydration.",
            "Seek care for blood in stool, persistent vomiting, or high fever.",
        ],
        "risk_flags": ["blood in stool", "dehydration", "persistent vomiting"],
    },
}

RISK_FACTORS: Dict[str, float] = {
    "smoking": 1.2,
    "poor diet": 1.0,
    "sedentary": 1.0,
    "family history": 1.3,
    "high bmi": 1.2,
    "diabetes": 1.2,
    "hypertension": 1.1,
    "pregnancy": 0.8,
    "asthma": 1.0,
    "elderly": 1.2,
}

EMERGENCY_TERMS: Set[str] = {
    "chest pain", "shortness of breath", "breathing difficulty", "fainting", "confusion",
    "unconscious", "stroke", "seizure", "severe bleeding", "blue lips",
}


def detect_disease(symptoms: Sequence[str]) -> Optional[str]:
    normalized = {symptom.strip().lower() for symptom in symptoms if symptom}
    best_match: Optional[str] = None
    best_score = 0
    for disease, model in DISEASE_DATABASE.items():
        score = len(normalized & set(model["symptoms"]))
        if score > best_score:
            best_score = score
            best_match = disease
    return best_match if best_score > 0 else None


def calculate_confidence(symptoms: Sequence[str], disease: str) -> int:
    model = DISEASE_DATABASE.get(disease.lower())
    if not model:
        return 48
    normalized = {symptom.strip().lower() for symptom in symptoms if symptom}
    disease_symptoms = set(model["symptoms"])
    matched = len(normalized & disease_symptoms)
    base = int((matched / max(1, len(disease_symptoms))) * 100)
    return max(42, min(96, base + 18))


def guide_patient(disease: str) -> List[str]:
    model = DISEASE_DATABASE.get(disease.lower())
    if not model:
        return [
            "Describe your symptoms more specifically for a better match.",
            "Track fever, pain, hydration, and breathing changes.",
            "See a clinician if symptoms become severe or persistent.",
        ]
    return list(model["guidance"])


def suggest_medication(disease: str) -> List[str]:
    model = DISEASE_DATABASE.get(disease.lower())
    if not model:
        return ["Rest", "Hydration", "Professional medical review if symptoms continue"]
    return list(model["medications"])


def recommend_doctor(disease: str, location: str = "your area") -> str:
    model = DISEASE_DATABASE.get(disease.lower())
    specialty = model["specialty"] if model else "general physician"
    return f"Recommended specialist: {specialty}. Look for clinic, hospital, or telehealth support in {location}."


def _symptom_risk_boost(symptoms: Sequence[str]) -> float:
    normalized = {item.strip().lower() for item in symptoms if item}
    boost = 0.0
    if normalized & EMERGENCY_TERMS:
        boost += 2.4
    if "high fever" in normalized or "fever" in normalized:
        boost += 0.5
    if "dizziness" in normalized or "weakness" in normalized:
        boost += 0.4
    return boost


def predict_risk(age: int, bmi: float, conditions: Sequence[str], symptoms: Optional[Sequence[str]] = None) -> Dict[str, object]:
    score = 0.8
    if age >= 65:
        score += 1.5
    elif age >= 45:
        score += 0.9
    elif age <= 12:
        score += 0.7
    if bmi >= 30:
        score += 1.2
    elif bmi >= 25:
        score += 0.7
    normalized_conditions = {item.strip().lower() for item in conditions if item}
    for factor, weight in RISK_FACTORS.items():
        if factor in normalized_conditions:
            score += weight
    if symptoms:
        score += _symptom_risk_boost(symptoms)
    if score < 2.6:
        level = "Low"
        advice = "Maintain healthy habits, rest well, and continue monitoring."
    elif score < 4.8:
        level = "Medium"
        advice = "Follow guidance closely and arrange a medical review if symptoms stay active."
    else:
        level = "High"
        advice = "Seek professional care soon, especially if symptoms are worsening or urgent."
    percent = min(100, int((score / 7.0) * 100))
    return {"level": level, "score": percent, "advice": advice}


def get_red_flags(disease: str, symptoms: Sequence[str]) -> List[str]:
    flags: List[str] = []
    normalized = {item.strip().lower() for item in symptoms if item}
    model = DISEASE_DATABASE.get(disease.lower())
    if model:
        for term in model.get("risk_flags", []):
            if term in normalized:
                flags.append(f"Red flag detected: {term}.")
    for term in EMERGENCY_TERMS:
        if term in normalized and f"Red flag detected: {term}." not in flags:
            flags.append(f"Red flag detected: {term}.")
    return flags
