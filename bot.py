
from flask import Flask, request, jsonify
import requests
from telegram import Bot
import os

app = Flask(__name__)

# Configurações via variáveis de ambiente
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MERCADO_PAGO_TOKEN = os.getenv("MERCADO_PAGO_TOKEN")
DRIVE_LINK = os.getenv("DRIVE_LINK")
VALOR_PAGAMENTO = float(os.getenv("VALOR_PAGAMENTO", "10.00"))

bot = Bot(token=TELEGRAM_BOT_TOKEN)
usuarios_aguardando = {}

@app.route('/gerar-pix', methods=['POST'])
def gerar_pix():
    data = request.get_json()
    chat_id = data.get('chat_id')

    body = {
        "transaction_amount": VALOR_PAGAMENTO,
        "description": "Acesso ao pack Jigsaw",
        "payment_method_id": "pix",
        "payer": {
            "email": "pagador@teste.com"
        }
    }

    headers = {
        "Authorization": f"Bearer {MERCADO_PAGO_TOKEN}",
        "Content-Type": "application/json"
    }

    res = requests.post("https://api.mercadopago.com/v1/payments", json=body, headers=headers)
    result = res.json()

    payment_id = result["id"]
    usuarios_aguardando[payment_id] = chat_id

    qr_code_base64 = result['point_of_interaction']['transaction_data']['qr_code_base64']
    return jsonify({"qr_base64": qr_code_base64, "id": payment_id})

@app.route('/notificacao', methods=['POST'])
def notificacao():
    data = request.json
    payment_id = data.get("data", {}).get("id")
    headers = {"Authorization": f"Bearer {MERCADO_PAGO_TOKEN}"}
    res = requests.get(f"https://api.mercadopago.com/v1/payments/{payment_id}", headers=headers)
    result = res.json()

    status = result.get("status")
    if status == "approved":
        chat_id = usuarios_aguardando.get(payment_id)
        if chat_id:
            bot.send_message(chat_id=chat_id, text=f'✅ Pagamento confirmado! Aqui está seu acesso: https://drive.google.com/drive/folders/169K1_jRdvYcQvydz7HicB3OlQHuRGJaX?usp=drive_link')
{DRIVE_LINK}")
    return jsonify({"status": "ok"})

@app.route('/')
def home():
    return "Bot Pix Jigsaw online ✅"
