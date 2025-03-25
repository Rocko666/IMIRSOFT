import os
from flask import Flask, request, jsonify
import requests
import openai
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
WHATSAPP_API_KEY = os.getenv("WHATSAPP_API_KEY")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY
app = Flask(__name__)

# URL base de la API de WhatsApp Business
WHATSAPP_API_URL = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"

# Función para enviar mensajes por WhatsApp
def send_whatsapp_message(to_number, message):
    headers = {
        "Authorization": f"Bearer {WHATSAPP_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": message}
    }
    response = requests.post(WHATSAPP_API_URL, json=payload, headers=headers)
    return response.json()

# Función para generar respuestas con OpenAI
def generate_openai_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente de WhatsApp útil y conciso."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# Webhook para recibir mensajes de WhatsApp
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if data.get("entry"):
        entry = data["entry"][0]
        changes = entry.get("changes")
        if changes and changes[0].get("value").get("messages"):
            message = changes[0]["value"]["messages"][0]
            sender_number = message["from"]
            message_body = message["text"]["body"]

            # Procesar el mensaje con OpenAI
            ai_response = generate_openai_response(message_body)

            # Enviar respuesta por WhatsApp
            send_whatsapp_message(sender_number, ai_response)

    return jsonify({"status": "success"}), 200

# Verificación del webhook (requerido por Meta)
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    verify_token = "tu_token_de_verificacion"  # Debe coincidir con el que configures en Meta
    if request.args.get("hub.verify_token") == verify_token:
        return request.args.get("hub.challenge"), 200
    return "Token inválido", 403

if __name__ == "__main__":
    app.run(debug=True, port=5000)
    