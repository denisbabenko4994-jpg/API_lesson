import os
import re
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Загружаем переменные из .env
load_dotenv()

YC_API_KEY = os.getenv("YC_API_KEY")
YC_FOLDER_ID = os.getenv("YC_FOLDER_ID")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


# Функция для очистки от LaTeX-мусора и красивой замены знаков
def clean_latex(text: str) -> str:
    # Заменяем \times на красивый знак умножения ×
    text = text.replace(r"\times", "×")
    # Заменяем степенные обозначения 10^{-34} или 10^-34 на понятный текст
    text = re.sub(r"10\^\{?-?(\d+)\}?", r"10⁻\1", text)
    # Убираем знаки доллар $
    text = text.replace("$", "")
    return text


# Функция обращения к Yandex GPT
def ask_yandex_gpt(prompt_text: str) -> str:
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {YC_API_KEY}"
    }
    data = {
        "modelUri": f"gpt://{YC_FOLDER_ID}/yandexgpt/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 0.5,  # Баланс между точностью и естественностью речи
            "maxTokens": "2000"
        },
        "messages": [
            {
                "role": "system",
                "text": (
                    "Ты — эксперт-консультант. Отвечай строго, точно и понятным, доступным языком. "
                    "Избегай детских метафор, оценочных слов (например, 'волшебный', 'чудесный') и излишних упрощений. "
                    "Формулируй мысли профессионально, логично и структурно. "
                    "Не используй LaTeX-разметку со знаками доллара $, пиши числа и формулы в обычном тексте."
                )
            },
            {
                "role": "user",
                "text": prompt_text
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        raw_text = result["result"]["alternatives"][0]["message"]["text"]
        return clean_latex(raw_text)
    else:
        return f"Ошибка Yandex API ({response.status_code}): {response.text}"


# Обработчик команды /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Здравствуйте! Напишите ваш вопрос, и я предоставлю точный и подробный ответ.")


# Обработчик текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.reply_chat_action("typing")

    gpt_response = ask_yandex_gpt(user_text)

    try:
        await update.message.reply_text(gpt_response, parse_mode="Markdown")
    except Exception:
        await update.message.reply_text(gpt_response)


if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот перезапущен со строгим стилем!")
    app.run_polling()