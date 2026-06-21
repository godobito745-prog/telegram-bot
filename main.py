import os
import time
import threading
from collections import defaultdict
from flask import Flask

from telegram import ChatPermissions

from pymongo import MongoClient

from telegram import Update
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
TOKEN = "8969661165:AAE4nbghCtDz4UUk7Fe7io6cV3y6rvdN9fY"

MONGO_URL = "mongodb+srv://Godobito745_db_user:obito1877@telegram-bot.mfoibwj.mongodb.net/?appName=Telegram-bot"

OWNER_ID = 8887583330

# =====================
# FLASK FOR RENDER
# =====================
web = Flask(__name__)

@web.route("/")
def home():
    return "Bot is online!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web).start()

# =====================
# DATABASE
# =====================
client = MongoClient(MONGO_URL)
db = client["telegram_bot"]

warn_db = db["warns"]

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
# ADMIN CHECK
# =====================
async def is_admin(update):
    user_id = update.effective_user.id

    if user_id == OWNER_ID:
        return True

    member = await update.effective_chat.get_member(user_id)
    return member.status in ["administrator", "creator"]

# =====================
# START
# =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot Online!"
    )

# =====================
# ID
# =====================
async def id_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🆔 Your ID: {update.effective_user.id}"
    )

# =====================
# BAN
# =====================
from telegram import ChatPermissions

async def ban(update, context):
    try:
        if not await is_admin(update):
            await update.message.reply_text("⚠️ You need admin to do this.")
            return

        if not update.message.reply_to_message:
            await update.message.reply_text("❌ Reply to a user to ban them.")
            return

        user_id = update.message.reply_to_message.from_user.id
        chat_id = update.effective_chat.id

        await context.bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            permissions=ChatPermissions(
                can_send_messages=False,
                can_send_media_messages=False,
                can_send_polls=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False,
            )
        )

        await update.message.reply_text(
            f"😞 Another user has gone!\nUser ID: {user_id}"
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Ban failed: {e}")

# =====================
# UNBAN
# =====================
async def unban(update, context):
    try:
        if not await is_admin(update):
            await update.message.reply_text("⚠️ You need admin to do this.")
            return

        if not update.message.reply_to_message:
            await update.message.reply_text("❌ Reply to a user to unban them.")
            return

        user_id = update.message.reply_to_message.from_user.id
        chat_id = update.effective_chat.id

        await context.bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
            )
        )

        await update.message.reply_text(
            f"✅ Hey hey welcome again dude!\nUser ID: {user_id}"
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Unban failed: {e}")
# =====================
# MUTE
# =====================
from telegram import ChatPermissions

async def mute(update, context):
    if not await is_admin(update):
        await update.message.reply_text("⚠️ You need admin to do this.")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a user to mute them.")
        return

    user_id = update.message.reply_to_message.from_user.id
    chat_id = update.effective_chat.id

    muted.add(user_id)

    await context.bot.restrict_chat_member(
        chat_id=chat_id,
        user_id=user_id,
        permissions=ChatPermissions(
            can_send_messages=False
        )
    )

    await update.message.reply_text("shhhh.....There is no need to speak now.")

# =====================
# UNMUTE
# =====================
async def unmute(update, context):
    if not await is_admin(update):
        await update.message.reply_text("⚠️ You need admin to do this.")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a user to unmute them.")
        return

    user_id = update.message.reply_to_message.from_user.id
    chat_id = update.effective_chat.id

    muted.discard(user_id)

    await context.bot.restrict_chat_member(
        chat_id=chat_id,
        user_id=user_id,
        permissions=ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_polls=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True
        )
    )

    await update.message.reply_text("wow.....now you can speak 🗣️.")

