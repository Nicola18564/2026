function toList(text) {
  if (!text || !text.trim()) return [];
  return text.split(",").map((x) => x.trim()).filter(Boolean);
}

function toNumberOrNull(v) {
  if (v === "" || v === null || v === undefined) return null;
  const n = Number(v);
  return Number.isNaN(n) ? null : n;
}

function addMessage(type, text) {
  const chatBox = document.getElementById("chat_box");
  const div = document.createElement("div");
  div.className = `msg ${type}`;
  div.textContent = text;
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function buildPayload() {
  return {
    query: document.getElementById("query").value,
    symptoms: toList(document.getElementById("symptoms").value),
    age: Number(document.getElementById("age").value || 30),
    bmi: Number(document.getElementById("bmi").value || 24),
    conditions: toList(document.getElementById("conditions").value),
    location: document.getElementById("location").value || "your area",
    mental_topic: document.getElementById("mental_topic").value || "stress",
    fitness_goal: document.getElementById("fitness_goal").value || "general",
    region: document.getElementById("region").value,
    resources: toList(document.getElementById("resources").value),
    accessibility_challenge: document.getElementById("accessibility_challenge").value,
    public_health_case: document.getElementById("public_health_case").value,
    elderly_event: document.getElementById("elderly_event").value,
    voice_text: document.getElementById("voice_text").value,
    vitals: {
      heart_rate: toNumberOrNull(document.getElementById("heart_rate").value),
      temperature: toNumberOrNull(document.getElementById("temperature").value),
      oxygen_saturation: toNumberOrNull(document.getElementById("oxygen_saturation").value),
      systolic_bp: toNumberOrNull(document.getElementById("systolic_bp").value),
      diastolic_bp: toNumberOrNull(document.getElementById("diastolic_bp").value),
    },
  };
}

async function runAssessment() {
  const payload = buildPayload();
  const output = document.getElementById("json_output");
  output.textContent = "Running assessment...";

  try {
    const res = await fetch("/api/assess", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();

    document.getElementById("disease_pill").textContent = `Condition: ${data.disease_detection.predicted_condition}`;
    document.getElementById("risk_pill").textContent = `Risk: ${data.risk_prediction.level} (${data.risk_prediction.score}%)`;
    document.getElementById("confidence_pill").textContent = `Confidence: ${data.disease_detection.confidence_percent}%`;
    output.textContent = JSON.stringify(data, null, 2);
  } catch (error) {
    output.textContent = `Error: ${error.message}`;
  }
}

function showEmergencyBlock() {
  const output = document.getElementById("json_output");
  output.textContent = JSON.stringify(
    {
      headline: "Emergency Guidance",
      steps: [
        "Call local emergency number immediately",
        "Keep airway clear and patient safe",
        "Share age, symptoms, and vitals with responders",
      ],
      warning: "Do not delay hospital care in severe symptoms",
    },
    null,
    2,
  );
}

async function sendChat() {
  const input = document.getElementById("chat_message");
  const message = input.value.trim();
  if (!message) return;

  addMessage("user", message);
  input.value = "";

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, age: 30, bmi: 24, conditions: [] }),
    });
    const data = await res.json();
    addMessage("bot", data.assistant_reply);
  } catch (error) {
    addMessage("bot", `Unable to reach backend: ${error.message}`);
  }
}

document.getElementById("assess_btn").addEventListener("click", runAssessment);
document.getElementById("emergency_btn").addEventListener("click", showEmergencyBlock);
document.getElementById("chat_send").addEventListener("click", sendChat);
document.getElementById("chat_message").addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    e.preventDefault();
    sendChat();
  }
});

addMessage("bot", "MediAssist ready. Enter symptoms to get diagnosis and monitoring guidance.");
