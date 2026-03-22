import requests
import time
import asyncio
import os
from dotenv import load_dotenv
from pymongo import MongoClient

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler
)

# 🔐 ENV
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
UPI_ID = os.getenv("UPI_ID")

# 🗄️ DB
client = MongoClient(MONGO_URI)
db = client["pincode_bot"]
users_col = db["users"]
history_col = db["history"]

# 💎 Plans
PLANS = {
    "basic": 30,
    "pro": 90,
    "ultra": 180
}

# 🔍 Lookup
class PincodeLookup:
    def __init__(self):
        self.base_url = "https://api.postalpincode.in/pincode/"
        self.session = requests.Session()

    def get_pincode_info(self, pincode):
        try:
            res = self.session.get(f"{self.base_url}{pincode}", timeout=10)
            data = res.json()
            return data[0] if data else None
        except:
            return None

lookup = PincodeLookup()

# 👤 Save user
def save_user(user_id):
    if not users_col.find_one({"user_id": user_id}):
        users_col.insert_one({
            "user_id": user_id,
            "count": 0,
            "date": str(time.strftime("%Y-%m-%d")),
            "premium": False,
            "expiry": 0
        })

# 💎 Premium check
def is_premium(user_id):
    user = users_col.find_one({"user_id": user_id})
    if not user or not user.get("premium"):
        return False

    if time.time() > user.get("expiry", 0):
        users_col.update_one({"user_id": user_id}, {"$set": {"premium": False}})
        return False

    return True

# ⛔ Limit
def can_use(user_id):
    user = users_col.find_one({"user_id": user_id})
    today = str(time.strftime("%Y-%m-%d"))

    if user["date"] != today:
        users_col.update_one({"user_id": user_id}, {"$set": {"count": 0, "date": today}})

    if is_premium(user_id):
        return True

    if user["count"] >= 5:
        return False

    users_col.update_one({"user_id": user_id}, {"$inc": {"count": 1}})
    return True

# 🔄 Extend premium
def extend_premium(user_id, days):
    user = users_col.find_one({"user_id": user_id})
    now = int(time.time())

    if user and user.get("expiry", 0) > now:
        expiry = user["expiry"] + days * 86400
    else:
        expiry = now + days * 86400

    users_col.update_one(
        {"user_id": user_id},
        {"$set": {"premium": True, "expiry": expiry}},
        upsert=True
    )

# 🎯 START (PHOTO + TEXT)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id

    save_user(user_id)

    text = (
        f"👋 Hello {user.first_name},\n\n"
        f"🤖 I am [Number Full Info](http://t.me/phone_number_info_ak_bot)\n"
        f"*Your Professional Restricted Content Saver Bot.*\n\n"
        f"🚀 System Status: 🟢 Online\n"
        f"⚡ Performance: 10x High-Speed Processing\n"
        f"🔐 Security: End-to-End Encrypted\n"
        f"📊 Uptime: 99.9% Guaranteed\n\n"
        f"👇 Select an Option Below to Get Started:"
    )

    keyboard = [
        [InlineKeyboardButton("🔍 Search", callback_data="search")],
        [InlineKeyboardButton("📜 History", callback_data="history")],
        [InlineKeyboardButton("💎 Buy Premium", callback_data="buy")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ]

    await update.message.reply_photo(
        photo="https://i.ibb.co/bjwFrTyy/7168219724-28773.jpg",
        caption=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# 🔘 Buttons
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id

    if q.data == "search":
        await q.message.reply_text("📩 Send pincode")

    elif q.data == "history":
        data = history_col.find({"user_id": uid}).limit(5)
        txt = "📜 History:\n"
        for d in data:
            txt += f"📍 {d['pincode']}\n"
        await q.message.reply_text(txt)

    elif q.data == "help":
        await q.message.reply_text("Send 6-digit pincode")

    elif q.data == "buy":
        keyboard = [
            [InlineKeyboardButton("💎 ₹49 (30d)", callback_data="buy_basic")],
            [InlineKeyboardButton("🚀 ₹99 (90d)", callback_data="buy_pro")],
            [InlineKeyboardButton("🔥 ₹199 (180d)", callback_data="buy_ultra")]
        ]
        await q.message.reply_text("Choose plan:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif q.data.startswith("buy_"):
        plan = q.data.split("_")[1]
        days = PLANS[plan]

        await q.message.reply_text(
            f"💳 {plan.upper()} PLAN\n\n"
            f"⏳ {days} days\n"
            f"💰 Pay: {UPI_ID}\n\n"
            f"Send screenshot to admin"
        )

# 📩 MESSAGE
async def msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    text = update.message.text.strip()

    if not text.isdigit() or len(text) != 6:
        await update.message.reply_text("❌ Invalid pincode")
        return

    if not can_use(uid):
        await update.message.reply_text("🚫 Limit reached. Buy Premium")
        return

    m = await update.message.reply_text("🔍 Fetching...")

    data = lookup.get_pincode_info(text)
    if not data:
        await m.edit_text("❌ Not found")
        return

    history_col.insert_one({"user_id": uid, "pincode": text})

    reply = f"📍 {text}\n\n"
    for o in data.get("PostOffice", [])[:5]:
        reply += f"🏢 {o['Name']}\n📍 {o['District']}, {o['State']}\n\n"

    await m.edit_text(reply)

# 👑 ADMIN
async def add(update, context):
    if update.message.from_user.id != ADMIN_ID:
        return

    plan = context.args[0]
    uid = int(context.args[1])

    extend_premium(uid, PLANS[plan])
    await update.message.reply_text("✅ Premium added")

async def users(update, context):
    if update.message.from_user.id != ADMIN_ID:
        return
    total = users_col.count_documents({})
    await update.message.reply_text(f"👥 Users: {total}")

async def broadcast(update, context):
    if update.message.from_user.id != ADMIN_ID:
        return

    txt = " ".join(context.args)
    for u in users_col.find():
        try:
            await context.bot.send_message(u["user_id"], txt)
        except:
            pass

# ⏰ Expiry checker
async def checker(app):
    while True:
        for u in users_col.find({"premium": True}):
            if time.time() > u.get("expiry", 0):
                users_col.update_one({"user_id": u["user_id"]}, {"$set": {"premium": False}})
        await asyncio.sleep(86400)

async def start_tasks(app):
    asyncio.create_task(checker(app))

# 🚀 MAIN
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("users", users))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, msg))

    app.post_init = start_tasks

    print("🔥 BOT RUNNING...")
    app.run_polling()

if __name__ == "__main__":
    main()
