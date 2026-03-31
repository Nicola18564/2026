from __future__ import annotations

from typing import List


def rural_healthcare_advice(region: str, resources: List[str]) -> List[str]:
    base = [
        f"For rural region '{region or 'local area'}', prioritize telemedicine and mobile clinic schedules.",
        "Maintain a home first-aid kit and an updated symptom log.",
        "Coordinate with accredited social health workers/community health centers.",
    ]
    if resources:
        base.append(f"Available resources noted: {', '.join(resources)}.")
    return base


def accessibility_support(challenge: str) -> List[str]:
    text = challenge.strip().lower()
    if "vision" in text or "blind" in text:
        return [
            "Use text-to-speech and high-contrast large-font instructions.",
            "Enable voice prompts and tactile medication organizers.",
        ]
    if "hearing" in text or "deaf" in text:
        return [
            "Use text alerts, captioned guidance, and visual emergency indicators.",
            "Provide written after-care steps and reminder cards.",
        ]
    if "mobility" in text or "wheelchair" in text:
        return [
            "Plan nearest wheelchair-accessible clinics and transport support.",
            "Use home-monitoring and teleconsult options where possible.",
        ]
    return [
        "Use plain-language instructions and caregiver-inclusive guidance.",
        "Offer multi-format communication: text, voice, and visuals.",
    ]


def public_health_advice(case_type: str) -> List[str]:
    text = case_type.strip().lower()
    if "epidemic" in text or "outbreak" in text or "pandemic" in text:
        return [
            "Activate symptom surveillance and early reporting.",
            "Promote masking, hand hygiene, and distancing based on local advisory.",
            "Use vaccination drives and trusted local health communication channels.",
        ]
    return [
        "Track community health bulletins regularly.",
        "Promote prevention awareness and routine immunization.",
    ]


def elderly_fall_detection(event: str) -> str:
    text = event.strip().lower()
    if "fall" in text or "slip" in text or "collapsed" in text:
        return "Possible fall event detected: check consciousness, injury risk, and contact emergency help if needed."
    return "No fall event detected from provided description. Continue routine mobility monitoring."


def voice_assistant_prompt(text_input: str) -> str:
    cleaned = text_input.strip() or "(no input)"
    return (
        f"Voice/Text assistant input: '{cleaned}'. "
        "I can guide symptoms, medicines, doctors, risk, and emergency next steps."
    )
