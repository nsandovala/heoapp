¡Bienvenido a HEO 2.0! Este proyecto representa un sistema empático de asistencia médica con IA, inspirado en una visión humanista y tecnológica. Este repositorio contiene el backend en Flask y un asistente basado en Groq (usando el modelo LLaMA 3).

---

## 🚀 ¿Cómo ejecutar este proyecto?

### Requisitos
- Python 3.8+
- Cuenta en [Render](https://render.com)
- Clave API de [Groq](https://console.groq.com)

### 1. Clonar repositorio

```bash
git clone https://github.com/tuusuario/heo2.0.git
cd heo2.0
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Variables de entorno

Crear un archivo `.env` con el siguiente contenido:

```env
GROQ_API_KEY=tu_clave_de_api_aqui
```

### 4. Ejecutar localmente

```bash
python app.py
```

---

## 🌐 Deploy en Render

1. Crear nuevo servicio Web (Python 3).
2. Conectar con tu repositorio.
3. Setear comandos:

- Comando de build: `pip install -r requirements.txt`
- Comando de inicio: `gunicorn app:app`

4. Agregar variables de entorno (`GROQ_API_KEY`) en el panel de Render.
5. Listo 🎉

---

## 📁 Estructura

```
├── app.py
├── requirements.txt
├── Procfile
├── templates/
│   └── index.html
├── static/
│   └── style.css
└── audio/
    └── [voces mp3]
```

---

## 🧠 Propósito del Proyecto

HEO busca entregar asistencia emocional y médica preventiva, con una interfaz accesible y capaz de responder a necesidades en tiempo real, ayudando especialmente a personas en situaciones de vulnerabilidad.

---

## ✨ Créditos

Creado por Nelson Sandoval Arias – Powered by OpenAI, con la visión de transformar la asistencia humana.

---

🕊️ *"Stay humble, stay faithful."*
