"""Optional Flask demo UI for MediAssist.

This file is kept as a secondary demo surface; `app.py` is the final entrypoint.
"""

from PIL import Image, ImageStat, UnidentifiedImageError
from flask import Flask, jsonify, request, render_template_string

from app import build_response
from core import DISEASE_DATABASE
from utils import parse_symptoms

app = Flask(__name__)

FEATURE_ITEMS = [
    ("disease", "Disease Detection"),
    ("risk", "Risk Prediction"),
    ("medicine", "Medicine Suggestion"),
    ("doctor", "Doctor Recommendation"),
    ("emergency", "Emergency Alert"),
    ("mental", "Mental Health Support"),
    ("fitness", "Fitness Advice"),
    ("rural", "Rural Healthcare"),
    ("epidemic", "Epidemic Awareness"),
    ("fall", "Elderly Fall Detection"),
    ("unknown", "Unknown Condition Assist"),
    ("skin", "Skin Disease Detection"),
    ("device_vitals", "Accessory Vitals Capture"),
]

FEATURE_PROMPTS = {
    "disease": "I have fever, cough, body ache, and weakness.",
    "risk": "I have dizziness, chest discomfort, and hypertension history.",
    "medicine": "I have cold and sore throat with mild fever.",
    "doctor": "I have repeated high blood pressure and headache.",
    "emergency": "Severe chest pain and breathlessness started suddenly.",
    "mental": "I feel anxious, stressed, and unable to sleep.",
    "fitness": "I want preventive care and sustainable fitness guidance.",
    "rural": "In my village I have fever and weak access to clinics.",
    "epidemic": "Many nearby people have fever and cough. I now have similar symptoms.",
    "fall": "My elderly father slipped and now has dizziness and chest pain.",
    "unknown": "I do not know my condition. I have fever, cough, body ache, and weakness.",
    "skin": "I have a skin rash with redness and itching.",
    "device_vitals": "Capture pulse, temperature, and condition score from mobile-assisted accessories.",
}

PRESETS = {
    "rural": {
        "query": "I live in a rural village and have fever, cough, weakness, and dizziness.",
        "conditions": "hypertension",
        "age": "52",
        "bmi": "27",
        "region": "Rural district",
        "resources": "mobile clinic, community nurse",
        "challenge": "mobility",
        "case_type": "outbreak",
        "event": "",
        "goal": "prevention",
        "mood": "stress",
        "heart_rate": "102",
        "blood_pressure": "148/94",
        "temperature": "38.4",
        "oxygen_saturation": "95",
        "budget": "low",
        "internet": "poor",
        "language": "local",
        "living_alone": "no",
        "unknown_mode": "yes",
    },
    "epidemic": {
        "query": "Many people nearby have fever and cough. I now have high fever, body ache, and fatigue.",
        "conditions": "sedentary",
        "age": "34",
        "bmi": "25",
        "region": "Community cluster",
        "resources": "telehealth, local clinic",
        "challenge": "",
        "case_type": "epidemic",
        "event": "",
        "goal": "general",
        "mood": "anxiety",
        "heart_rate": "99",
        "blood_pressure": "126/84",
        "temperature": "38.8",
        "oxygen_saturation": "96",
        "budget": "medium",
        "internet": "good",
        "language": "english",
        "living_alone": "yes",
        "unknown_mode": "yes",
    },
    "elderly_fall": {
        "query": "My grandfather had a fall and now has dizziness, chest pain, and breathlessness.",
        "conditions": "elderly, hypertension",
        "age": "74",
        "bmi": "26",
        "region": "Urban home",
        "resources": "caregiver",
        "challenge": "mobility",
        "case_type": "",
        "event": "fall detected",
        "goal": "mobility",
        "mood": "anxiety",
        "heart_rate": "112",
        "blood_pressure": "162/98",
        "temperature": "37.2",
        "oxygen_saturation": "93",
        "budget": "medium",
        "internet": "good",
        "language": "english",
        "living_alone": "no",
        "unknown_mode": "yes",
    },
}

DEFAULT_FORM = {
    "query": "",
    "conditions": "",
    "age": "30",
    "bmi": "24",
    "region": "",
    "resources": "",
    "challenge": "",
    "case_type": "",
    "event": "",
    "goal": "prevention",
    "mood": "stress",
    "heart_rate": "",
    "blood_pressure": "",
    "temperature": "",
    "oxygen_saturation": "",
    "budget": "medium",
    "internet": "good",
    "language": "english",
    "living_alone": "no",
    "unknown_mode": "yes",
    "camera_pulse": "",
    "device_temp": "",
    "body_condition": "",
}

