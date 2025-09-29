import os
import asyncio
import nest_asyncio
from datetime import datetime
from telegram import Bot
from telegram.ext import Application, CommandHandler
from openai import OpenAI

# Чтобы Render не ругался на event loop
nest_asyncio.apply()

# === Переменные окружения ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# === Айди канала (фиксированный) ===
CHANNEL_ID = -1002971665440

# === Telegram и OpenAI клиенты ===
application = Application.builder().token(BOT_TOKEN).build()
bot = Bot(token=BOT_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)


# ======= Генерация текста =======
async def generate_text():
    prompt = (
        "Сделай короткий пост для Telegram-канала о бело-серых схемах заработка "
        "и автоматизации через ИИ. Максимум 2 предложения. Стиль — лаконичный, "
        "с элементом мотивации. Добавь 1 эмодзи в тему."
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=80,
    )
    return response.choices[0].message.content.strip()


# ======= Генерация картинки =======
async def generate_image():
    try:
        response = client.images.generate(
            model="gpt-image-1",
            prompt="Абстрактная иллюстрация заработка с помощью ИИ, минимализм, современный стиль, с серо-белой палитрой",
            size="1024x1024"
        )
        return response.data[0].url
    except Exception as e:
        print(f"Ошибка генерации картинки: {e}")
        return None


# ======= Автопостинг =======
async def autopost():
    while True:
        try:
            text = await generate_text()
            image = await generate_image()

            if image:
                await bot.send_photo(chat_id=CHANNEL_ID, photo=image, caption=text)
            else:
                await bot.send_message(chat_id=CHANNEL_ID, text=text)

            print(f"[{datetime.now()}] Автопостинг отправлен")
        except Exception as e:
            print(f"Ошибка при автопостинге: {e}")

        # Интервал: каждые 3 часа
        await asyncio.sleep(3 * 60 * 60)


# ======= Команды =======
async def start(update, context):
    await update.message.reply_text("✅ Бот запущен и готов постить!")


async def post(update, context):
    """Принудительный пост по команде /post"""
    try:
        text = await generate_text()
        image = await generate_image()

        if image:
            await bot.send_photo(chat_id=CHANNEL_ID, photo=image, caption=text)
        else:
            await bot.send_message(chat_id=CHANNEL_ID, text=text)

        await update.message.reply_text("📨 Пост отправлен в канал!")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")


# ======= Основной запуск =======
async def main():
    # Команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("post", post))

    # Автопостинг параллельно
    asyncio.create_task(autopost())

    # Запуск
    await application.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
