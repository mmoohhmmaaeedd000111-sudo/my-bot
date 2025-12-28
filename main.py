import telebot
from telebot import types
import requests
import json, os
from threading import Thread
from flask import Flask

# --- الإعدادات ---
BOT_TOKEN = "8476427848:AAFvLp9QK8VYv4uZTCOkJR-H_mWnVvZQv3Q"
ADMIN_ID = "8463703998" 
API_KEY = "9967a35290cae1978403a8caa91c59d6"
API_URL = "https://kd1s.com/api/v2"
POINT_VALUE = 2000 # كل 1 دولار = 2000 نقطة

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

@app.route('/')
def home(): return "FINAL STABLE VERSION ACTIVE 🟢"

# --- قائمة الأقسام المثبتة (هنا يكمن الحل) ---
# ملاحظة: الأسماء بالإنجليزية يجب أن تطابق كلمات من أقسام موقع kd1s
CATEGORIES = [
    {"show": "📸 خدمات إنستقرام", "search": "Instagram"},
    {"show": "🎬 خدمات تيك توك", "search": "TikTok"},
    {"show": "💬 خدمات واتساب", "search": "WhatsApp"},
    {"show": "🎥 خدمات يوتيوب", "search": "YouTube"},
    {"show": "🟡 خدمات سناب شات", "search": "Snapchat"},
    {"show": "🎮 شحن بوبجي (PUBG)", "search": "PUBG"},
    {"show": "🎲 خدمات لودو (Ludo)", "search": "Ludo"},
    {"show": "🔹 خدمات تليجرام", "search": "Telegram"},
    {"show": "👤 خدمات فيسبوك", "search": "Facebook"}
]

def load_db():
    if not os.path.exists('db.json'): return {"users": {}, "orders_count": 6385597}
    with open('db.json', 'r') as f: return json.load(f)

def get_main_markup(uid):
    db = load_db()
    pts = db["users"].get(uid, {"points": 0}).get("points", 0)
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(types.InlineKeyboardButton("🛍️ قائمة الخدمات", callback_data="services"))
    markup.add(types.InlineKeyboardButton(f"📟 الحساب ({pts})", callback_data="acc"), 
               types.InlineKeyboardButton("✳️ تجميع", callback_data="collect"))
    markup.add(types.InlineKeyboardButton("🔍 بحث", callback_data="search_start"), 
               types.InlineKeyboardButton("💳 كود", callback_data="use_code"))
    markup.add(types.InlineKeyboardButton("🚩 تتبع طلب", callback_data="info"), 
               types.InlineKeyboardButton("💰 شحن نقاط", callback_data="topup"))
    markup.add(types.InlineKeyboardButton("📜 الشروط", callback_data="terms"), 
               types.InlineKeyboardButton("⚙️ التحديثات", callback_data="updates"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.chat.id)
    db = load_db()
    if uid not in db["users"]: db["users"][uid] = {"points": 0}
    with open('db.json', 'w') as f: json.dump(db, f)
    bot.send_message(message.chat.id, "👋 أهلاً بك في بوت الشموخ للرشق", reply_markup=get_main_markup(uid))

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == "services":
        # هنا نعرض الأقسام التي ثبتناها يدوياً فوراً دون انتظار الموقع
        markup = types.InlineKeyboardMarkup(row_width=1)
        for cat in CATEGORIES:
            markup.add(types.InlineKeyboardButton(cat["show"], callback_data=f"showcat_{cat['search']}"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back"))
        bot.edit_message_text("📂 اختر المنصة المطلوبة:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith("showcat_"):
        search_key = call.data.replace("showcat_", "")
        bot.answer_callback_query(call.id, "🔎 جاري جلب الخدمات...")
        
        # جلب الخدمات التي تحتوي على الكلمة المطلوبة فقط
        res = requests.post(API_URL, data={'key': API_KEY, 'action': 'services'}).json()
        markup = types.InlineKeyboardMarkup()
        
        count = 0
        for s in res:
            if search_key.lower() in s['category'].lower() and count < 20:
                price = int(float(s['rate']) * POINT_VALUE)
                name = s['name'].replace("Followers", "متابعين").replace("Likes", "لايكات")
                markup.add(types.InlineKeyboardButton(f"🔹 {name} | {price}ن", callback_data=f"ord_{s['service']}"))
                count += 1
        
        markup.add(types.InlineKeyboardButton("🔙 العودة للأقسام", callback_data="services"))
        bot.edit_message_text(f"🚀 خدمات {search_key}:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "back":
        bot.edit_message_text("👋 القائمة الرئيسية:", call.message.chat.id, call.message.message_id, reply_markup=get_main_markup(str(call.message.chat.id)))

    elif call.data == "topup":
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("👨‍💻 تواصل مع المطور @l550r", url="https://t.me/l550r"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back"))
        bot.edit_message_text("💰 لشحن الرصيد تواصل معي مباشرة:", call.message.chat.id, call.message.message_id, reply_markup=markup)

def run(): app.run(host='0.0.0.0', port=8080)
if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
