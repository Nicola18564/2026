from __future__ import annotations

from typing import Dict, List

MENTAL_HEALTH_TEMPLATES: Dict[str, Dict[str, str]] = {
    "stress": {
        "response": "Pause for 60 seconds, breathe slowly, and focus on one manageable next step.",
        "resource": "Try grounding, journaling, and brief breaks. Contact a counselor if distress continues.",
    },
    "anxiety": {
        "response": "Name 5 things you can see and take calm breaths to reduce immediate anxiety intensity.",
        "resource": "If anxiety is frequent or intense, connect with a mental health professional.",
    },
    "sad": {
        "response": "Acknowledge your feeling and reach out to a trusted person today.",
        "resource": "Consider counseling support, sleep routine, and light daily movement.",
    },
    "burnout": {
        "response": "Burnout recovery starts with rest boundaries, hydration, and reducing overload.",
        "resource": "Plan micro-breaks and seek professional support when exhaustion persists.",
    },
}

FITNESS_PLANS: Dict[str, List[str]] = {
    "weight loss": [
        "Walk 30 minutes daily (can split into 3 x 10 minutes).",
        "Add 2 days/week strength training (bodyweight or resistance bands).",
        "Use plate method: half vegetables, quarter protein, quarter whole grains.",
    ],
    "cardio": [
        "Start low-impact cardio 20 minutes, 5 days/week.",
        "Increase by 5 minutes weekly as tolerated.",
        "Track resting heart rate trend for progress.",
    ],
    "mobility": [
        "Perform joint mobility drills for hips, spine, and shoulders.",
        "Do gentle balance practice and calf raises.",
        "Take movement breaks every 45-60 minutes.",
    ],
    "general": [
        "Aim for 150 minutes of moderate activity weekly.",
        "Sleep 7-8 hours and hydrate consistently.",
        "Include fruits, vegetables, and protein-rich meals daily.",
    ],
}


def mental_health_support(topic: str) -> Dict[str, str]:
    choice = topic.strip().lower()
    return MENTAL_HEALTH_TEMPLATES.get(
        choice,
        {
            "response": "I am here with you. Share what feels hardest right now and take one small self-care action.",
            "resource": "If emotional pain increases, contact a mental health professional or local helpline.",
        },
    )


def fitness_recommendations(goal: str) -> List[str]:
    return FITNESS_PLANS.get(goal.strip().lower(), FITNESS_PLANS["general"])


def monitor_health(vitals: Dict[str, float]) -> List[str]:
    alerts: List[str] = []

    hr = vitals.get("heart_rate")
    bp = vitals.get("blood_pressure")
    temp = vitals.get("temperature")
    oxygen = vitals.get("oxygen_saturation")

    if hr is not None:
        if hr < 50:
            alerts.append("Heart rate is low. Sit or lie down and reassess if symptoms continue.")
        elif hr > 100:
            alerts.append("Heart rate is elevated. Rest, hydrate, and monitor trend.")

    if bp is not None:
        systolic, diastolic = bp
        if systolic > 140 or diastolic > 90:
            alerts.append("Blood pressure appears high. Recheck after rest and follow up with clinician.")
        elif systolic < 90 or diastolic < 60:
            alerts.append("Blood pressure appears low. Hydrate and avoid sudden standing.")

    if temp is not None:
        if temp >= 38.0:
            alerts.append("Fever pattern detected. Rest, fluids, and monitor worsening signs.")
        elif temp < 35.5:
            alerts.append("Body temperature is low. Warm up and seek care if persistent.")

    if oxygen is not None and oxygen < 95:
        alerts.append("Oxygen saturation below normal range. Seek urgent care for breathlessness.")

    if not alerts:
        alerts.append("Vitals are within expected range for now. Continue regular monitoring.")

    return alerts


def emergency_advice() -> Dict[str, str]:
    return {
        "headline": "Emergency Guidance",
        "instructions": "Call local emergency services immediately and keep the person safe and breathing.",
        "quick_steps": [
            "Stay calm and assess responsiveness.",
            "Keep airway clear and avoid risky movement.",
            "Share symptoms, age, and vitals with responders.",
        ],
        "note": "This assistant is not a substitute for emergency medical professionals.",
    }
