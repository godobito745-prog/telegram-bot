import time
from collections import defaultdict

from pymongo import MongoClient

from telegram import Update, ChatPermissions
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# =====================
# CONFIG
# =====================
TOKEN = "8969661165:AAEcO_i4VIVE681592N-pKtixfAYZczwvBw"
MONGO_URL = "mongodb+srv://Godobito745_db_user:obito1877@telegram-bot.mfoibwj.mongodb.net/?appName=Telegram-bot"
OWNER_ID = 8887583330

# =====================
# MONGO
# =====================
client = MongoClient(MONGO_URL)
db = client["telegram_bot"]

warn_db = db["warns"]
admin_db = db["admins"]

# =====================
# MEMORY
# =====================
banned = set()
muted = set()
spam_tracker = defaultdict(list)

chat_locked = False
lock_pics = False
lock_stickers = False

# =====================
# HELPERS
# =====================
async def is_admin(update: Update):
    user_id = update.effective_user.id

    if user_id == OWNER_ID:
        return True

    member = await update.effective_chat.get_member(user_id)
    return member.status in ["administrator", "creator"]

# =====================
# BASIC COMMANDS
# =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot is online!")

async def id_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🆔 Your ID: {update.effective_user.id}")

# =====================
# BAN / UNBAN
# =====================
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        await update.message.reply_text("⚠️ Admin only")
        return

    user = update.message.reply_to_message.from_user.id
    banned.add(user)
    await update.message.reply_text("🚫 User banned")

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        return

    user = update.message.reply_to_message.from_user.id
    banned.discard(user)
    await update.message.reply_text("✅ User unbanned")

# =====================
# MUTE
# =====================
async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        return

    user = update.message.reply_to_message.from_user.id
    muted.add(user)
    await update.message.reply_text("🔇 User muted")

async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        return

    user = update.message.reply_to_message.from_user.id
    muted.discard(user)
    await update.message.reply_text("🔊 User unmuted")

# =====================
# WARN SYSTEM
# =====================
async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        return

    user = update.message.reply_to_message.from_user.id

    data = warn_db.find_one({"_id": user})
    count = data["count"] if data else 0
    count += 1

    warn_db.update_one({"_id": user}, {"$set": {"count": count}}, upsert=True)

    if count >= 3:
        banned.add(user)
        await update.message.reply_text("🚫 Banned after 3 warns")
    else:
        await update.message.reply_text(f"⚠️ Warning {count}/3")

# =====================
# LOCK SYSTEM
# =====================
async def lockall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global chat_locked
    if not await is_admin(update):
        return

    chat_locked = True
    await update.message.reply_text("🔒 Chat locked")

async def unlockall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global chat_locked
    if not await is_admin(update):
        return

    chat_locked = False
    await update.message.reply_text("🔓 Chat unlocked")

async def lockpics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global lock_pics
    if not await is_admin(update):
        return

    lock_pics = True
    await update.message.reply_text("🖼 Photos locked")

async def locksticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global lock_stickers
    if not await is_admin(update):
        return

    lock_stickers = True
    await update.message.reply_text("🎭 Stickers locked")

# =====================
# MESSAGE FILTER
# =====================
async def filter_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    user = update.effective_user.id
    text = update.message.text or ""

    if user in banned:
        await update.message.delete()
        return

    if user in muted:
        await update.message.delete()
        return

    if chat_locked:
        member = await update.effective_chat.get_member(user)
        if member.status not in ["administrator", "creator"]:
            await update.message.delete()
            return

    if "http" in text or "t.me/" in text:
        if not await is_admin(update):
            await update.message.delete()
            return

    now = time.time()
    spam_tracker[user].append(now)
    spam_tracker[user] = [t for t in spam_tracker[user] if now - t < 4]

    if len(spam_tracker[user]) > 5:
        await update.message.delete()

    if update.message.photo and lock_pics:
        if not await is_admin(update):
            await update.message.delete()

    if update.message.sticker and lock_stickers:
        if not await is_admin(update):
            await update.message.delete()

# =====================
# MAIN
# =====================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", id_cmd))

    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("unban", unban))
    app.add_handler(CommandHandler("mute", mute))
    app.add_handler(CommandHandler("unmute", unmute))
    app.add_handler(CommandHandler("warn", warn))

    app.add_handler(CommandHandler("lockall", lockall))
    app.add_handler(CommandHandler("unlockall", unlockall))
    app.add_handler(CommandHandler("lockpics", lockpics))
    app.add_handler(CommandHandler("locksticker", locksticker))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, filter_messages))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