HTML = """
<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>MediAssist OpenEnv Dashboard</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&family=Sora:wght@500;700&display=swap');

    :root {
      --bg: #eaf5f2;
      --surface: #ffffff;
      --ink: #12323d;
      --muted: #4f6f79;
      --primary: #007a6c;
      --danger: #b91c1c;
      --line: #cde4dc;
      --ok: #0f766e;
    }

    * { box-sizing: border-box; }
    body {
      margin: 0;
      background:
        radial-gradient(900px 450px at -10% 0%, #c6ecdf 0%, transparent 62%),
        radial-gradient(900px 450px at 110% 0%, #ffe5bf 0%, transparent 62%),
        var(--bg);
      color: var(--ink);
      font-family: Outfit, "Segoe UI", sans-serif;
    }
    .page { max-width: 1280px; margin: 0 auto; padding: 22px 16px 40px; }
    .hero, .card { background: var(--surface); border: 1px solid var(--line); border-radius: 18px; box-shadow: 0 16px 36px rgba(18, 50, 61, 0.12); }
    .hero { padding: 22px; margin-bottom: 14px; }
    .kicker { display: inline-block; background: #daf3ec; color: #035a4e; border: 1px solid #bce4d9; border-radius: 999px; padding: 6px 10px; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; font-size: 12px; }
    h1 { margin: 8px 0 4px; font-family: Sora, Outfit, sans-serif; font-size: clamp(1.9rem, 3.5vw, 2.9rem); }
    .hero p { margin: 0; color: var(--muted); }

    .feature-form { margin-bottom: 14px; }
    .features { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 10px; }
    .feature-btn {
      text-align: center; border: 1px solid var(--line); border-radius: 10px; padding: 9px;
      background: #fbfffd; font-size: 13px; font-weight: 700; cursor: pointer;
    }
    .feature-btn.active { background: #e6f8f3; border-color: #94d6c8; color: #015247; }

    .layout { display: grid; grid-template-columns: 1.1fr 1fr; gap: 14px; }
    .card { padding: 16px; }
    h2 { margin: 0 0 6px; font-size: 1.2rem; font-family: Sora, Outfit, sans-serif; }
    .sub { margin: 0 0 12px; color: var(--muted); font-size: 14px; }

    .preset-row { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 10px; }
    .btn { border-radius: 10px; border: 0; padding: 9px 12px; font-weight: 700; cursor: pointer; font-family: Sora, Outfit, sans-serif; }
    .btn.primary { background: linear-gradient(135deg, var(--primary), #0ea594); color: #fff; }
    .btn.secondary { background: #fff; border: 1px solid var(--line); color: #204b56; }

    .grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
    .field { display: grid; gap: 6px; }
    .field.full { grid-column: 1 / -1; }
    label { font-size: 12px; text-transform: uppercase; letter-spacing: .05em; color: #476772; font-weight: 700; }

    input, textarea, select {
      width: 100%; padding: 10px; border: 1px solid var(--line); border-radius: 10px; font: inherit; background: #fbfffd;
    }
    textarea { min-height: 88px; resize: vertical; }

    .kpis { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; margin-bottom: 10px; }
    .kpi { border: 1px solid var(--line); border-radius: 10px; padding: 10px; background: #fbfffd; }
    .kpi .label { font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: .06em; font-weight: 700; }
    .kpi .value { margin-top: 6px; font-size: 1.08rem; font-weight: 800; }

    .result-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; margin-top: 8px; }
    .tile { border: 1px solid var(--line); border-radius: 10px; padding: 10px; background: #fbfffd; font-size: 14px; line-height: 1.45; }
    .tile strong { display: block; margin-bottom: 6px; }

    .alert { margin-top: 10px; border: 1px solid #f5c2c2; background: #fff2f2; color: #8a1717; border-radius: 10px; padding: 10px; font-weight: 700; }
    .safe { margin-top: 10px; border: 1px solid #b8e4dc; background: #effaf8; color: var(--ok); border-radius: 10px; padding: 10px; font-weight: 700; }

    .report-overlay { position: fixed; inset: 0; background: rgba(18, 50, 61, 0.56); display: none; align-items: center; justify-content: center; padding: 18px; z-index: 2000; }
    .report-overlay.open { display: flex; }
    .report-card { width: min(980px, 100%); max-height: 90vh; overflow-y: auto; background: #ffffff; border-radius: 22px; border: 1px solid var(--line); box-shadow: 0 24px 60px rgba(18, 50, 61, 0.25); padding: 22px; }
    .report-top { display: flex; justify-content: space-between; gap: 12px; align-items: start; margin-bottom: 16px; }
    .report-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
    .report-section { border: 1px solid var(--line); border-radius: 12px; padding: 12px; background: #fbfffd; }
    .report-section.full { grid-column: 1 / -1; }
    .report-section h3 { margin: 0 0 8px; font-size: 1rem; font-family: Sora, Outfit, sans-serif; }
    .report-line { margin: 6px 0; color: var(--muted); }
    .report-note { margin-top: 12px; font-size: 12px; color: var(--muted); }

    ul { margin: 6px 0 0 18px; padding: 0; }

    @media (max-width: 680px) {
      .report-grid { grid-template-columns: 1fr; }
    }

    @media (max-width: 1020px) {
      .layout { grid-template-columns: 1fr; }
      .features { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
    @media (max-width: 680px) {
      .grid, .kpis, .result-grid, .features { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <main class=\"page\">
    <section class=\"hero\">
      <span class=\"kicker\">Hackathon Demo Dashboard</span>
      <h1>MediAssist OpenEnv</h1>
      <p>Interactive healthcare AI demo with triage, emergency detection, and real-world deployment solvers.</p>
    </section>

    <form method=\"POST\" class=\"feature-form\">
      <section class=\"features\">
        {% for fid, label in feature_items %}
          <button class=\"feature-btn {% if active_feature == fid %}active{% endif %}\" type=\"submit\" name=\"action\" value=\"feature:{{ fid }}\">{{ label }}</button>
        {% endfor %}
      </section>
    </form>

    <section class=\"layout\">
      <article class=\"card\">
        <h2>Demo Input Box</h2>
        <p class=\"sub\">Use presets, click top features, or enter a custom patient case.</p>

        <form id=\"mainForm\" method=\"POST\" enctype=\"multipart/form-data\">
          <div class=\"preset-row\">
            <button class=\"btn secondary\" type=\"submit\" name=\"action\" value=\"preset:rural\">Load Rural Demo</button>
            <button class=\"btn secondary\" type=\"submit\" name=\"action\" value=\"preset:epidemic\">Load Epidemic Demo</button>
            <button class=\"btn secondary\" type=\"submit\" name=\"action\" value=\"preset:elderly_fall\">Load Elderly Fall</button>
            <button class=\"btn secondary\" type=\"button\" id=\"cameraPulseBtn\">Capture Camera Pulse (Beta)</button>
            <button class=\"btn secondary\" type=\"button\" id=\"startVoiceBtn\">Start Lady Voice Assistant</button>
            <button class=\"btn secondary\" type=\"button\" id=\"stopVoiceBtn\">Stop Voice</button>
            <button class=\"btn secondary\" type=\"button\" id=\"testLadyVoiceBtn\">Test Lady Voice</button>
          </div>

          <div class=\"grid\">
            <div class=\"field full\"><label>Symptoms / Query</label><textarea name=\"query\">{{ form.query }}</textarea></div>
            <div class=\"field\"><label>Patient Knows Condition?</label><select name=\"unknown_mode\"><option value=\"yes\" {% if form.unknown_mode=='yes' %}selected{% endif %}>No (unknown)</option><option value=\"no\" {% if form.unknown_mode=='no' %}selected{% endif %}>Yes</option></select></div>
            <div class=\"field\"><label>Conditions</label><input name=\"conditions\" value=\"{{ form.conditions }}\" /></div>
            <div class=\"field\"><label>Region</label><input name=\"region\" value=\"{{ form.region }}\" /></div>
            <div class=\"field\"><label>Resources</label><input name=\"resources\" value=\"{{ form.resources }}\" /></div>
            <div class=\"field\"><label>Case Type</label><input name=\"case_type\" value=\"{{ form.case_type }}\" /></div>
            <div class=\"field\"><label>Accessibility</label><input name=\"challenge\" value=\"{{ form.challenge }}\" /></div>
            <div class=\"field\"><label>Elderly Event</label><input name=\"event\" value=\"{{ form.event }}\" /></div>
            <div class=\"field\"><label>Mood</label><input name=\"mood\" value=\"{{ form.mood }}\" /></div>
            <div class=\"field\"><label>Goal</label><input name=\"goal\" value=\"{{ form.goal }}\" /></div>
            <div class=\"field\"><label>Age</label><input type=\"number\" name=\"age\" value=\"{{ form.age }}\" /></div>
            <div class=\"field\"><label>BMI</label><input type=\"number\" step=\"0.1\" name=\"bmi\" value=\"{{ form.bmi }}\" /></div>
            <div class=\"field\"><label>Heart Rate</label><input type=\"number\" name=\"heart_rate\" value=\"{{ form.heart_rate }}\" /></div>
            <div class=\"field\"><label>Blood Pressure</label><input name=\"blood_pressure\" value=\"{{ form.blood_pressure }}\" placeholder=\"120/80\" /></div>
            <div class=\"field\"><label>Temperature (C)</label><input type=\"number\" step=\"0.1\" name=\"temperature\" value=\"{{ form.temperature }}\" /></div>
            <div class=\"field\"><label>Oxygen (%)</label><input type=\"number\" name=\"oxygen_saturation\" value=\"{{ form.oxygen_saturation }}\" /></div>
            <div class=\"field\"><label>Budget Level</label><select name=\"budget\"><option {% if form.budget=='low' %}selected{% endif %}>low</option><option {% if form.budget=='medium' %}selected{% endif %}>medium</option><option {% if form.budget=='high' %}selected{% endif %}>high</option></select></div>
            <div class=\"field\"><label>Internet Access</label><select name=\"internet\"><option {% if form.internet=='poor' %}selected{% endif %}>poor</option><option {% if form.internet=='intermittent' %}selected{% endif %}>intermittent</option><option {% if form.internet=='good' %}selected{% endif %}>good</option></select></div>
            <div class=\"field\"><label>Language</label><input name=\"language\" value=\"{{ form.language }}\" /></div>
            <div class=\"field\"><label>Living Alone</label><select name=\"living_alone\"><option {% if form.living_alone=='yes' %}selected{% endif %}>yes</option><option {% if form.living_alone=='no' %}selected{% endif %}>no</option></select></div>
            <div class=\"field\"><label>Pulse From Camera (BPM)</label><input id=\"camera_pulse\" type=\"number\" name=\"camera_pulse\" value=\"{{ form.camera_pulse }}\" /></div>
            <div class=\"field\"><label>Temp From Device (C)</label><input id=\"device_temp\" type=\"number\" step=\"0.1\" name=\"device_temp\" value=\"{{ form.device_temp }}\" /></div>
            <div class=\"field\"><label>Body Condition Score (0-100)</label><input id=\"body_condition\" type=\"number\" min=\"0\" max=\"100\" name=\"body_condition\" value=\"{{ form.body_condition }}\" /></div>
            <div class=\"field full\"><label>Skin Image Upload (JPG/PNG)</label><input type=\"file\" name=\"skin_image\" accept=\"image/*\" /></div>
          </div>

          <div style=\"margin-top:10px;\">
            <button class=\"btn primary\" id=\"analyzeBtn\" type=\"submit\" name=\"action\" value=\"analyze\">Analyze</button>
          </div>
        </form>
      </article>

      <article class=\"card\">
        <h2>Results Dashboard</h2>
        <p class=\"sub\">Interactive output plus real-world solver features for deployment viability.</p>

        {% if result %}
          <div class=\"kpis\">
            <div class=\"kpi\"><div class=\"label\">Disease</div><div class=\"value\">{{ result.analysis.disease }}</div></div>
            <div class=\"kpi\"><div class=\"label\">Risk</div><div class=\"value\">{{ result.care_plan.risk_prediction.level }} ({{ result.care_plan.risk_prediction.score }}%)</div></div>
            <div class=\"kpi\"><div class=\"label\">Action</div><div class=\"value\">{{ result.analysis.triage.status }}</div></div>
          </div>

          <div class=\"result-grid\">
            <div class=\"tile\"><strong>Medication Suggestions</strong><ul>{% for med in result.care_plan.medication_suggestions %}<li>{{ med }}</li>{% endfor %}</ul></div>
            <div class=\"tile\"><strong>Doctor Recommendation</strong>{{ result.care_plan.doctor_recommendation }}</div>
            <div class=\"tile\"><strong>Monitoring Alerts</strong><ul>{% for item in result.care_plan.monitoring_alerts %}<li>{{ item }}</li>{% endfor %}</ul></div>
            <div class=\"tile\"><strong>Red Flags</strong>{% if result.analysis.red_flags %}<ul>{% for rf in result.analysis.red_flags %}<li>{{ rf }}</li>{% endfor %}</ul>{% else %}No critical red flags from current input.{% endif %}</div>
            <div class=\"tile\"><strong>Mental Health Support</strong>{{ result.health_support.mental_health.response }}</div>
            <div class=\"tile\"><strong>Fitness Advice</strong><ul>{% for tip in result.health_support.fitness_and_prevention %}<li>{{ tip }}</li>{% endfor %}</ul></div>
            <div class=\"tile\"><strong>Public Health</strong><ul>{% for p in result.scenarios.public_health %}<li>{{ p }}</li>{% endfor %}</ul></div>
            <div class=\"tile\"><strong>Elderly Fall Detection</strong>{{ result.scenarios.elderly_fall_detection }}</div>

            <div class=\"tile\"><strong>Low-Cost Care Optimizer</strong><ul>{% for p in solvers.cost_plan %}<li>{{ p }}</li>{% endfor %}</ul></div>
            <div class=\"tile\"><strong>Low-Connectivity Mode</strong><ul>{% for p in solvers.connectivity_plan %}<li>{{ p }}</li>{% endfor %}</ul></div>
            <div class=\"tile\"><strong>Medication Adherence Planner</strong><ul>{% for p in solvers.adherence_plan %}<li>{{ p }}</li>{% endfor %}</ul></div>
            <div class=\"tile\"><strong>Home Safety & Follow-up</strong><ul>{% for p in solvers.home_safety_plan %}<li>{{ p }}</li>{% endfor %}</ul></div>
            <div class=\"tile\"><strong>Language/Accessibility Bridge</strong><ul>{% for p in solvers.language_plan %}<li>{{ p }}</li>{% endfor %}</ul></div>
            <div class=\"tile\"><strong>Referral Escalation Router</strong><ul>{% for p in solvers.referral_plan %}<li>{{ p }}</li>{% endfor %}</ul></div>
            {% if device_plan %}
            <div class=\"tile\"><strong>Accessory Vitals Capture</strong>
              <div><strong>Status:</strong> {{ device_plan.status }}</div>
              <ul>{% for p in device_plan.points %}<li>{{ p }}</li>{% endfor %}</ul>
            </div>
            {% endif %}
            {% if unknown_plan %}
            <div class=\"tile\"><strong>Unknown Condition Assist</strong>
              <div><strong>Likely conditions</strong></div>
              <ul>{% for d in unknown_plan.likely_conditions %}<li>{{ d }}</li>{% endfor %}</ul>
              <div><strong>Follow-up questions</strong></div>
              <ul>{% for q in unknown_plan.follow_up_questions %}<li>{{ q }}</li>{% endfor %}</ul>
              <div><strong>Suggested first tests</strong></div>
              <ul>{% for t in unknown_plan.suggested_tests %}<li>{{ t }}</li>{% endfor %}</ul>
            </div>
            {% endif %}
            {% if skin_result %}
            <div class=\"tile\"><strong>Skin Disease Detection (Image)</strong>
              {% if skin_result.error %}
                <div>{{ skin_result.error }}</div>
              {% else %}
                <div><strong>Detected Pattern:</strong> {{ skin_result.prediction }}</div>
                <div><strong>Confidence:</strong> {{ skin_result.confidence }}%</div>
                <div><strong>Severity:</strong> {{ skin_result.severity }}</div>
                <div><strong>Note:</strong> {{ skin_result.note }}</div>
                <div><strong>Care Advice:</strong></div>
                <ul>{% for a in skin_result.advice %}<li>{{ a }}</li>{% endfor %}</ul>
              {% endif %}
            </div>
            {% endif %}
          </div>

          {% if emergency %}
            <div class=\"alert\">Emergency Alert: high-risk/urgent pattern detected. Escalate to emergency care now.</div>
          {% else %}
            <div class=\"safe\">No immediate emergency trigger from current data. Continue monitoring and follow guidance.</div>
          {% endif %}
        {% else %}
          <div class=\"tile\">Load a preset, click a feature above, or enter custom symptoms and click Analyze.</div>
        {% endif %}

        <div class=\"tile\" style=\"margin-top:10px;\">
          <strong>Passive Monitoring (Background)</strong>
          <div id=\"passiveStatus\">Status: Not running</div>
          <div id=\"passiveVitals\">Pulse: -- bpm | Temp: -- C | Fever: -- | Body Condition: --</div>
          <div id=\"passiveAction\">Action: waiting for monitor start</div>
          <div class=\"preset-row\" style=\"margin-top:8px;\">
            <button class=\"btn secondary\" type=\"button\" id=\"startPassiveBtn\">Start Passive Monitor</button>
            <button class=\"btn secondary\" type=\"button\" id=\"stopPassiveBtn\">Stop</button>
          </div>
          <div style=\"font-size:12px;color:#4f6f79;\">Requires camera permission for pulse estimation. Temperature can come from connected device/manual input.</div>
        </div>
        <div class="tile" style="margin-top:10px;">
          <strong>Voice Assistant Intake</strong>
          <div id="voiceStatus">Status: idle</div>
          <div id="voiceQuestion">Question: --</div>
          <div id="voiceAnswer">Last answer: --</div>
          <div id="voiceEngine">Voice: detecting female voice...</div>
          <div id="voiceResult" style="margin-top:8px;font-size:13px;line-height:1.5;color:#12323d;">Result: waiting for voice analysis.</div>
          <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:10px;">
            <input id="voiceTextInput" type="text" placeholder="Type answer or question here if mic does not work" style="flex:1;min-width:220px;padding:10px;border:1px solid #cde4dc;border-radius:10px;" />
            <button class="btn secondary" type="button" id="sendVoiceTextBtn">Send Answer</button>
            <button class="btn secondary" type="button" id="repeatVoiceBtn">Repeat Prompt</button>
          </div>
          <div style="font-size:12px;color:#4f6f79;">Press Start to begin. If microphone does not work, type the answer or question here and press Send Answer.</div>
        </div>
      </article>
    </section>

    <div id="voiceReportOverlay" class="report-overlay" aria-hidden="true">
      <div class="report-card">
        <div class="report-top">
          <div>
            <span class="kicker">Voice Analysis Report</span>
            <h2 id="reportTitle" style="margin-top:10px;">Clinical Result</h2>
            <p id="reportSubtitle" class="sub">Structured result after assistant intake.</p>
          </div>
          <button class="btn secondary" type="button" id="closeVoiceReportBtn">Close Report</button>
        </div>
        <div class="report-grid">
          <div class="report-section">
            <h3>Clinical Impression</h3>
            <div id="reportImpression" class="report-line">Waiting for analysis.</div>
            <div id="reportTriage" class="report-line"></div>
            <div id="reportConfidence" class="report-line"></div>
          </div>
          <div class="report-section">
            <h3>Prescription-Style Care Plan</h3>
            <ul id="reportPrescription"></ul>
          </div>
          <div class="report-section">
            <h3>Doctor Recommendation</h3>
            <div id="reportDoctor" class="report-line"></div>
            <div id="reportRisk" class="report-line"></div>
          </div>
          <div class="report-section">
            <h3>Monitoring</h3>
            <ul id="reportMonitoring"></ul>
          </div>
          <div class="report-section full">
            <h3>Step-by-Step Guidance</h3>
            <ul id="reportGuidance"></ul>
          </div>
          <div class="report-section full">
            <h3>Precautions and Red Flags</h3>
            <ul id="reportRedFlags"></ul>
          </div>
        </div>
        <div class="report-note">Demo medical assistant output for educational presentation use. Final prescriptions and diagnosis should be confirmed by a licensed clinician.</div>
      </div>
    </div>
  </main>
  <script>
    const cameraBtn = document.getElementById("cameraPulseBtn");
    const pulseInput = document.getElementById("camera_pulse");
    const tempInput = document.getElementById("device_temp");
    const bodyScoreInput = document.getElementById("body_condition");
    const startVoiceBtn = document.getElementById("startVoiceBtn");
    const stopVoiceBtn = document.getElementById("stopVoiceBtn");
    const testLadyVoiceBtn = document.getElementById("testLadyVoiceBtn");
    const voiceStatus = document.getElementById("voiceStatus");
    const voiceQuestion = document.getElementById("voiceQuestion");
    const voiceAnswer = document.getElementById("voiceAnswer");
    const voiceEngine = document.getElementById("voiceEngine");
    const voiceResult = document.getElementById("voiceResult");
    const voiceTextInput = document.getElementById("voiceTextInput");
    const sendVoiceTextBtn = document.getElementById("sendVoiceTextBtn");
    const repeatVoiceBtn = document.getElementById("repeatVoiceBtn");
    const analyzeBtn = document.getElementById("analyzeBtn");
    const mainForm = document.getElementById("mainForm");
    const voiceReportOverlay = document.getElementById("voiceReportOverlay");
    const closeVoiceReportBtn = document.getElementById("closeVoiceReportBtn");
    const reportTitle = document.getElementById("reportTitle");
    const reportSubtitle = document.getElementById("reportSubtitle");
    const reportImpression = document.getElementById("reportImpression");
    const reportTriage = document.getElementById("reportTriage");
    const reportConfidence = document.getElementById("reportConfidence");
    const reportPrescription = document.getElementById("reportPrescription");
    const reportDoctor = document.getElementById("reportDoctor");
    const reportRisk = document.getElementById("reportRisk");
    const reportMonitoring = document.getElementById("reportMonitoring");
    const reportGuidance = document.getElementById("reportGuidance");
    const reportRedFlags = document.getElementById("reportRedFlags");
    const startPassiveBtn = document.getElementById("startPassiveBtn");
    const stopPassiveBtn = document.getElementById("stopPassiveBtn");
    const passiveStatus = document.getElementById("passiveStatus");
    const passiveVitals = document.getElementById("passiveVitals");
    const passiveAction = document.getElementById("passiveAction");

    let passiveStream = null;
    let passiveVideo = null;
    let passiveInterval = null;

    let voiceRunning = false;
    let voiceRecognition = null;
    let voiceIndex = 0;
    let voiceMode = "intake"; // intake | assistant
    let answerCaptured = false;
    let recognitionActive = false;
    let pendingAutoStart = false;
    let preferredLadyVoice = null;
    let voiceRetries = 0;
    const maxVoiceRetries = 2;
    const skipWords = ["skip", "not sure", "don't know", "do not know", "unknown", "next question"];

    const voiceFlow = [
      { field: "query", question: "Please describe your main symptoms.", required: true },
      { field: "age", question: "What is your age in years?", required: true },
      { field: "conditions", question: "Do you have any known conditions like diabetes, hypertension, or asthma? Say none if there are no known conditions.", required: true },
      { field: "region", question: "What region or area are you in?", required: false },
      { field: "resources", question: "What healthcare resources do you have, such as telehealth, caregiver, clinic, or ambulance?", required: false },
      { field: "challenge", question: "Do you have any accessibility challenge such as vision, hearing, or mobility? Say none if not.", required: false },
      { field: "case_type", question: "Is this related to an outbreak, epidemic, pandemic, or general case?", required: false },
      { field: "event", question: "Was there any elderly fall, slip, or collapse event? Say none if not.", required: false },
      { field: "heart_rate", question: "If available, what is your pulse or heart rate? You can also say skip.", required: false },
      { field: "blood_pressure", question: "If known, what is your blood pressure? For example one twenty over eighty. You can also say skip.", required: false },
      { field: "temperature", question: "What is your body temperature in Celsius? You can also say skip.", required: false },
      { field: "oxygen_saturation", question: "What is your oxygen saturation percentage? You can also say skip.", required: false },
      { field: "mood", question: "How is your mood? stress, anxiety, sad, burnout, or neutral?", required: false },
      { field: "goal", question: "What is your health goal? prevention, mobility, cardio, weight loss, or general?", required: false }
    ];

    function getField(name) {
      return document.querySelector(`[name="${name}"]`);
    }

    function firstNumber(text) {
      const m = String(text || "").match(/-?\\d+(\\.\\d+)?/);
      return m ? m[0] : "";
    }

    function parseBloodPressure(text) {
      const m = String(text || "").match(/(\\d{2,3})\\D+(\\d{2,3})/);
      return m ? `${m[1]}/${m[2]}` : "";
    }

    function shouldSkipTranscript(transcript) {
      const low = String(transcript || "").toLowerCase();
      return skipWords.some((word) => low.includes(word));
    }

    function applyVoiceAnswer(field, transcript) {
      const target = getField(field);
      if (!target) return false;

      let value = transcript.trim();
      if (!value) return false;

      if (shouldSkipTranscript(value)) {
        if (field === "conditions" || field === "challenge" || field === "event" || field === "case_type") {
          target.value = "";
        }
        return true;
      }

      if (field === "age" || field === "heart_rate" || field === "oxygen_saturation") {
        value = firstNumber(value);
      } else if (field === "temperature") {
        value = firstNumber(value);
      } else if (field === "blood_pressure") {
        value = parseBloodPressure(value) || "";
      } else if (field === "query") {
        const prev = (target.value || "").trim();
        value = prev ? `${prev}. ${value}` : value;
      } else if (field === "mood" || field === "goal" || field === "conditions" || field === "challenge" || field === "case_type") {
        value = value.toLowerCase();
      }

      if (!value && field !== "conditions" && field !== "challenge" && field !== "event" && field !== "case_type") {
        return false;
      }
      target.value = value;
      return true;
    }

    function appendToQuery(text) {
      const target = getField("query");
      if (!target) return;
      const prev = (target.value || "").trim();
      target.value = prev ? `${prev}. ${text}` : text;
    }

    function formPayload() {
      const payload = {};
      if (!mainForm) return payload;
      const formData = new FormData(mainForm);
      for (const [key, value] of formData.entries()) {
        payload[key] = value;
      }
      payload.symptoms = payload.query || "";
      return payload;
    }

    function renderList(target, items, fallback) {
      if (!target) return;
      const values = items && items.length ? items : [fallback];
      target.innerHTML = values.map((item) => `<li>${item}</li>`).join('');
    }

    function buildPrescriptionLines(result) {
      const meds = result.care_plan.medication_suggestions || [];
      const disease = result.analysis.disease;
      const lines = meds.map((med, index) => `Rx ${index + 1}: ${med} - use only with clinician/pharmacist confirmation.`);
      lines.push(`Condition focus: ${disease}. Follow the step-by-step guidance and reassess symptoms if they worsen.`);
      return lines;
    }

    function openVoiceReport(result) {
      if (!voiceReportOverlay) return;
      reportTitle.textContent = `Clinical Result: ${result.analysis.disease}`;
      reportSubtitle.textContent = `Prepared after assistant intake for ${result.patient_profile.region || 'your area'}.`;
      reportImpression.textContent = result.analysis.summary;
      reportTriage.textContent = `Triage: ${result.analysis.triage.status} - ${result.analysis.triage.message}`;
      reportConfidence.textContent = `Confidence: ${result.analysis.confidence}%`;
      reportDoctor.textContent = result.care_plan.doctor_recommendation;
      reportRisk.textContent = `Risk: ${result.care_plan.risk_prediction.level} (${result.care_plan.risk_prediction.score}%) - ${result.care_plan.risk_prediction.advice}`;
      renderList(reportPrescription, buildPrescriptionLines(result), 'No prescription-style plan available.');
      renderList(reportMonitoring, result.care_plan.monitoring_alerts, 'No monitoring alerts available.');
      renderList(reportGuidance, result.care_plan.step_by_step_guidance, 'No guidance available.');
      renderList(reportRedFlags, result.analysis.red_flags, 'No major red flags detected from current input.');
      voiceReportOverlay.classList.add('open');
      voiceReportOverlay.setAttribute('aria-hidden', 'false');
    }

    function closeVoiceReport() {
      if (!voiceReportOverlay) return;
      voiceReportOverlay.classList.remove('open');
      voiceReportOverlay.setAttribute('aria-hidden', 'true');
    }

    function buildVoiceSummary(result) {
      const disease = result.analysis.disease;
      const risk = result.care_plan.risk_prediction.level;
      const score = result.care_plan.risk_prediction.score;
      const doctor = result.care_plan.doctor_recommendation;
      return `Clinical impression: ${disease}. Risk ${risk} at ${score} percent. ${doctor}`;
    }

    function buildAssistantReply(transcript, result) {
      const low = String(transcript || "").toLowerCase();
      if (low.includes("doctor") || low.includes("specialist")) {
        return result.care_plan.doctor_recommendation;
      }
      if (low.includes("medicine") || low.includes("medication") || low.includes("tablet") || low.includes("drug")) {
        return `Suggested medications: ${result.care_plan.medication_suggestions.join(', ')}.`;
      }
      if (low.includes("risk") || low.includes("danger") || low.includes("serious")) {
        return `Risk is ${result.care_plan.risk_prediction.level} at ${result.care_plan.risk_prediction.score} percent. ${result.care_plan.risk_prediction.advice}`;
      }
      if (low.includes("emergency") || low.includes("urgent") || low.includes("hospital")) {
        return result.analysis.triage.message;
      }
      if (low.includes("mental") || low.includes("stress") || low.includes("anxiety") || low.includes("sad")) {
        return result.health_support.mental_health.response;
      }
      if (low.includes("fitness") || low.includes("exercise") || low.includes("prevention")) {
        return `Fitness and prevention advice: ${result.health_support.fitness_and_prevention.join(' ')}`;
      }
      if (low.includes("monitor") || low.includes("oxygen") || low.includes("pressure") || low.includes("pulse")) {
        return `Monitoring update: ${result.care_plan.monitoring_alerts.join(' ')}`;
      }
      if (low.includes("what happened") || low.includes("what is result") || low.includes("disease") || low.includes("condition")) {
        return `${buildVoiceSummary(result)} ${result.analysis.summary}`;
      }
      const firstGuide = result.care_plan.step_by_step_guidance[0] || result.analysis.summary;
      return `${result.analysis.summary} First next step: ${firstGuide}`;
    }

    async function analyzeVoiceCase() {
      if (!mainForm) return null;
      voiceStatus.textContent = "Status: analyzing voice answers...";
      if (voiceResult) voiceResult.textContent = "Result: analyzing current answers...";
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formPayload()),
      });
      const result = await response.json();
      const spoken = buildVoiceSummary(result);
      if (voiceResult) {
        voiceResult.textContent = `${spoken} Guidance: ${result.analysis.summary}`;
      }
      openVoiceReport(result);
      await speakText(`${spoken} ${result.analysis.summary}`);
      return result;
    }

    async function processVoiceTranscript(transcript) {
      if (!voiceRunning) return;
      const cleaned = (transcript || "").trim();
      answerCaptured = cleaned.length > 0;
      voiceAnswer.textContent = `Last answer: ${cleaned || "(empty)"}`;

      if (voiceMode === "intake") {
        const item = voiceFlow[voiceIndex];
        const accepted = item && cleaned ? applyVoiceAnswer(item.field, cleaned) : false;
        if (!accepted && item && item.required) {
          voiceRetries += 1;
          if (voiceRetries <= maxVoiceRetries) {
            voiceAnswer.textContent = "Last answer: not clear, asking again";
            await repeatCurrentQuestion(`Status: waiting for a clear answer to question ${voiceIndex + 1}/${voiceFlow.length}`);
            return;
          }
        }
        if (!accepted && item && !item.required) {
          voiceAnswer.textContent = "Last answer: skipped";
        }
        await movePastCurrentQuestion();
        return;
      }

      const low = cleaned.toLowerCase();
      if (low.includes("stop assistant") || low.includes("stop voice") || low.includes("exit")) {
        stopVoiceIntake(true);
        await speakText("Voice assistant stopped.");
        return;
      }

      if (cleaned) appendToQuery(cleaned);
      try {
        const result = await analyzeVoiceCase();
        const reply = buildAssistantReply(cleaned, result);
        voiceStatus.textContent = "Status: processed input and answered your question";
        if (voiceResult) voiceResult.textContent = `Result: ${reply}`;
        await speakText(reply);
      } catch (error) {
        voiceStatus.textContent = "Status: processed input but analysis failed";
        if (voiceResult) voiceResult.textContent = "Result: analysis failed for the latest input.";
        await speakText("I heard you, but I could not finish the analysis right now.");
      }
      if (voiceRecognition) {
        setTimeout(() => {
          if (voiceRunning) listenNow();
        }, 1200);
      }
    }

    function pickLadyVoice() {
      if (!("speechSynthesis" in window)) return null;
      const voices = window.speechSynthesis.getVoices() || [];
      if (!voices.length) return null;

      const preferred = [
        "google uk english female",
        "microsoft zira",
        "samantha",
        "aria",
        "jenny",
        "female"
      ];

      for (const key of preferred) {
        const found = voices.find((v) => `${v.name} ${v.lang}`.toLowerCase().includes(key));
        if (found) return found;
      }
      return voices[0];
    }

    function initVoiceEngine() {
      if (!("speechSynthesis" in window)) {
        if (voiceEngine) voiceEngine.textContent = "Voice: speech synthesis not supported";
        return;
      }
      preferredLadyVoice = pickLadyVoice();
      if (voiceEngine) {
        if (preferredLadyVoice) {
          voiceEngine.textContent = `Voice: ${preferredLadyVoice.name} (${preferredLadyVoice.lang})`;
        } else {
          voiceEngine.textContent = "Voice: no voice profile loaded yet";
        }
      }
    }

    function speakText(text) {
      return new Promise((resolve) => {
        if (!("speechSynthesis" in window)) {
          resolve();
          return;
        }
        const utter = new SpeechSynthesisUtterance(text);
        if (!preferredLadyVoice) {
          preferredLadyVoice = pickLadyVoice();
        }
        if (preferredLadyVoice) {
          utter.voice = preferredLadyVoice;
          utter.lang = preferredLadyVoice.lang || "en-US";
        } else {
          utter.lang = "en-US";
        }
        utter.rate = 0.96;
        utter.pitch = 1.15;
        utter.onend = () => resolve();
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(utter);
      });
    }

    function listenNow() {
      if (!voiceRunning || !voiceRecognition || recognitionActive) return;
      answerCaptured = false;
      voiceStatus.textContent = voiceMode === "intake" ? `Status: listening for question ${voiceIndex + 1}/${voiceFlow.length}` : "Status: listening for your question";
      try {
        voiceRecognition.start();
        recognitionActive = true;
      } catch (e) {
        setTimeout(() => {
          if (voiceRunning) listenNow();
        }, 700);
      }
    }

    async function askNextVoiceQuestion() {
      if (!voiceRunning || voiceMode !== "intake") return;
      if (voiceIndex >= voiceFlow.length) {
        voiceStatus.textContent = "Status: intake complete. Running analysis and speaking result...";
        await speakText("Thank you. I am analyzing your answers now.");
        try {
          await analyzeVoiceCase();
        } catch (error) {
          voiceStatus.textContent = "Status: analysis failed";
          if (voiceResult) voiceResult.textContent = "Result: unable to analyze the voice answers right now.";
          await speakText("I could not analyze the result right now. Please tap analyze once.");
        }
        await switchToAssistantMode();
        return;
      }

      const item = voiceFlow[voiceIndex];
      voiceQuestion.textContent = `Question: ${item.question}`;
      voiceStatus.textContent = `Status: intake question ${voiceIndex + 1}/${voiceFlow.length}`;
      if (voiceTextInput) voiceTextInput.placeholder = item.question;
      await speakText(item.question);
      if (voiceRecognition) {
        listenNow();
      } else {
        voiceStatus.textContent = `Status: intake question ${voiceIndex + 1}/${voiceFlow.length}. Type the answer below or use a supported voice browser.`;
      }
    }

    async function repeatCurrentQuestion(reasonText) {
      if (!voiceRunning || voiceMode !== "intake") return;
      const item = voiceFlow[voiceIndex];
      if (!item) return;
      voiceStatus.textContent = reasonText || `Status: repeating question ${voiceIndex + 1}/${voiceFlow.length}`;
      voiceQuestion.textContent = `Question: ${item.question}`;
      if (voiceTextInput) voiceTextInput.placeholder = item.question;
      await speakText(`I did not catch that clearly. ${item.question} You can also say skip.`);
      if (voiceRecognition) {
        listenNow();
      }
    }

    async function movePastCurrentQuestion() {
      const item = voiceFlow[voiceIndex];
      voiceIndex += 1;
      voiceRetries = 0;
      if (item) {
        voiceAnswer.textContent = `Last answer: ${item.field} captured`;
      }
      await askNextVoiceQuestion();
    }

    async function switchToAssistantMode() {
      if (!voiceRunning) return;
      voiceMode = "assistant";
      voiceQuestion.textContent = "Question: Ask me anything about your result, medicine, doctor, risk, or new symptoms. Say stop assistant to end.";
      voiceStatus.textContent = "Status: always-on voice assistant active";
      if (voiceTextInput) voiceTextInput.placeholder = "Ask about result, medicine, risk, doctor, or type new symptoms";
      await speakText("Voice assistant is active. You can ask about your result, medicine, doctor, risk, mental health, or tell me new symptoms anytime.");
      if (voiceRecognition) {
        listenNow();
      }
    }

    function stopVoiceIntake(updateStatus = true) {
      voiceRunning = false;
      recognitionActive = false;
      pendingAutoStart = false;
      voiceRetries = 0;
      if (voiceRecognition) {
        try {
          voiceRecognition.stop();
        } catch (e) {}
      }
      if ("speechSynthesis" in window) {
        window.speechSynthesis.cancel();
      }
      if (updateStatus) {
        voiceStatus.textContent = "Status: stopped";
      }
      voiceQuestion.textContent = "Question: --";
    }

    function resetVoiceAssistantUi() {
      voiceIndex = 0;
      voiceRetries = 0;
      voiceAnswer.textContent = "Last answer: --";
      voiceQuestion.textContent = "Question: preparing intake...";
      if (voiceResult) voiceResult.textContent = "Result: waiting for voice analysis.";
      closeVoiceReport();
    }

    async function startVoiceIntake(autoStart = false, startMode = "intake") {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRecognition) {
        voiceRecognition = null;
        voiceRunning = true;
        voiceMode = startMode === "intake" ? "intake" : "assistant";
        voiceIndex = 0;
        voiceRetries = 0;
        voiceStatus.textContent = "Status: voice recognition not supported here. Type your answers below and press Send Answer.";
        if (voiceMode === "intake") {
          await askNextVoiceQuestion();
        } else {
          await switchToAssistantMode();
        }
        return true;
      }

      if (!voiceRecognition) {
        voiceRecognition = new SpeechRecognition();
        voiceRecognition.lang = "en-US";
        voiceRecognition.interimResults = false;
        voiceRecognition.maxAlternatives = 1;
        voiceRecognition.continuous = false;

        voiceRecognition.onresult = async (event) => {
          recognitionActive = false;
          if (!voiceRunning) return;
          const transcript = (event.results[0][0].transcript || "").trim();
          await processVoiceTranscript(transcript);
        };

        voiceRecognition.onerror = async (event) => {
          recognitionActive = false;
          if (!voiceRunning) return;

          if (event.error === "not-allowed" || event.error === "service-not-allowed") {
            pendingAutoStart = false;
            voiceStatus.textContent = "Status: microphone permission blocked. Allow microphone access and press Start Lady Voice Assistant again.";
            if (voiceResult) voiceResult.textContent = "Result: microphone permission is required for voice assistant.";
            return;
          }

          if (voiceMode === "intake") {
            voiceRetries += 1;
            if (voiceRetries <= maxVoiceRetries) {
              voiceAnswer.textContent = "Last answer: not captured, asking again";
              await repeatCurrentQuestion(`Status: retrying question ${voiceIndex + 1}/${voiceFlow.length}`);
            } else {
              voiceAnswer.textContent = "Last answer: skipped after retries";
              await speakText("I will leave this answer blank and continue.");
              await movePastCurrentQuestion();
            }
          } else {
            setTimeout(() => {
              if (voiceRunning) listenNow();
            }, 1200);
          }
        };

        voiceRecognition.onend = async () => {
          recognitionActive = false;
          if (!voiceRunning) return;

          if (voiceMode === "intake" && !answerCaptured) {
            voiceRetries += 1;
            if (voiceRetries <= maxVoiceRetries) {
              voiceAnswer.textContent = "Last answer: silence detected, asking again";
              await repeatCurrentQuestion(`Status: waiting for answer to question ${voiceIndex + 1}/${voiceFlow.length}`);
              return;
            }
            voiceAnswer.textContent = "Last answer: skipped after silence";
            await speakText("No answer detected. I will leave this blank and continue.");
            await movePastCurrentQuestion();
            return;
          }

          if (voiceMode === "assistant") {
            setTimeout(() => {
              if (voiceRunning) listenNow();
            }, 900);
          }
        };
      }

      voiceRunning = true;
      voiceMode = startMode === "intake" ? "intake" : "assistant";
      voiceIndex = 0;
      voiceRetries = 0;
      voiceStatus.textContent = "Status: starting always-on voice assistant...";
      if (voiceMode === "intake") {
        await askNextVoiceQuestion();
      } else {
        await switchToAssistantMode();
      }
      return true;
    }

    async function estimateCameraPulse() {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert("Camera API not available on this device/browser.");
        return;
      }

      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" }, audio: false });
      const video = document.createElement("video");
      video.srcObject = stream;
      video.muted = true;
      video.playsInline = true;
      await video.play();

      const canvas = document.createElement("canvas");
      const ctx = canvas.getContext("2d");
      canvas.width = 160;
      canvas.height = 120;

      const redSeries = [];
      const start = Date.now();

      while (Date.now() - start < 12000) {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const pixels = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
        let redSum = 0;
        for (let i = 0; i < pixels.length; i += 4) redSum += pixels[i];
        redSeries.push(redSum / (pixels.length / 4));
        await new Promise((r) => setTimeout(r, 140));
      }

      stream.getTracks().forEach((t) => t.stop());

      let peaks = 0;
      for (let i = 1; i < redSeries.length - 1; i++) {
        if (redSeries[i] > redSeries[i - 1] && redSeries[i] > redSeries[i + 1]) peaks++;
      }

      const bpm = Math.max(55, Math.min(140, Math.round((peaks / 12) * 60)));
      pulseInput.value = String(bpm);

      if (!tempInput.value) tempInput.value = "36.9";
      if (!bodyScoreInput.value) {
        const score = Math.max(35, Math.min(95, 100 - Math.abs(85 - bpm)));
        bodyScoreInput.value = String(score);
      }
      alert("Camera pulse capture complete (beta). Review values before Analyze.");
    }

    async function estimatePulseFromOpenStream(video) {
      const canvas = document.createElement("canvas");
      const ctx = canvas.getContext("2d");
      canvas.width = 120;
      canvas.height = 90;
      const redSeries = [];
      const start = Date.now();

      while (Date.now() - start < 3500) {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const pixels = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
        let redSum = 0;
        for (let i = 0; i < pixels.length; i += 4) redSum += pixels[i];
        redSeries.push(redSum / (pixels.length / 4));
        await new Promise((r) => setTimeout(r, 120));
      }

      let peaks = 0;
      for (let i = 1; i < redSeries.length - 1; i++) {
        if (redSeries[i] > redSeries[i - 1] && redSeries[i] > redSeries[i + 1]) peaks += 1;
      }

      return Math.max(55, Math.min(145, Math.round((peaks / 3.5) * 60)));
    }

    function estimateBodyCondition(pulse, temp) {
      const pulsePenalty = Math.abs(82 - pulse) * 1.3;
      const tempPenalty = Math.abs(36.9 - temp) * 18;
      return Math.max(20, Math.min(98, Math.round(100 - pulsePenalty - tempPenalty)));
    }

    async function sendPassiveVitals(pulse, temp, condition) {
      const payload = {
        pulse,
        temperature: temp,
        body_condition: condition,
        age: Number(document.querySelector('input[name=\"age\"]').value || 30),
        bmi: Number(document.querySelector('input[name=\"bmi\"]').value || 24),
        conditions: document.querySelector('input[name=\"conditions\"]').value || "",
        query: document.querySelector('textarea[name=\"query\"]').value || "",
      };

      const res = await fetch("/api/passive_monitor", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      return await res.json();
    }

    async function passiveTick() {
      if (!passiveVideo) return;
      const bpm = await estimatePulseFromOpenStream(passiveVideo);
      pulseInput.value = String(bpm);

      const tempValue = Number(tempInput.value || 36.9);
      const driftedTemp = Math.max(35.8, Math.min(39.8, tempValue + (Math.random() - 0.5) * 0.08));
      tempInput.value = driftedTemp.toFixed(1);

      const condition = estimateBodyCondition(bpm, driftedTemp);
      bodyScoreInput.value = String(condition);

      const monitor = await sendPassiveVitals(bpm, driftedTemp, condition);
      passiveVitals.textContent = `Pulse: ${monitor.pulse} bpm | Temp: ${monitor.temperature.toFixed(1)} C | Fever: ${monitor.fever ? 'Yes' : 'No'} | Body Condition: ${monitor.body_condition}/100`;
      passiveAction.textContent = `Action: ${monitor.action}`;
    }

    async function startPassiveMonitor() {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert("Camera API not available on this device/browser.");
        return;
      }
      if (passiveInterval) return;

      passiveStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" }, audio: false });
      passiveVideo = document.createElement("video");
      passiveVideo.srcObject = passiveStream;
      passiveVideo.muted = true;
      passiveVideo.playsInline = true;
      await passiveVideo.play();

      passiveStatus.textContent = "Status: Passive monitoring is running in background";
      await passiveTick();
      passiveInterval = setInterval(() => { passiveTick().catch(() => {}); }, 10000);
    }

    function stopPassiveMonitor() {
      if (passiveInterval) {
        clearInterval(passiveInterval);
        passiveInterval = null;
      }
      if (passiveStream) {
        passiveStream.getTracks().forEach((t) => t.stop());
        passiveStream = null;
      }
      passiveVideo = null;
      passiveStatus.textContent = "Status: Not running";
    }

    if (cameraBtn) {
      cameraBtn.addEventListener("click", async () => {
        cameraBtn.disabled = true;
        cameraBtn.textContent = "Capturing...";
        try {
          await estimateCameraPulse();
        } catch (e) {
          alert("Unable to capture camera pulse on this device. You can enter values manually.");
        } finally {
          cameraBtn.disabled = false;
          cameraBtn.textContent = "Capture Camera Pulse (Beta)";
        }
      });
    }

    if (startPassiveBtn) {
      startPassiveBtn.addEventListener("click", async () => {
        startPassiveBtn.disabled = true;
        startPassiveBtn.textContent = "Starting...";
        try {
          await startPassiveMonitor();
        } catch (e) {
          passiveStatus.textContent = "Status: Unable to start monitor";
          alert("Unable to start passive monitoring. Check camera permission.");
        } finally {
          startPassiveBtn.disabled = false;
          startPassiveBtn.textContent = "Start Passive Monitor";
        }
      });
    }

    if (stopPassiveBtn) {
      stopPassiveBtn.addEventListener("click", () => {
        stopPassiveMonitor();
      });
    }

    async function startVoiceFromButton() {
      stopVoiceIntake(false);
      pendingAutoStart = false;
      resetVoiceAssistantUi();
      initVoiceEngine();
      voiceStatus.textContent = "Status: starting intake. Please allow microphone access if prompted.";
      await startVoiceIntake(false, "intake");
    }

    if (startVoiceBtn) {
      startVoiceBtn.addEventListener("click", async () => {
        startVoiceBtn.disabled = true;
        startVoiceBtn.textContent = "Starting...";
        try {
          await startVoiceFromButton();
        } catch (e) {
          voiceStatus.textContent = "Status: unable to start voice assistant.";
          if (voiceResult) voiceResult.textContent = "Result: could not start the voice assistant. Check microphone permission and browser support.";
        } finally {
          startVoiceBtn.disabled = false;
          startVoiceBtn.textContent = "Start Lady Voice Assistant";
        }
      });
    }

    if (stopVoiceBtn) {
      stopVoiceBtn.addEventListener("click", () => {
        stopVoiceIntake(true);
      });
    }

    if (testLadyVoiceBtn) {
      testLadyVoiceBtn.addEventListener("click", async () => {
        await speakText("Hello, I am your MediAssist lady voice assistant. I am ready to help you.");
      });
    }

    async function sendTypedVoiceInput() {
      if (!voiceRunning) {
        await startVoiceFromButton();
      }
      const transcript = (voiceTextInput?.value || "").trim();
      if (!transcript) {
        voiceStatus.textContent = "Status: type an answer or question first.";
        return;
      }
      if (voiceTextInput) voiceTextInput.value = "";
      await processVoiceTranscript(transcript);
    }

    if (sendVoiceTextBtn) {
      sendVoiceTextBtn.addEventListener("click", async () => {
        await sendTypedVoiceInput();
      });
    }

    if (voiceTextInput) {
      voiceTextInput.addEventListener("keydown", async (event) => {
        if (event.key === "Enter") {
          event.preventDefault();
          await sendTypedVoiceInput();
        }
      });
    }

    if (repeatVoiceBtn) {
      repeatVoiceBtn.addEventListener("click", async () => {
        if (!voiceRunning) {
          await startVoiceFromButton();
          return;
        }
        if (voiceMode === "intake") {
          await repeatCurrentQuestion("Status: repeating current question");
        } else {
          await speakText("You can ask me about your result, doctor, medicine, risk, emergency care, or tell me new symptoms.");
        }
      });
    }

    if (closeVoiceReportBtn) {
      closeVoiceReportBtn.addEventListener("click", () => {
        closeVoiceReport();
      });
    }

    if (voiceReportOverlay) {
      voiceReportOverlay.addEventListener("click", (event) => {
        if (event.target === voiceReportOverlay) {
          closeVoiceReport();
        }
      });
    }

    window.addEventListener("load", () => {
      initVoiceEngine();
      if ("speechSynthesis" in window) {
        window.speechSynthesis.onvoiceschanged = () => {
          initVoiceEngine();
        };
      }
      voiceStatus.textContent = "Status: ready. Press Start Lady Voice Assistant to begin the full intake.";
      voiceQuestion.textContent = "Question: press Start Lady Voice Assistant";
      if (voiceResult) voiceResult.textContent = "Result: after intake, I will analyze the answers, open the report, and speak the result.";
      closeVoiceReport();
    });
  </script>
</body>
</html>
"""


