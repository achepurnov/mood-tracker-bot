import os
import json
import asyncio
from datetime import time
from pytz import timezone

from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
SUBS_FILE = "subscribers.json"
TRACKER_URL = "https://achepurnov.github.io/mood-tracker/"

tz = timezone("Europe/Moscow")


def load_subs():
    if os.path.exists(SUBS_FILE):
        with open(SUBS_FILE) as f:
            return set(json.load(f))
    return set()


def save_subs(subs):
    with open(SUBS_FILE, "w") as f:
        json.dump(list(subs), f)


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    subs = load_subs()
    chat_id = update.effective_chat.id
    subs.add(chat_id)
    save_subs(subs)
    await update.message.reply_text(
        "привет! теперь я буду напоминать тебе отмечать настроение каждый вечер 🌙\n\n"
        f"трекер: {TRACKER_URL}\n\n"
        "/stop — отписаться\n"
        "/mood — ссылка на трекер"
    )


async def stop(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    subs = load_subs()
    chat_id = update.effective_chat.id
    subs.discard(chat_id)
    save_subs(subs)
    await update.message.reply_text("отписал. если захочешь снова — /start")


async def mood(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"трекер настроения: {TRACKER_URL}")


async def daily_remind(app: Application):
    subs = load_subs()
    bot = app.bot
    for chat_id in subs:
        try:
            await bot.send_message(
                chat_id,
                "как дела? не забудь отметить настроение 🌙\n"
                f"{TRACKER_URL}"
            )
        except Exception:
            pass


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("mood", mood))

    if os.environ.get("DAILY_REMIND") == "1":
        app.job_queue.run_daily(daily_remind, time(21, 0, tzinfo=tz))

    app.run_polling()


if __name__ == "__main__":
    main()
