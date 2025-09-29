import os
from telegram.ext import Application, CommandHandler

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PORT = int(os.environ.get("PORT", 8443))  # Render сам даёт PORT

# Команда /start
async def start(update, context):
    await update.message.reply_text("Бот запущен и работает через Render 🚀")

def main():
    # Создаём приложение
    app = Application.builder().token(TOKEN).build()

    # Хэндлеры
    app.add_handler(CommandHandler("start", start))

    # Включаем webhook вместо polling
    app.run_webhook(
        listen="0.0.0.0",               # слушаем все адреса
        port=PORT,                      # порт от Render
        url_path=TOKEN,                 # секретный путь = токен
        webhook_url=f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}/{TOKEN}"
    )

if __name__ == "__main__":
    main()
