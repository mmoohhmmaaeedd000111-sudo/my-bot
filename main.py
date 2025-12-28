import telebot
from telebot import types
import requests
import json, os
from threading import Thread
from flask import Flask

# --- الإعدادات الثابتة ---
BOT_TOKEN = "8476427848:AAFvLp9QK8VYv4uZTCOkJR-H_mWnVvZQv3Q"
ADMIN_ID = "8463703998" 
API_KEY = "9967a35290cae1978403a8caa91c59d6"
API_URL = "https://kd1s.com/api/v2"
POINT_VALUE = 2000 

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

@app.route('/')
def home(): return "SYSTEM FULLY FIXED 🟢"

# --- إدارة قاعدة البيانات ---
def load_db():
    if not os.path.exists('db.json'): 
        return {"users": {}, "codes": {}, "orders_count": 6385597}
    with open('db.json', 'r') as f: return json.load(f)

def save_db(db):
    with open('db.json', 'w') as f: json.dump(db, f)

# --- واجهة الأزرار الكاملة (إعادة بناء دقيقة) ---
def get_full_markup(uid):
    db = load_db()
    pts = db["users"].get(uid, {"points": 0})["points"]
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(types.InlineKeyboardButton("🛍️ قائمة الخدمات", callback_data="all_services"))
    markup.add(types.InlineKeyboardButton(f"📟 الحساب ({pts})", callback_data="my_acc"), 
               types.InlineKeyboardButton("✳️ تجميع", callback_data="collect_pts"))
    markup.add(types.InlineKeyboardButton("🔍 بحث", callback_data="search_svc"), 
               types.InlineKeyboardButton("💳 استخدام كود", callback_data="enter_code"))
    markup.add(types.InlineKeyboardButton("🚩 تتبع طلب", callback_data="track_order"), 
               types.InlineKeyboardButton("💰 شحن نقاط", callback_data="charge_pts"))
    markup.add(types.InlineKeyboardButton("📜 الشروط", callback_data="terms_info"), 
               types.InlineKeyboardButton("⚙️ التحديثات", callback_data="updates_info"))
    markup.row(types.InlineKeyboardButton(f"✅ عدد الطلبات : {db['orders_count']}", callback_data="none"))
    return markup

@bot.message_handler(commands=['start'])
def start_cmd(message):
    uid = str(message.chat.id)
    db = load_db()
    if uid not in db["users"]: db["users"][uid] = {"points": 0}
    save_db(db)
    bot.send_message(message.chat.id, "👋 أهلاً بك في بوت الشموخ\nيرجى اختيار أحد الخيارات:", reply_markup=get_full_markup(uid))

# --- معالج الأوامر الموحد ---
@bot.callback_query_handler(func=lambda call: True)
def handle_all_actions(call):
    uid = str(call.message.chat.id)
    
    # 1. عرض الأقسام المرتبة
    if call.data == "all_services":
        cats = [
            ("📸 إنستقرام", "Instagram"), ("🎬 تيك توك", "TikTok"), 
            ("💬 واتساب", "WhatsApp"), ("🎥 يوتيوب", "YouTube"),
            ("🟡 سناب شات", "Snapchat"), ("🎮 بوبجي", "PUBG"),
            ("🎲 لودو", "Ludo"), ("🔹 تليجرام", "Telegram")
        ]
        markup = types.InlineKeyboardMarkup(row_width=1)
        for c_text, c_id in cats:
            markup.add(types.InlineKeyboardButton(c_text, callback_data=f"get_{c_id}"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="main_home"))
        bot.edit_message_text("📂 اختر القسم المطلوب:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    # 2. جلب الخدمات (إصلاح البحث الدقيق)
    elif call.data.startswith("get_"):
        key = call.data.split("_")[1]
        bot.answer_callback_query(call.id, "🔎 جاري فحص الخدمات في kd1s...")
        res = requests.post(API_URL, data={'key': API_KEY, 'action': 'services'}).json()
        markup = types.InlineKeyboardMarkup()
        
        found_count = 0
        for s in res:
            # تدقيق البحث في القسم والاسم معاً لضمان الظهور
            if key.lower() in s['category'].lower() or key.lower() in s['name'].lower():
                if found_count < 20:
                    price = int(float(s['rate']) * POINT_VALUE)
                    name = s['name'].replace("Followers", "متابعين").replace("Likes", "لايكات")
                    markup.add(types.InlineKeyboardButton(f"🔹 {name[:25]} | {price}ن", callback_data=f"buy_{s['service']}"))
                    found_count += 1
        
        if found_count == 0:
            bot.answer_callback_query(call.id, "❌ لا توجد خدمات حالية لهذا القسم", show_alert=True)
            return

        markup.add(types.InlineKeyboardButton("🔙 عودة للأقسام", callback_data="all_services"))
        bot.edit_message_text(f"🚀 خدمات {key}:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    # 3. العودة للقائمة الرئيسية
    elif call.data == "main_home":
        bot.edit_message_text("👋 القائمة الرئيسية:", call.message.chat.id, call.message.message_id, reply_markup=get_full_markup(uid))

    # 4. زر الشحن المباشر
    elif call.data == "charge_pts":
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("تواصل مع المطور @l550r", url="https://t.me/l550r"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="main_home"))
        bot.edit_message_text("💰 لشحن نقاطك، تواصل مع المطور وارسل صورة التحويل:", call.message.chat.id, call.message.message_id, reply_markup=markup)

def run(): app.run(host='0.0.0.0', port=8080)
if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
