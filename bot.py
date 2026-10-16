import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from transcribe import transcribe_url

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не найден в .env")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! 👋\n\n"
        "Я готов расшифровывать видео.\n"
        "Пришли мне ссылку на Instagram или TikTok."
    )

def split_text(text: str, max_length: int = 4000) -> list[str]:
    if len(text) <= max_length:
        return [text]

    parts = []
    remaining = text.strip()

    while len(remaining) > max_length:
        chunk = remaining[:max_length]

        # Сначала ищем перенос строки
        split_at = chunk.rfind("\n")

        # Если подходящего переноса нет — ищем конец предложения
        if split_at < max_length * 0.5:
            split_at = max(
                chunk.rfind(". "),
                chunk.rfind("! "),
                chunk.rfind("? "),
            )

        # Если и предложения нет — режем по последнему пробелу
        if split_at < max_length * 0.5:
            split_at = chunk.rfind(" ")

        # Совсем крайний случай
        if split_at <= 0:
            split_at = max_length

        parts.append(remaining[:split_at].strip())
        remaining = remaining[split_at:].strip()

    if remaining:
        parts.append(remaining)

    return parts

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if not url.startswith(("http://", "https://")):
        await update.message.reply_text(
            "Пришли мне ссылку на видео из Instagram или TikTok."
        )
        return

    await update.message.reply_text(
        "⏳ Подожди немного — я не завис, просто выполняю твоё задание 🙂"
    )

    try:
        text = transcribe_url(url)

        if not text.strip():
            await update.message.reply_text(
                "Не удалось получить текст из этого видео."
            )
            return

        for part in split_text(text):
            await update.message.reply_text(part)

    except Exception as e:
        print(f"ОШИБКА ПРИ ОБРАБОТКЕ: {e}")

        await update.message.reply_text(
            "Не получилось обработать это видео. "
            "Попробуй проверить ссылку или отправить другое видео."
        )

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен. Нажми Ctrl+C для остановки.")

    app.run_polling()


if __name__ == "__main__":
    main()
