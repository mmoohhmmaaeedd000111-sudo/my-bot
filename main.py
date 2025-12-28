import telebot
from telebot import types
import requests
import json, os, random, string
from threading import Thread
from flask import Flask

# --- 1. الإعدادات الأساسية ---
BOT_TOKEN = "8476427848:AAFvLp9QK8VYv4uZTCOkJR-H_mWnVvZQv3Q"
ADMIN_ID = "8463703998" 
API_KEY = "9967a35290cae1978403a8caa91c59d6"
API_URL = "https://kd1s.com/api/v2"
POINT_VALUE = 2000 # كل 1 دولار = 2000 نقطة (يمكنك تغييرها لزيادة ربحك)

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

@app.route('/')
def home(): return "SYSTEM FULLY ACTIVE 🟢"

# --- 2. إدارة قاعدة البيانات المحلية ---
def load_db():
    if not os.path.exists('db.json'): 
        return {"users": {}, "codes": {}, "orders_count": 6385597}
    with open('db.json', 'r') as f: return json.load(f)

def save_db(db):
    with open('db.json', 'w') as f: json.dump(db, f)

# --- 3. وظائف الإدارة والجلب ---
def send_admin_log(text):
    try: bot.send_message(ADMIN_ID, f"🔔 **إشعار الإدارة:**\n{text}", parse_mode="Markdown")
    except: pass

def get_kd1s_services():
    try: return requests.post(API_URL, data={'key': API_KEY, 'action': 'services'}).json()
    except: return []

# --- 4. واجهة الأزرار الرئيسية ---
def get_main_markup(uid):
    db = load_db()
    pts = db["users"].get(uid, {"points": 0}).get("points", 0)
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(types.InlineKeyboardButton("🛍️ الأقسام والخدمات", callback_data="services"))
    markup.add(types.InlineKeyboardButton(f"📟 الحساب ({pts})", callback_data="acc"), 
               types.InlineKeyboardButton("✳️ تجميع", callback_data="collect"))
    markup.add(types.InlineKeyboardButton("🔍 بحث", callback_data="search_start"), 
               types.InlineKeyboardButton("💳 كود", callback_data="use_code"))
    markup.add(types.InlineKeyboardButton("🚩 تتبع طلب", callback_data="info"), 
               types.InlineKeyboardButton("💰 شحن", callback_data="topup"))
    markup.add(types.InlineKeyboardButton("📜 الشروط", callback_data="terms"), 
               types.InlineKeyboardButton("⚙️ التحديثات", callback_data="updates"))
    markup.row(types.InlineKeyboardButton(f"✅ عدد الطلبات : {db['orders_count']}", callback_data="none"))
    return markup

# --- 5. معالجة الأوامر الرئيسية ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.chat.id)
    db = load_db()
    if uid not in db["users"]:
        db["users"][uid] = {"points": 0}
        send_admin_log(f"👤 مستخدم جديد انضم: {message.from_user.first_name} (`{uid}`)")
    save_db(db)
    bot.send_message(message.chat.id, f"👋 أهلاً بك في بوت الشموخ\n👤 نقاطك: {db['users'][uid]['points']}", reply_markup=get_main_markup(uid))

@bot.message_handler(commands=['gen']) # للأدمن فقط لإنشاء الأكواد
def gen_code(message):
    if str(message.chat.id) == ADMIN_ID:
        try:
            pts = int(message.text.split()[1])
            code = "SHM-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            db = load_db()
            db["codes"][code] = pts
            save_db(db)
            bot.reply_to(message, f"✅ تم إنشاء كود بقيمة {pts}ن:\n`{code}`", parse_mode="Markdown")
        except: bot.reply_to(message, "استخدم: /gen 1000")

# --- 6. معالجة جميع الأزرار (Callback) ---
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    uid = str(call.message.chat.id)
    db = load_db()

    if call.data == "services":
        services = get_kd1s_services()
        cats = sorted(list(set([s['category'] for s in services])))[:12]
        markup = types.InlineKeyboardMarkup(row_width=1)
        for c in cats: markup.add(types.InlineKeyboardButton(f"📁 {c}", callback_data=f"cat_{c[:20]}"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back"))
        bot.edit_message_text("📂 اختر القسم:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith("cat_"):
        cat_name = call.data.replace("cat_", "")
        services = get_kd1s_services()
        markup = types.InlineKeyboardMarkup()
        for s in [x for x in services if x['category'].startswith(cat_name)][:15]:
            price = int(float(s['rate']) * POINT_VALUE)
            markup.add(types.InlineKeyboardButton(f"{s['name']} | {price}ن", callback_data=f"ord_{s['service']}"))
        markup.add(types.InlineKeyboardButton("🔙 الأقسام", callback_data="services"))
        bot.edit_message_text(f"🚀 خدمات {cat_name}:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "topup":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("👨‍💻 تواصل مع المطور لشحن الرصيد", url="https://t.me/l550r"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back"))
        bot.edit_message_text("💰 لشحن الرصيد تواصل معي عبر الزر أدناه وارسل صورة التحويل.", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "back":
        bot.edit_message_text("👋 القائمة الرئيسية:", call.message.chat.id, call.message.message_id, reply_markup=get_main_markup(uid))

    elif call.data == "acc":
        pts = db["users"].get(uid, {"points": 0})["points"]
        bot.answer_callback_query(call.id, f"رصيدك الحالي: {pts} نقطة 💰", show_alert=True)

# --- 7. تشغيل السيرفر ---
def run(): app.run(host='0.0.0.0', port=8080)
if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
