import json
import sqlite3
import requests
from flask import Flask, jsonify, render_template, Response
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ContextTypes, filters
)
from config import BOT_TOKEN, CHANNEL, WEBSITE_URL, MAX_MEDIA

DB = "media.db"
app_web = Flask(__name__)

def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS media (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_message_id INTEGER NOT NULL,
            media_type TEXT NOT NULL,
            file_id TEXT NOT NULL,
            caption TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            telegram_file_path TEXT DEFAULT ''
        )
    """)
    conn.commit()
    conn.close()

def save_media(message):
    media_type = None
    file_id = None

    if message.photo:
        media_type = "photo"
        file_id = message.photo[-1].file_id
    elif message.video:
        media_type = "video"
        file_id = message.video.file_id

    if not file_id:
        return

    conn = db()
    conn.execute(
        "INSERT INTO media (telegram_message_id, media_type, file_id, caption) VALUES (?, ?, ?, ?)",
        (message.message_id, media_type, file_id, message.caption or "")
    )
    conn.commit()
    conn.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user:
        return

    button = KeyboardButton(
        text="🌐 Open Media Website",
        web_app=WebAppInfo(url=WEBSITE_URL)
    )
    keyboard = ReplyKeyboardMarkup([[button]], resize_keyboard=True)

    await update.message.reply_text(
        "🌐 নিচের বাটনে চাপলে Telegram-এর ভেতরেই Media Website খুলবে।",
        reply_markup=keyboard
    )

async def channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Bot must be an administrator in the channel.
    if update.channel_post:
        message = update.channel_post
        media_type = None
        file_id = None

        if message.photo:
            media_type = "photo"
            file_id = message.photo[-1].file_id
        elif message.video:
            media_type = "video"
            file_id = message.video.file_id

        if file_id:
            tg_file = await context.bot.get_file(file_id)
            conn = db()
            conn.execute(
                "INSERT INTO media (telegram_message_id, media_type, file_id, caption, telegram_file_path) VALUES (?, ?, ?, ?, ?)",
                (message.message_id, media_type, file_id, message.caption or "", tg_file.file_path or "")
            )
            conn.commit()
            conn.close()

async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or not update.message:
        return

    try:
        data = json.loads(update.message.web_app_data.data)
        media_id = int(data["media_id"])
    except Exception:
        await update.message.reply_text("❌ Invalid media selection.")
        return

    conn = db()
    row = conn.execute(
        "SELECT media_type, file_id, caption FROM media WHERE id = ?",
        (media_id,)
    ).fetchone()
    conn.close()

    if not row:
        await update.message.reply_text("❌ Media not found.")
        return

    caption = row["caption"] or ""
    if row["media_type"] == "photo":
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=row["file_id"],
            caption=caption[:1024] if caption else None
        )
    elif row["media_type"] == "video":
        await context.bot.send_video(
            chat_id=update.effective_chat.id,
            video=row["file_id"],
            caption=caption[:1024] if caption else None
        )

@app_web.route("/")
def home():
    return render_template("index.html", channel=CHANNEL)

@app_web.route("/api/media")
def media_api():
    conn = db()
    rows = conn.execute(
        "SELECT id, media_type, caption, created_at FROM media ORDER BY id DESC LIMIT ?",
        (MAX_MEDIA,)
    ).fetchall()
    conn.close()

    return jsonify([
        {
            "id": r["id"],
            "type": r["media_type"],
            "caption": r["caption"],
            "created_at": r["created_at"]
        }
        for r in rows
    ])

@app_web.route("/media/<int:media_id>")
def media_file(media_id):
    conn = db()
    row = conn.execute(
        "SELECT media_type, telegram_file_path FROM media WHERE id = ?",
        (media_id,)
    ).fetchone()
    conn.close()

    if not row or not row["telegram_file_path"]:
        return "Media not found", 404

    # Keep the bot token server-side; never expose it to the browser.
    url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{row['telegram_file_path']}"
    try:
        r = requests.get(url, timeout=30)
        if r.status_code != 200:
            return "Unable to fetch media", 502

        content_type = "image/jpeg" if row["media_type"] == "photo" else "video/mp4"
        return Response(r.content, content_type=content_type)
    except requests.RequestException:
        return "Unable to fetch media", 502

def run_web():
    # Local development only. Production should use gunicorn.
    app_web.run(host="0.0.0.0", port=8080)

def main():
    init_db()
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.StatusUpdate.CHANNEL_POST, channel_post)
    )
    application.add_handler(
        MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data)
    )

    # Flask and bot polling in the same process.
    import threading
    threading.Thread(target=run_web, daemon=True).start()

    print("Bot started. Waiting for channel posts...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
