import os
import json
import sys
from telegram import Bot

TOKEN = os.environ.get("BOT_TOKEN", "8938255790:AAHzlrwt8Lq1B4WCYCsPoY8LkK-jYxFsn4E")
SUBS_FILE = os.path.join(os.path.dirname(__file__), "subscribers.json")
TRACKER_URL = "https://achepurnov.github.io/mood-tracker/"


def load_subs():
    if os.path.exists(SUBS_FILE):
        with open(SUBS_FILE) as f:
            return set(json.load(f))
    return set()


def save_subs(subs):
    with open(SUBS_FILE, "w") as f:
        json.dump(list(subs), f)


def send_remind():
    subs = load_subs()
    bot = Bot(TOKEN)
    for chat_id in subs:
        try:
            bot.send_message(
                chat_id,
                "как дела? не забудь отметить настроение 🌙\n"
                f"{TRACKER_URL}"
            )
        except Exception:
            pass
    print(f"reminded {len(subs)} subscribers")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "remind":
        send_remind()
    else:
        # interactive mode — polling for commands
        from telegram import Update
        from telegram.ext import Application, CommandHandler, ContextTypes

        async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
            chat_id = update.effective_chat.id
            subs = load_subs()
            subs.add(chat_id)
            save_subs(subs)
            await update.message.reply_text(
                "как дела? настроение как? 🌙\n\n"
                "теперь каждый вечер я буду напоминать тебе отмечать настроение. "
                "заходишь на сайт, выбираешь смайлик, и всё — день прожит не зря ☝️\n\n"
                f"{TRACKER_URL}\n\n"
                "/stop — отписаться от напоминаний"
            )

        async def stop(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
            chat_id = update.effective_chat.id
            subs = load_subs()
            subs.discard(chat_id)
            save_subs(subs)
            await update.message.reply_text("ок, отписал. если захочешь снова — /start")

        async def mood(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
            await update.message.reply_text(f"трекер: {TRACKER_URL}")

        app = Application.builder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("stop", stop))
        app.add_handler(CommandHandler("mood", mood))
        print("bot polling...")
        app.run_polling()
