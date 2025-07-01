
# Instruções para publicar no Render

1. Acesse https://render.com e crie uma conta
2. Crie um novo Web Service
3. Envie os arquivos deste projeto
4. Defina o comando de inicialização: gunicorn bot:app
5. Adicione as variáveis de ambiente:
    - TELEGRAM_BOT_TOKEN
    - MERCADO_PAGO_TOKEN
    - DRIVE_LINK
    - VALOR_PAGAMENTO
6. Após o deploy, use a URL do Render como webhook no Mercado Pago: https://seunome.onrender.com/notificacao
