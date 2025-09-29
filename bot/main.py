import os
import random
import asyncio
from datetime import datetime, timedelta
from telegram.ext import Application
from openai import OpenAI

# Переменные окружения
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("1002971665440")  # ID канала (например -1001234567890)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)


async def generate_post():
    """Генерация текста поста через GPT"""
    styles = [
        "Сделай короткий пост про серые схемы заработка через ИИ, добавь эмодзи.",
        "Придумай полезный лайфхак: как использовать ChatGPT для автоматизации дохода.",
        "Напиши пост с лёгким юмором про заработок с помощью ИИ.",
        "Составь мини-инструкцию, как можно зарабатывать, используя MidJourney или DALL·E.",
        "Напиши вопрос к подписчикам, связанный с ИИ и заработком."
    ]

    prompt = random.choice(styles)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=350
    )

    return response.choices[0].message.content.strip()


async def generate_image():
    """Генерация картинки через DALL·E"""
    prompts = [
        "Futuristic AI hacking style illustration, cyberpunk theme",
        "Minimalistic infographic style about making money with AI",
        "Funny meme-style illustration about AI and money",
        "Stylized image of robot businessman earning online",
    ]

    prompt = random.choice(prompts)

    response = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024"
    )

    return response.data[0].url


async def post_task(app):
    """Фоновая задача: автопостинг"""
    while True:
        # выбираем время (12:00 или 18:00 ± рандомные минуты)
        hours = [12, 18]
        target_hour = random.choice(hours)
        target_minute = random.randint(0, 20)

        now = datetime.now()
        target = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)

        if target < now:
            target += timedelta(days=1)

        wait_time = (target - now).total_seconds()
        print(f"Следующий пост через {wait_time/60:.1f} минут")
        await asyncio.sleep(wait_time)

        # генерируем текст поста
        post_text = await generate_post()

        # случайно решаем — текст или текст + картинка
        if random.random() < 0.3:  # примерно 30% постов будут с картинкой
            image_url = await generate_image()
            await app.bot.send_photo(chat_id=CHAT_ID, photo=image_url, caption=post_text)
        else:
            await app.bot.send_message(chat_id=CHAT_ID, text=post_text)


async def main():
    app = Application.builder().token(TOKEN).build()

    # запускаем фоновую задачу
    asyncio.create_task(post_task(app))

    # чтобы Render держал процесс живым
    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
