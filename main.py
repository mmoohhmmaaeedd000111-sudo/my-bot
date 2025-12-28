import telebot
from telebot import types
import json, os, random, string
from threading import Thread
from flask import Flask

# --- الإعدادات ---
BOT_TOKEN = "8476427848:AAFvLp9QK8VYv4uZTCOkJR-H_mWnVvZQv3Q"
ADMIN_ID = "8463703998" 
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

@app.route('/')
def home(): return "SYSTEM ONLINE 🟢"

def load_db():
    if not os.path.exists('db.json'): 
        return {"users": {}, "codes": {}, "orders_count": 6385597}
    with open('db.json', 'r') as f: return json.load(f)

def save_db(db):
    with open('db.json', 'w') as f: json.dump(db, f)

def get_main_markup(uid):
    db = load_db()
    pts = db["users"].get(uid, {"points": 0}).get("points", 0)
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(types.InlineKeyboardButton("🛍️ الخدمات", callback_data="services"))
    markup.add(types.InlineKeyboardButton(f"📟 الحساب ({pts})", callback_data="acc"), 
               types.InlineKeyboardButton("✳️ تجميع", callback_data="collect"))
    markup.add(types.InlineKeyboardButton("♻️ تحويل نقاط", callback_data="trans"), 
               types.InlineKeyboardButton("💳 استخدام كود", callback_data="use_code"))
    markup.add(types.InlineKeyboardButton("🚩 طلباتي", callback_data="my_orders"), 
               types.InlineKeyboardButton("📩 معلومات الطلب", callback_data="info"))
    markup.add(types.InlineKeyboardButton("📊 الاحصائيات", callback_data="stats"), 
               types.InlineKeyboardButton("💰 شحن نقاط", callback_data="topup"))
    markup.add(types.InlineKeyboardButton("📜 الشروط", callback_data="terms"), 
               types.InlineKeyboardButton("⚙️ التحديثات", callback_data="updates"))
    markup.row(types.InlineKeyboardButton(f"✅ عدد الطلبات : {db['orders_count']}", callback_data="none"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.chat.id)
    db = load_db()
    if uid not in db["users"]: db["users"][uid] = {"points": 0}
    save_db(db)
    bot.send_message(message.chat.id, f"👋 مرحباً بك في بوت الشموخ\n👤 نقاطك : {db['users'][uid]['points']}\n🆔 ايديك : {uid}", reply_markup=get_main_markup(uid))

# --- تفعيل جميع الأزرار هنا ---
@bot.callback_query_handler(func=lambda call: True)
def handle_all_buttons(call):
    uid = str(call.message.chat.id)
    db = load_db()

    if call.data == "services":
        txt = "📦 **قائمة الخدمات:**\n\n1️⃣ إنستقرام (1000 متابع) -> 1200ن\n2️⃣ تيك توك (1000 متابع) -> 2000ن\n\nارسل الرابط للطلب."
        bot.edit_message_text(txt, call.message.chat.id, call.message.message_id, reply_markup=types.InlineKeyboardMarkup().row(types.InlineKeyboardButton("🔙 رجوع", callback_data="back")), parse_mode="Markdown")

    elif call.data == "acc":
        pts = db["users"].get(uid, {"points": 0})["points"]
        bot.answer_callback_query(call.id, f"رصيدك الحالي هو: {pts} نقطة 💰", show_alert=True)

    elif call.data == "collect":
        link = f"https://t.me/{bot.get_me().username}?start={uid}"
        bot.send_message(call.message.chat.id, f"✳️ رابط دعوتك:\n{link}\n\nشارك الرابط واحصل على 50 نقطة لكل صديق!")

    elif call.data == "trans":
        bot.send_message(call.message.chat.id, "♻️ لتحويل النقاط، أرسل: (تحويل + الأيدي + العدد)\nمثال: تحويل 123456 100")

    elif call.data == "use_code":
        msg = bot.send_message(call.message.chat.id, "💳 أرسل كود الشحن الآن:")
        bot.register_next_step_handler(msg, process_code)

    elif call.data == "stats":
        u_count = len(db["users"])
        bot.answer_callback_query(call.id, f"📊 عدد مستخدمي البوت: {u_count}\n✅ الطلبات الناجحة: {db['orders_count']}", show_alert=True)

    elif call.data == "info" or call.data == "my_orders":
        bot.send_message(call.message.chat.id, "🚩 لا توجد طلبات سابقة لهذا الحساب حالياً.")

    elif call.data == "terms":
        bot.send_message(call.message.chat.id, "📜 **شروط الاستخدام:**\n1. يمنع رشق الحسابات الإباحية.\n2. لا يمكن إلغاء الطلب بعد البدء.")

    elif call.data == "topup":
        bot.send_message(call.message.chat.id, "💰 للشحن المباشر تواصل مع المطور: @YourUsername")

    elif call.data == "back":
        bot.edit_message_text(f"👋 قائمة التحكم الرئيسية:", call.message.chat.id, call.message.message_id, reply_markup=get_main_markup(uid))

def process_code(message):
    code = message.text.strip()
    db = load_db()
    if code in db.get("codes", {}):
        pts = db["codes"][code]
        db["users"][str(message.chat.id)]["points"] += pts
        del db["codes"][code]
        save_db(db)
        bot.send_message(message.chat.id, f"✅ تم شحن {pts} نقطة بنجاح!")
    else:
        bot.send_message(message.chat.id, "❌ الكود غير صحيح.")

# --- أوامر الأدمن المباشرة ---
@bot.message_handler(commands=['gen'])
def gen(message):
    if str(message.chat.id) == ADMIN_ID:
        pts = int(message.text.split()[1])
        code = "SHM-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        db = load_db()
        db["codes"][code] = pts
        save_db(db)
        bot.send_message(ADMIN_ID, f"✅ كود جديد: `{code}`\nالقيمة: {pts}", parse_mode="Markdown")

def run(): app.run(host='0.0.0.0', port=8080)
if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
