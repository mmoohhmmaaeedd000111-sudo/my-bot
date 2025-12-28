import telebot
from telebot import types
import json, os
from threading import Thread
from flask import Flask

# --- إعداداتك ---
BOT_TOKEN = "8476427848:AAFvLp9QK8VYv4uZTCOkJR-H_mWnVvZQv3Q"
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

@app.route('/')
def home(): return "BOT IS ACTIVE 🟢"

# --- قاعدة بيانات المستخدمين ---
def load_db():
    if not os.path.exists('db.json'): return {"users": {}}
    with open('db.json', 'r') as f: return json.load(f)

def save_db(db):
    with open('db.json', 'w') as f: json.dump(db, f)

# --- قائمة الأزرار (نفس التي نجحت في إظهارها) ---
def get_main_markup(uid):
    db = load_db()
    pts = db["users"].get(uid, 0)
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(types.InlineKeyboardButton("🛍️ الخدمات", callback_data="services"))
    markup.add(types.InlineKeyboardButton(f"📟 الحساب ({pts})", callback_data="acc"), types.InlineKeyboardButton("✳️ تجميع", callback_data="coll"))
    markup.add(types.InlineKeyboardButton("♻️ تحويل نقاط", callback_data="trans"), types.InlineKeyboardButton("💳 استخدام كود", callback_data="code"))
    markup.add(types.InlineKeyboardButton("🚩 طلباتي", callback_data="orders"), types.InlineKeyboardButton("📩 معلومات الطلب", callback_data="info"))
    markup.add(types.InlineKeyboardButton("📊 الاحصائيات", callback_data="stats"), types.InlineKeyboardButton("💰 شحن نقاط", callback_data="topup"))
    markup.add(types.InlineKeyboardButton("📜 الشروط", callback_data="terms"), types.InlineKeyboardButton("⚙️ التحديثات", callback_data="updates"))
    markup.row(types.InlineKeyboardButton("✅ عدد الطلبات : 6385597", callback_data="none"))
    return markup

# --- رسالة الترحيب ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.chat.id)
    db = load_db()
    if uid not in db["users"]: db["users"][uid] = 0
    save_db(db)
    
    welcome_msg = (f"👋 مرحباً بك في بوت الشموخ للخدمات\n\n"
                  f"👤 نقاطك : {db['users'][uid]}\n"
                  f"🆔 ايديك : {uid}\n\n"
                  f"🚀 اختر الخدمة المطلوبة من الأزرار أدناه:")
    bot.send_message(message.chat.id, welcome_msg, reply_markup=get_main_markup(uid))

# --- برمجة وظائف الأزرار ---
@bot.callback_query_handler(func=lambda call: True)
def handle_calls(call):
    uid = str(call.message.chat.id)
    db = load_db()

    if call.data == "services":
        # قائمة الخدمات بأسعار واضحة
        serv_text = ("📦 **قائمة الخدمات المتاحة:**\n\n"
                    "🔹 **إنستقرام**\n"
                    "├ 1000 متابع (ثابت) ⬅️ 1000 نقطة\n"
                    "└ 1000 لايك (سريع) ⬅️ 250 نقطة\n\n"
                    "🔹 **تيك توك**\n"
                    "├ 1000 متابع ⬅️ 1500 نقطة\n"
                    "└ 1000 مشاهدة ⬅️ 100 نقطة\n\n"
                    "⚠️ أرسل رقم الخدمة أو الرابط للبدء.")
        bot.edit_message_text(serv_text, call.message.chat.id, call.message.message_id, 
                             reply_markup=types.InlineKeyboardMarkup().row(types.InlineKeyboardButton("🔙 رجوع", callback_data="back")), parse_mode="Markdown")

    elif call.data == "acc":
        bot.answer_callback_query(call.id, f"رصيدك الحالي: {db['users'].get(uid, 0)} نقطة 💰", show_alert=True)

    elif call.data == "topup":
        bot.send_message(call.message.chat.id, "💳 **طرق شحن النقاط:**\n\n- كارت آسيا سيل (فئة 5$ = 5000 نقطة)\n- تحويل رصيد مباشر\n\nارسل الكود أو صورة التحويل للمطور: @YourUsername")

    elif call.data == "back":
        bot.edit_message_text(f"👋 مرحباً بك مجدداً\n👤 نقاطك : {db['users'].get(uid, 0)}", 
                             call.message.chat.id, call.message.message_id, reply_markup=get_main_markup(uid))

# --- تشغيل السيرفر ---
def run(): app.run(host='0.0.0.0', port=8080)
if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
