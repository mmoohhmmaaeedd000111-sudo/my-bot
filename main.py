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
POINT_VALUE = 2000 

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

@app.route('/')
def home(): return "PRIORITY SYSTEM ACTIVE 🟢"

# --- قاموس الأولوية والتعريب (الترتيب يتبع ترتيبك المذكور) ---
PRIORITY_TRANSLATION = {
    "Instagram": "📸 خدمات إنستقرام",
    "TikTok": "🎬 خدمات تيك توك",
    "WhatsApp": "💬 خدمات واتساب",
    "YouTube": "🎥 خدمات يوتيوب",
    "Snapchat": "🟡 خدمات سناب شات",
    "PUBG": "🎮 شحن بوبجي (PUBG)",
    "Ludo": "🎲 خدمات لودو (Ludo)",
    "Telegram": "🔹 خدمات تليجرام",
    "Facebook": "👤 خدمات فيسبوك"
}

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
               types.InlineKeyboardButton("💳 استخدام كود", callback_data="use_code"))
    markup.add(types.InlineKeyboardButton("🚩 تتبع طلب", callback_data="info"), 
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
    with open('db.json', 'w') as f: json.dump(db, f)
    bot.send_message(message.chat.id, f"👋 أهلاً بك في بوت الشموخ\n👤 نقاطك: {db['users'][uid]['points']}", reply_markup=get_main_markup(uid))

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    uid = str(call.message.chat.id)
    
    if call.data == "services":
        try:
            res = requests.post(API_URL, data={'key': API_KEY, 'action': 'services'}).json()
            all_cats = list(set([s['category'] for s in res]))
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            added_cats = []

            # أولاً: إضافة المنصات ذات الأولوية بالترتيب المطلوب
            for eng_key, arb_name in PRIORITY_TRANSLATION.items():
                for real_cat in all_cats:
                    if eng_key.lower() in real_cat.lower() and real_cat not in added_cats:
                        markup.add(types.InlineKeyboardButton(arb_name, callback_data=f"cat_{real_cat[:20]}"))
                        added_cats.append(real_cat)
            
            # ثانياً: إضافة باقي الأقسام (المنصات الأخرى) تحتها
            for cat in sorted(all_cats):
                if cat not in added_cats:
                    markup.add(types.InlineKeyboardButton(f"📦 {cat}", callback_data=f"cat_{cat[:20]}"))
            
            markup.add(types.InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back"))
            bot.edit_message_text("📂 اختر المنصة (المنصات الرئيسية في الأعلى):", call.message.chat.id, call.message.message_id, reply_markup=markup)
        except:
            bot.answer_callback_query(call.id, "❌ خطأ في الاتصال بموقع kd1s")

    elif call.data.startswith("cat_"):
        cat_name = call.data.replace("cat_", "")
        res = requests.post(API_URL, data={'key': API_KEY, 'action': 'services'}).json()
        markup = types.InlineKeyboardMarkup()
        for s in [x for x in res if x['category'].startswith(cat_name)][:15]:
            price = int(float(s['rate']) * POINT_VALUE)
            # تعريب كلمات الخدمات
            s_name = s['name'].replace("Followers", "متابعين").replace("Likes", "لايكات").replace("Views", "مشاهدات")
            markup.add(types.InlineKeyboardButton(f"🔹 {s_name} | {price}ن", callback_data=f"ord_{s['service']}"))
        markup.add(types.InlineKeyboardButton("🔙 العودة للأقسام", callback_data="services"))
        bot.edit_message_text(f"🚀 الخدمات المتوفرة لهذا القسم:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "back":
        bot.edit_message_text("👋 قائمة التحكم الرئيسية:", call.message.chat.id, call.message.message_id, reply_markup=get_main_markup(uid))

    elif call.data == "topup":
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("👨‍💻 تواصل مع المطور @l550r", url="https://t.me/l550r"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back"))
        bot.edit_message_text("💰 لشحن رصيدك، تواصل مع المطور مباشرة عبر المعرف أدناه:", call.message.chat.id, call.message.message_id, reply_markup=markup)

def run(): app.run(host='0.0.0.0', port=8080)
if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
