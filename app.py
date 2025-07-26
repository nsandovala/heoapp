# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import datetime
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)
CORS(app)

# ================================
# 1. CONFIGURACIÓN DE GOOGLE SHEETS
# ================================
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name("credenciales.json", scope)
client = gspread.authorize(creds)
sheet = client.open("HEO_SENTINEL_LOGS").sheet1

# ================================
# 2. CONFIGURACIÓN OPENROUTER
# ================================
openai.api_key = os.getenv("OPENROUTER_API_KEY")
openai.api_base = "https://openrouter.ai/api/v1"

# ================================
# 3. MODELO A UTILIZAR
# ================================
model = "mistralai/mixtral-8x7b-instruct"

# ================================
# 4. PALABRAS CLAVE PARA DETECTAR INTENCIÓN
# ================================
TRIGGER_WORDS = ["dolor", "síntoma", "fiebre", "mareo", "cansancio", "tos", "vómito", "gripe", "resfriado", "infección"]
TRIGGER_BUSINESS = ["negocio", "idea", "emprendimiento", "monetizar", "empresa", "proyecto", "modelo de negocio"]

# ================================
# 5. RESPUESTAS PERSONALIZADAS
# ================================
respuestas = {
    "Bienestar": """
EVALUACIÓN DE BIENESTAR:

Nivel leve → Recomendación natural (infusiones, reposo, hidratación).
Nivel medio → Sugerencia de medicina general con receta.
Nivel grave → Acudir a urgencias. En caso de duda, contacto médico verificado.

🧠 Esta respuesta es informativa. No reemplaza evaluación clínica real.
""",

    "Legal": """
Asistencia Legal Inicial:

1. Describe tu caso en una frase.
2. ¿Qué esperas lograr? (resolver conflicto, redactar documento, etc.)
3. ¿Urgencia? ¿Plazo límite?

Luego de eso, puedo ayudarte a estructurar tu solicitud con el Método Códex:
- Claridad del problema
- Objetivo deseado
- Estrategia legal preliminar

⚖️ Este sistema no reemplaza asesoría jurídica profesional.
""",

    "Creativo": """
Laboratorio Creativo Activado:

🎨 Método Códex Learning Loop:
1. Define el objetivo creativo
2. Lanza ideas iniciales
3. Explora variaciones locas
4. Refina lo mejor
5. Prueba con feedback real

¡Estoy listo para co-crear contigo! ¿Por dónde comenzamos?
""",

    "Negocio": """
Mentoría Inicial de Negocios:

🧠 Método Códex Aplicado:
1. Define la idea central en 1 frase
2. ¿Para quién es? ¿Qué problema resuelve?
3. ¿Cómo ganarías dinero con ello?

Responde estas 3 preguntas y te ayudo a modelar tu idea paso a paso.
"""
}

# ================================
# 6. RUTA PRINCIPAL DEL CHAT
# ================================
@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_input = data.get('message', '')

        if not user_input:
            return jsonify({'error': 'Mensaje vacío'}), 400

        # Clasificación según intención
        lower_input = user_input.lower()
        if any(p in lower_input for p in TRIGGER_WORDS):
            respuesta = respuestas["Bienestar"]
        elif "contrato" in lower_input or "demanda" in lower_input or "juicio" in lower_input:
            respuesta = respuestas["Legal"]
        elif any(p in lower_input for p in TRIGGER_BUSINESS):
            respuesta = respuestas["Negocio"]
        elif "nombre creativo" in lower_input or "slogan" in lower_input or "marca" in lower_input:
            respuesta = respuestas["Creativo"]
        else:
            # Si no detecta intención clara, se va al LLM
            messages = [
                {"role": "system", "content": "Eres HEO, un asistente de bienestar, creatividad y ayuda comunitaria. Responde de forma clara, empática y útil."},
                {"role": "user", "content": user_input}
            ]
            completion = openai.ChatCompletion.create(
                model=model,
                messages=messages
            )
            respuesta = completion.choices[0].message['content']

        # Log en Google Sheets
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([now, user_input, respuesta])

        return jsonify({'message': respuesta})

    except Exception as e:
        print(f"ERROR: {e}")
        return jsonify({'error': 'Error al procesar la solicitud'}), 500

# ================================
# 7. RUN FLASK
# ================================
if __name__ == '__main__':
    app.run(debug=True)
