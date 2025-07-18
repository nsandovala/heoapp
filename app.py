# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import requests

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Configuración OpenRouter
API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("MODEL", "openai/gpt-4o-mini")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Palabras clave para activar lógica médica
TRIGGER_WORDS = ["dolor", "síntoma", "fiebre", "mareo", "cansancio", "tos", "vomito", "dolor de cabeza"]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat")
def chat():
    return render_template("chat.html")

@app.route("/api/chat", methods=["POST"])
def api_chat():
    user_message = request.json.get("message", "").lower()

    # Detectar si es contexto médico
    is_medical = any(word in user_message for word in TRIGGER_WORDS)

    # Prompt dinámico
    if is_medical:
        system_prompt = (
            "Eres HEO, un asistente empático y experto en bienestar. "
            "Si detectas síntomas, clasifica como LEVE, MEDIO o GRAVE y responde:\n"
            "1. LEVE → consejo natural + texto exacto: [CONSEJO_NATURAL]\n"
            "2. MEDIO → recomienda médico general + texto exacto: [MEDICO_LINK]\n"
            "3. GRAVE → recomienda urgencias + texto exacto: [URGENCIAS_LINK]\n"
            "Sé breve, humano y muy claro."
        )
    else:
        system_prompt = "Eres HEO, un asistente empático y experto en bienestar general."

    # Payload para OpenRouter
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    }

    try:
        response = requests.post(OPENROUTER_URL, headers=HEADERS, json=payload)
        response_data = response.json()
        heo_reply = response_data["choices"][0]["message"]["content"]

        # Reemplazar enlaces por botones estilizados
        heo_reply = heo_reply.replace(
            "[URGENCIAS_LINK]",
            '<br><a href="https://maps.google.com?q=urgencias+cercanas" class="btn-urgencias" target="_blank">🚨 Ubicar Urgencias Cercanas</a>'
        )

        heo_reply = heo_reply.replace(
            "[MEDICO_LINK]",
            '<br><a href="https://medicos.generales.cl" class="btn-medico" target="_blank">👨‍⚕️ Consultar Médico General</a>'
        )

        heo_reply = heo_reply.replace(
            "[CONSEJO_NATURAL]",
            '<br><a href="#consejo" class="btn-leve">🌱 Ver Consejos Naturales</a>'
        )

        return jsonify({"reply": heo_reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
