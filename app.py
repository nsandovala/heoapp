# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify, send_from_directory
from dotenv import load_dotenv
import os
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json

# ================================
# 1. CARGAR VARIABLES DE ENTORNO
# ================================
# Esto lee .env en Render o local (OPENROUTER_API_KEY y GOOGLE_CREDENTIALS)
load_dotenv()

app = Flask(__name__)

# ================================
# 2. CONFIGURACIÓN OPENROUTER
# ================================
API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("MODEL", "openai/gpt-4o-mini")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# ================================
# 3. GOOGLE SHEETS - CREDENCIALES
# ================================
# Las credenciales se guardan en Render en la variable GOOGLE_CREDENTIALS (JSON)
# Para local, copia el contenido de credentials.json en esa variable.
google_creds = os.getenv("GOOGLE_CREDENTIALS")

if not google_creds:
    raise Exception("❌ Falta la variable GOOGLE_CREDENTIALS en Render")

# Parsear el JSON y crear credenciales
creds_dict = json.loads(google_creds)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Abrir la hoja (asegúrate de compartir el Sheet con el email del servicio)
sheet = client.open("HEO_Metricas").sheet1  # Nombre exacto del Google Sheet

# ================================
# 4. PALABRAS CLAVE PARA INTENCIÓN
# ================================
TRIGGER_WORDS = ["dolor", "síntoma", "fiebre", "mareo", "cansancio", "tos", "vomito", "dolor de cabeza"]
TRIGGER_BUSINESS = ["negocio", "idea", "emprendimiento", "monetización", "startup", "empresa", "modelo de negocio"]

# ================================
# 5. RUTA PRINCIPAL PARA CHAT API
# ================================
@app.route("/api/chat", methods=["POST"])
def api_chat():
    user_message = request.json.get("message", "").lower()

    # Detectar intención (bienestar o negocio)
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
        system_prompt = "Eres HEO, asistente empático experto en bienestar general y creatividady ayuda comunitaria. Responde de forma clara, empática y útil."

    # Payload para OpenRouter
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    }

    try:
        # Llamada a la API OpenRouter
        response = requests.post(OPENROUTER_URL, headers=HEADERS, json=payload)
        response_data = response.json()
        heo_reply = response_data["choices"][0]["message"]["content"]

        # Reemplazar placeholders por botones
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

        # Guardar métrica en Google Sheets
        tipo = "Negocio" if is_business else "Bienestar" if is_medical else "General"
        sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_message, tipo, heo_reply])

        return jsonify({"reply": heo_reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ================================
# 6. RUTAS PARA PWA
# ================================
@app.route('/')
def home():
    return render_template("index.html")

@app.route('/chat')
def chat():
    return render_template("chat.html")

@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/service-worker.js')
def service_worker():
    return send_from_directory('static', 'service-worker.js')

# ================================
# 7. INICIAR SERVIDOR
# ================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