# ======================
# PORMOTE 
# ======================
async def promote(update, context):
    if not await is_admin(update):
        await update.message.reply_text("⚠️ You need admin to do this.")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a user to promote them.")
        return

    user_id = update.message.reply_to_message.from_user.id
    chat_id = update.effective_chat.id

    await context.bot.promote_chat_member(
        chat_id=chat_id,
        user_id=user_id,
        can_change_info=True,
        can_delete_messages=True,
        can_invite_users=True,
        can_restrict_members=True,
        can_pin_messages=True,
        can_promote_members=False
    )

    await update.message.reply_text("👑 User promoted to admin.")

# =====================
# DEMOTE
# =====================
async def demote(update, context):
    if not await is_admin(update):
        await update.message.reply_text("⚠️ You need admin to do this.")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a user to demote them.")
        return

    user_id = update.message.reply_to_message.from_user.id
    chat_id = update.effective_chat.id

    await context.bot.promote_chat_member(
        chat_id=chat_id,
        user_id=user_id,
        can_change_info=False,
        can_delete_messages=False,
        can_invite_users=False,
        can_restrict_members=False,
        can_pin_messages=False,
        can_promote_members=False
    )

    await update.message.reply_text("👇 User demoted (admin removed).")

# =====================
# WARN
# =====================
async def warn(update, context):
    if not await is_admin(update):
        await update.message.reply_text(
            "⚠️ You need admin to use this command."
        )
        return

    if not update.message.reply_to_message:
        return

    user = update.message.reply_to_message.from_user.id

    data = warn_db.find_one({"_id": user})
    count = data["count"] if data else 0

    count += 1

    warn_db.update_one(
        {"_id": user},
        {"$set": {"count": count}},
        upsert=True
    )

    if count >= 3:
        banned.add(user)
        await update.message.reply_text(
            "🚫 User banned after 3 warnings."
        )
    else:
        await update.message.reply_text(
            f"⚠️ Warning {count}/3"
        )

# =====================
# LOCK ALL
# =====================
async def lockall(update, context):
    global chat_locked

    if not await is_admin(update):
        await update.message.reply_text(
            "⚠️ You need admin."
        )
        return

    chat_locked = True

    await update.message.reply_text(
        "🔒 Chat locked."
    )

async def unlockall(update, context):
    global chat_locked

    if not await is_admin(update):
        return

    chat_locked = False

    await update.message.reply_text(
        "🔓 Chat unlocked."
    )

# =====================
# LOCK PICS
# =====================
async def lockpics(update, context):
    global lock_pics

    if not await is_admin(update):
        return

    lock_pics = True

    await update.message.reply_text(
        "🖼 Photos locked."
    )
    
#======================
# UNLOCH PICS
#======================
async def unlockpics(update, context):
    global lock_pics

    if not await is_admin(update):
        return

    lock_pics = False
    await update.message.reply_text("🖼 Photos unlocked.")
    
# =====================
# LOCK STICKERS
# =====================
async def locksticker(update, context):
    global lock_stickers

    if not await is_admin(update):
        return

    lock_stickers = True

    await update.message.reply_text(
        "🎭 Stickers locked."
    )

#======================
# UNLOCK STICKERS 
#=====================
async def unlockstickers(update, context):
    global lock_stickers

    if not await is_admin(update):
        return

    lock_stickers = False
    await update.message.reply_text("🎭 Stickers unlocked.")
 
# =====================
# FILTERS
# =====================
async def filter_messages(update, context):

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

    spam_tracker[user] = [
        t for t in spam_tracker[user]
        if now - t < 4
    ]

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
    app.add_handler(CommandHandler("unlockpics", unlockpics))
    
    app.add_handler(CommandHandler("locksticker", locksticker))
    app.add_handler(CommandHandler("unlockstickers", unlockstickers))
    
    app.add_handler(CommandHandler("mute", mute))
    app.add_handler(CommandHandler("unmute", unmute))

    app.add_handler(CommandHandler("promote", promote))
    app.add_handler(CommandHandler("demote", demote))

    app.add_handler(
        MessageHandler(
            filters.ALL,
            filter_messages
        )
    )

    print("Bot is running...")

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
