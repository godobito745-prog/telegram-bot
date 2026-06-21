from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from collections import defaultdict
from flask import Flask
import threading
import time

# =====================
# BOT TOKEN
# =====================
TOKEN = "8969661165:AAHS20hgTSo9FperGJPybYBzovxkKoaJNX8"

# =====================
# OWNER
# =====================
OWNER_ID = 8887583330
ADMINS = set([OWNER_ID])

# =====================
# DATABASE
# =====================
banned = set()
muted = set()
warnings = defaultdict(int)

settings = {
    "chat_locked": False,
    "antilink": True,
    "antispam": True
}

spam_tracker = defaultdict(list)

# =====================
# FLASK (24/7 KEEP ALIVE)
# =====================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running"

def run():
    app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run).start()

# =====================
# HELPERS
# =====================
def is_admin(user_id):
    return user_id in ADMINS or user_id == OWNER_ID

def get_target(update, context):
    if update.message.reply_to_message:
        return update.message.reply_to_message.from_user.id

    if context.args:
        try:
            return int(context.args[0])
        except:
            return None
    return None

# =====================
# COMMANDS
# =====================
def manage(update, context):
    user_id = update.effective_user.id
    text = update.message.text.lower()

    if not is_admin(user_id):
        return

    target = get_target(update, context)

    if text.startswith("/ban") and target:
        banned.add(target)
        update.message.reply_text("🚫 User banned")

    elif text.startswith("/unban") and target:
        banned.discard(target)
        update.message.reply_text("✅ User unbanned")

    elif text.startswith("/mute") and target:
        muted.add(target)
        update.message.reply_text("🔇 User muted")

    elif text.startswith("/unmute") and target:
        muted.discard(target)
        update.message.reply_text("🔊 User unmuted")

    elif text.startswith("/warn") and target:
        warnings[target] += 1
        if warnings[target] >= 3:
            banned.add(target)
            update.message.reply_text("🚫 Banned after 3 warnings")
        else:
            update.message.reply_text(f"⚠️ Warning {warnings[target]}/3")

    elif text.startswith("/lockall"):
        settings["chat_locked"] = True
        update.message.reply_text("🔒 Chat locked")

    elif text.startswith("/unlockall"):
        settings["chat_locked"] = False
        update.message.reply_text("🔓 Chat unlocked")

    elif text.startswith("/id"):
        if target:
            update.message.reply_text(f"🆔 ID: {target}")
        else:
            update.message.reply_text(f"🆔 Your ID: {user_id}")

# =====================
# MESSAGE FILTER
# =====================
def filter_messages(update, context):
    user = update.effective_user.id
    text = update.message.text or ""

    if user in banned:
        update.message.delete()
        return

    if user in muted:
        update.message.delete()
        return

    if settings["chat_locked"] and not is_admin(user):
        update.message.delete()
        return

    if settings["antilink"]:
        if "http" in text or "t.me/" in text:
            update.message.delete()
            return

    if settings["antispam"]:
        now = time.time()
        spam_tracker[user].append(now)
        spam_tracker[user] = [t for t in spam_tracker[user] if now - t < 4]

        if len(spam_tracker[user]) > 5:
            update.message.delete()

# =====================
# WELCOME / LEAVE
# =====================
def welcome(update, context):
    for u in update.message.new_chat_members:
        update.message.reply_text(f"👋 Welcome {u.first_name}")

def leave(update, context):
    user = update.message.left_chat_member
    update.message.reply_text(f"👋 Bye {user.first_name}")

# =====================
# MAIN FUNCTION
# =====================
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("ban", manage))
    dp.add_handler(CommandHandler("unban", manage))
    dp.add_handler(CommandHandler("mute", manage))
    dp.add_handler(CommandHandler("unmute", manage))
    dp.add_handler(CommandHandler("warn", manage))
    dp.add_handler(CommandHandler("lockall", manage))
    dp.add_handler(CommandHandler("unlockall", manage))
    dp.add_handler(CommandHandler("id", manage))

    dp.add_handler(MessageHandler(Filters.text, filter_messages))
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, welcome))
    dp.add_handler(MessageHandler(Filters.status_update.left_chat_member, leave))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
