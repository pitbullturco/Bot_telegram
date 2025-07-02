from flask import Flask, request, jsonify
import requests
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, CallbackContext
import os

app = Flask(__name__)

# Variáveis de ambiente
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MERCADO_PAGO_TOKEN = os.getenv("MERCADO_PAGO_TOKEN")
DRIVE_LINK = os.getenv("DRIVE_LINK")
VALOR_PAGAMENTO = float(os.getenv("VALOR_PAGAMENTO", "10.00"))

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dispatcher = Dispatcher(bot=bot, update_queue=None, workers=0, use_context=True)
usuarios_aguardando = {}

# 🔹 Comando /start no Telegram
def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    usuarios_aguardando["ultimo_usuario"] = chat_id  # Salva último usuário que chamou
    bot.send_message(
        chat_id=chat_id,
        text=(
            "🔐 Sou o *bot de pagamento do Jigsaw*.\n\n"
            "Para ter acesso ao nosso pack exclusivo, basta efetuar um pagamento via Pix de R$ {:.2f}.\n\n"
            "Clique no botão abaixo para gerar o QR Code de pagamento ou acesse:\n"
            "➡️ https://botpixgabriel.onrender.com/gerar-pix"
        ).format(VALOR_PAGAMENTO),
        parse_mode="Markdown"
    )

dispatcher.add_handler(CommandHandler("start", start))

# 🔹 Rota Webhook para receber mensagens do Telegram
@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return jsonify({"status": "ok"})

# 🔹 Geração de Pix
@app.route('/gerar-pix', methods=['POST'])
def gerar_pix():
    data = request.get_json()
    chat_id = data.get('chat_id', usuarios_aguardando.get("ultimo_usuario"))

    body = {
        "transaction_amount": VALOR_PAGAMENTO,
        "description": "Acesso ao pack Jigsaw",
        "payment_method_id": "pix",
        "payer": {"email": "pagador@teste.com"}
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

# 🔹 Notificação automática do Mercado Pago
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
            bot.send_message(
                chat_id=chat_id,
                text=f"✅ Pagamento confirmado com sucesso!\n\nAqui está seu acesso: {DRIVE_LINK}"
            )

    return jsonify({"status": "ok"})

# 🔹 Rota raiz
@app.route('/')
def home():
    return "Bot Pix Jigsaw online ✅"
