from flask import Flask, render_template, request, jsonify, send_from_directory
from dotenv import load_dotenv
import os
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

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

# ✅ Configuración Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("HEO_Metricas").sheet1  # Nombre del Google Sheet

# Palabras clave
TRIGGER_WORDS = ["dolor", "síntoma", "fiebre", "mareo", "cansancio", "tos", "vomito", "dolor de cabeza"]
TRIGGER_BUSINESS = ["negocio", "idea", "emprendimiento", "monetización", "startup", "empresa"]

@app.route("/api/chat", methods=["POST"])
def api_chat():
    user_message = request.json.get("message", "").lower()

    # Detectar intención
    is_medical = any(word in user_message for word in TRIGGER_WORDS)
    is_business = any(word in user_message for word in TRIGGER_BUSINESS)

    # Prompt dinámico
    if is_medical:
        system_prompt = """
        Eres HEO, un asistente empático experto en bienestar.
        Si detectas síntomas, clasifica como LEVE, MEDIO o GRAVE y responde:
        [CONSEJO_NATURAL], [MEDICO_LINK], [URGENCIAS_LINK].
        Sé breve, humano y muy claro.
        """
    elif is_business:
        system_prompt = """
        Eres HEO, un asistente estratégico que aplica el Método Códex Learning Loop™.
        Objetivo: Genera ideas de negocio creativas y accionables.
        Formato:
        ✅ IDEA: breve y diferenciada
        💡 ¿Por qué funciona?: razón lógica
        🚀 Primeros pasos: 3 acciones claras
        📊 Escalabilidad: cómo crecer rápido y barato
        """
    else:
        system_prompt = "Eres HEO, asistente empático experto en bienestar general y creatividad."

    # Llamada a OpenRouter
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

        # Reemplazar enlaces por botones
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

        # ✅ Guardar en Google Sheets
        tipo = "Negocio" if is_business else "Bienestar" if is_medical else "General"
        sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_message, tipo, heo_reply])

        return jsonify({"reply": heo_reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ✅ Rutas para PWA (si decides implementarlo)
@app.route('/manifest.json')
def manifest():
    return send_from_directory('.', 'manifest.json')

@app.route('/service-worker.js')
def service_worker():
    return send_from_directory('.', 'service-worker.js')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