def _to_number(value: str, fallback: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def _build_payload(form: dict) -> dict:
    heart_rate_value = form["heart_rate"] or form["camera_pulse"]
    temperature_value = form["temperature"] or form["device_temp"]
    return {
        "query": form["query"],
        "symptoms": form["query"],
        "conditions": form["conditions"],
        "age": int(_to_number(form["age"], 30)),
        "bmi": _to_number(form["bmi"], 24),
        "region": form["region"],
        "resources": form["resources"],
        "challenge": form["challenge"],
        "case_type": form["case_type"],
        "event": form["event"],
        "goal": form["goal"],
        "mood": form["mood"],
        "heart_rate": heart_rate_value,
        "blood_pressure": form["blood_pressure"],
        "temperature": temperature_value,
        "oxygen_saturation": form["oxygen_saturation"],
    }


def _analyze_skin_image(file_storage) -> dict:
    if not file_storage or not getattr(file_storage, "filename", ""):
        return {}

    try:
        image = Image.open(file_storage.stream).convert("RGB").resize((256, 256))
    except (UnidentifiedImageError, OSError):
        return {"error": "Uploaded file is not a valid image. Please upload JPG or PNG."}

    stat = ImageStat.Stat(image)
    red, green, blue = stat.mean[:3]
    contrast = sum(stat.stddev[:3]) / 3.0
    redness = red - ((green + blue) / 2.0)
    darkness = 255 - ((red + green + blue) / 3.0)

    prediction = "Unclear skin pattern"
    severity = "Mild"
    confidence = 52

    if redness > 35 and contrast > 45:
        prediction = "Possible inflammatory dermatitis or psoriasis-like rash"
        severity = "Moderate"
        confidence = 82
    elif redness > 25 and green > 110:
        prediction = "Possible eczema or contact dermatitis pattern"
        severity = "Mild to Moderate"
        confidence = 76
    elif darkness > 115 and contrast > 38:
        prediction = "Possible fungal infection-like patch pattern"
        severity = "Moderate"
        confidence = 73
    elif redness > 16 and contrast > 28:
        prediction = "Possible acne or folliculitis-like pattern"
        severity = "Mild"
        confidence = 69

    advice = [
        "Keep affected skin clean and dry.",
        "Avoid scratching and harsh cosmetic products.",
        "Use tele-dermatology or in-person dermatologist review for confirmation.",
    ]
    if severity != "Mild":
        advice.append("If rash is spreading, painful, or with fever, seek urgent medical care.")

    return {
        "prediction": prediction,
        "confidence": confidence,
        "severity": severity,
        "advice": advice,
        "note": "Image-based screening is assistive only and not a definitive diagnosis.",
    }


def _rank_likely_conditions(query: str) -> list:
    symptoms = parse_symptoms(query or "")
    ranked = []
    for disease, model in DISEASE_DATABASE.items():
        known = set(model.get("symptoms", set()))
        score = 0
        for symptom in symptoms:
            if symptom in known:
                score += 2
            elif any(symptom in item or item in symptom for item in known):
                score += 1
        if score > 0:
            ranked.append((score, disease))
    ranked.sort(key=lambda x: x[0], reverse=True)
    return [name for _, name in ranked[:3]]


def _unknown_condition_plan(form: dict, result: dict) -> dict:
    if form.get("unknown_mode", "yes") != "yes":
        return {}

    query = form.get("query", "")
    symptoms = parse_symptoms(query)
    likely = _rank_likely_conditions(query)
    if not likely:
        likely = [result["analysis"]["disease"]]

    follow_up_questions = [
        "When did symptoms start and are they getting better or worse?",
        "Do you have chest pain, shortness of breath, confusion, or fainting?",
        "Any known chronic disease, pregnancy, or recent infection exposure?",
    ]
    if "fever" in symptoms:
        follow_up_questions.append("What is the highest measured temperature and for how many days?")
    if "cough" in symptoms:
        follow_up_questions.append("Is the cough dry or with sputum, and any breathing discomfort?")
    if "dizziness" in symptoms or "weakness" in symptoms:
        follow_up_questions.append("Did dizziness occur with standing, and was there any fall or blackout?")

    suggested_tests = [
        "Vitals panel: BP, pulse, temperature, oxygen saturation",
        "CBC (complete blood count)",
        "Random blood sugar",
    ]
    if "fever" in symptoms:
        suggested_tests.append("Infection screen as per local protocol (for example malaria/dengue/COVID/flu)")
    if "chest pain" in query.lower() or "breath" in query.lower():
        suggested_tests.append("ECG and urgent physician evaluation")

    return {
        "likely_conditions": likely,
        "follow_up_questions": follow_up_questions,
        "suggested_tests": suggested_tests,
    }


def _build_solvers(form: dict, result: dict) -> dict:
    risk = result["care_plan"]["risk_prediction"]["level"]
    score = result["care_plan"]["risk_prediction"]["score"]
    disease = result["analysis"]["disease"]

    cost_plan = [
        "Prioritize generic medicines and government-supported pharmacies.",
        "Use PHC/community clinics before tertiary referral for non-critical follow-up.",
    ]
    if form["budget"] == "low":
        cost_plan.append("Enable low-cost mode: bundle labs into essential panel only.")

    connectivity_plan = ["Keep printable one-page triage summary for offline continuity."]
    if form["internet"] in {"poor", "intermittent"}:
        connectivity_plan.extend([
            "Switch reminders to SMS/voice call instead of app notifications.",
            "Use store-and-forward updates through ASHA worker/community volunteer.",
        ])
    else:
        connectivity_plan.append("Use teleconsultation and periodic remote vitals check-ins.")

    adherence_plan = [
        "Create morning-evening medication checklist with caregiver confirmation.",
        "Use color-coded pill box and missed-dose escalation rule (>2 misses/week).",
    ]

    home_safety_plan = [
        "Maintain symptom/vitals diary with date-time stamps.",
        "Add fall-risk reduction: anti-slip mats, night lights, reachable emergency contact card.",
    ]
    if form["living_alone"] == "yes":
        home_safety_plan.append("Set automated daily wellbeing check and neighbor escalation contact.")

    language_plan = [
        f"Provide instructions in preferred language: {form['language']}.",
        "Use plain-language discharge summary with icon-based instructions.",
    ]

    referral_plan = [
        f"Current condition '{disease}' at risk score {score}% -> triage route: {risk}.",
        "If red flags appear (chest pain, breathlessness, confusion), route to emergency immediately.",
        "Otherwise schedule specialist referral within 24-72 hours based on risk.",
    ]

    return {
        "cost_plan": cost_plan,
        "connectivity_plan": connectivity_plan,
        "adherence_plan": adherence_plan,
        "home_safety_plan": home_safety_plan,
        "language_plan": language_plan,
        "referral_plan": referral_plan,
    }


def _device_vitals_plan(form: dict, result: dict) -> dict:
    pulse = int(_to_number(form.get("camera_pulse", ""), 0))
    temp = _to_number(form.get("device_temp", ""), 0.0)
    condition_score = int(_to_number(form.get("body_condition", ""), 0))

    points = []
    status = "No accessory vitals captured yet"

    if pulse > 0:
        points.append(f"Camera/PPG pulse estimate: {pulse} bpm.")
        if pulse > 110:
            points.append("Pulse appears high; rest and recheck after 5 minutes.")
        elif pulse < 55:
            points.append("Pulse appears low; verify manually and monitor symptoms.")

    if temp > 0:
        points.append(f"Device-assisted temperature: {temp:.1f} C.")
        if temp >= 38.0:
            points.append("Fever pattern detected from accessory input.")

    if condition_score > 0:
        points.append(f"Body condition score: {condition_score}/100.")
        if condition_score < 45:
            points.append("Low body condition score: prioritize hydration, rest, and clinician review.")

    if points:
        status = "Accessory capture integrated into triage"
        points.append(
            f"Combined with model risk: {result['care_plan']['risk_prediction']['level']} ({result['care_plan']['risk_prediction']['score']}%)."
        )

    return {"status": status, "points": points}


@app.post("/api/analyze")
def api_analyze():
    data = request.get_json(silent=True) or {}
    result = build_response(data)
    return jsonify(result)


@app.post("/api/passive_monitor")
def passive_monitor():
    data = request.get_json(silent=True) or {}

    pulse = int(_to_number(data.get("pulse"), 0))
    temperature = _to_number(data.get("temperature"), 0.0)
    body_condition = int(_to_number(data.get("body_condition"), 0))
    age = int(_to_number(data.get("age"), 30))
    bmi = _to_number(data.get("bmi"), 24.0)
    conditions = data.get("conditions", "")
    query = str(data.get("query", "")).strip()

    fever = temperature >= 38.0 if temperature > 0 else False
    heart_status = "normal"
    if pulse > 110:
        heart_status = "tachycardia-pattern"
    elif 0 < pulse < 55:
        heart_status = "bradycardia-pattern"

    auto_symptoms = []
    if fever:
        auto_symptoms.append("fever")
    if heart_status == "tachycardia-pattern":
        auto_symptoms.append("dizziness")
    if heart_status != "normal":
        auto_symptoms.append("chest discomfort")
    if body_condition and body_condition < 45:
        auto_symptoms.append("weakness")

    auto_query = ", ".join(auto_symptoms) if auto_symptoms else (query or "passive monitoring ongoing")
    payload = {
        "query": auto_query,
        "symptoms": auto_query,
        "conditions": conditions,
        "age": age,
        "bmi": bmi,
        "heart_rate": pulse or "",
        "temperature": temperature or "",
        "oxygen_saturation": "",
    }

    result = build_response(payload)
    action = result["analysis"]["triage"]["message"]

    return jsonify(
        {
            "pulse": pulse,
            "temperature": temperature if temperature > 0 else 0.0,
            "fever": fever,
            "heart_status": heart_status,
            "body_condition": body_condition,
            "risk_level": result["care_plan"]["risk_prediction"]["level"],
            "risk_score": result["care_plan"]["risk_prediction"]["score"],
            "action": action,
        }
    )


@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    emergency = False
    solvers = {}
    unknown_plan = {}
    skin_result = {}
    device_plan = {}
    form = dict(DEFAULT_FORM)
    active_feature = ""

    if request.method == "POST":
        action = request.form.get("action", "analyze").strip()

        if action.startswith("preset:"):
            key = action.split(":", 1)[1]
            if key in PRESETS:
                form.update(PRESETS[key])
                result = build_response(_build_payload(form))
        elif action.startswith("feature:"):
            active_feature = action.split(":", 1)[1]
            form["query"] = FEATURE_PROMPTS.get(active_feature, form["query"])
            if active_feature == "epidemic":
                form["case_type"] = "epidemic"
            if active_feature == "fall":
                form["event"] = "fall detected"
            if active_feature == "unknown":
                form["unknown_mode"] = "yes"
            result = build_response(_build_payload(form))
        else:
            for key in form.keys():
                form[key] = request.form.get(key, "").strip() or form[key]
            result = build_response(_build_payload(form))

        uploaded = request.files.get("skin_image")
        if uploaded and uploaded.filename:
            skin_result = _analyze_skin_image(uploaded)

        if result:
            triage_status = result["analysis"]["triage"]["status"]
            risk_level = result["care_plan"]["risk_prediction"]["level"]
            red_flags = result["analysis"]["red_flags"]
            emergency = triage_status == "Urgent attention" or risk_level == "High" or bool(red_flags)
            solvers = _build_solvers(form, result)
            unknown_plan = _unknown_condition_plan(form, result)
            device_plan = _device_vitals_plan(form, result)

    return render_template_string(
        HTML,
        feature_items=FEATURE_ITEMS,
        active_feature=active_feature,
        result=result,
        emergency=emergency,
        form=form,
        solvers=solvers,
        unknown_plan=unknown_plan,
        skin_result=skin_result,
        device_plan=device_plan,
    )


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
