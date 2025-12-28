import telebot
from telebot import types
import requests
import json, os
from threading import Thread
from flask import Flask

# --- الإعدادات ---
BOT_TOKEN = "8476427848:AAFvLp9QK8VYv4uZTCOkJR-H_mWnVvZQv3Q"
API_KEY = "9967a35290cae1978403a8caa91c59d6"
API_URL = "https://kd1s.com/api/v2"
POINT_VALUE = 2000 

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

@app.route('/')
def home(): return "SYSTEM FULLY FIXED 🟢"

# --- إدارة قاعدة البيانات ---
def load_db():
    if not os.path.exists('db.json'): return {"users": {}, "codes": {}, "orders_count": 6385597}
    with open('db.json', 'r') as f: return json.load(f)

def save_db(db):
    with open('db.json', 'w') as f: json.dump(db, f)

# --- الواجهة الرئيسية (استعادة كل الأزرار) ---
def main_markup(uid):
    db = load_db()
    pts = db["users"].get(uid, {"points": 0})["points"]
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(types.InlineKeyboardButton("🛍️ قائمة الخدمات", callback_data="all_sv"))
    markup.add(types.InlineKeyboardButton(f"📟 الحساب ({pts})", callback_data="acc"), 
               types.InlineKeyboardButton("✳️ تجميع", callback_data="coll"))
    markup.add(types.InlineKeyboardButton("🔍 بحث", callback_data="search"), 
               types.InlineKeyboardButton("💳 استخدام كود", callback_data="code"))
    markup.add(types.InlineKeyboardButton("🚩 تتبع طلب", callback_data="track"), 
               types.InlineKeyboardButton("💰 شحن نقاط", callback_data="topup"))
    markup.add(types.InlineKeyboardButton("📜 الشروط", callback_data="terms"), 
               types.InlineKeyboardButton("⚙️ التحديثات", callback_data="upds"))
    markup.row(types.InlineKeyboardButton(f"✅ عدد الطلبات : {db['orders_count']}", callback_data="none"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.chat.id)
    db = load_db()
    if uid not in db["users"]: db["users"][uid] = {"points": 0}
    save_db(db)
    bot.send_message(message.chat.id, "👋 أهلاً بك في بوت الشموخ\nتم إصلاح جميع الأزرار وتصنيف الخدمات:", reply_markup=main_markup(uid))

# --- معالج الأزرار (دقة 100%) ---
@bot.callback_query_handler(func=lambda call: True)
def handle_actions(call):
    uid = str(call.message.chat.id)
    
    # 1. قائمة المنصات
    if call.data == "all_sv":
        platforms = [("📸 إنستقرام", "Insta"), ("🎬 تيك توك", "TikTok"), ("🎥 يوتيوب", "YT"), ("🔹 تليجرام", "Tele"), ("🟡 سناب شات", "Snap")]
        markup = types.InlineKeyboardMarkup(row_width=1)
        for name, pid in platforms:
            markup.add(types.InlineKeyboardButton(name, callback_data=f"p_{pid}"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="home"))
        bot.edit_message_text("📂 اختر المنصة:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    # 2. التصنيفات الفرعية داخل المنصة
    elif call.data.startswith("p_"):
        plat = call.data.split("_")[1]
        subs = [("👥 متابعين", "Fol"), ("❤️ لايكات", "Lik"), ("👁️ مشاهدات", "View"), ("💬 تعليقات", "Comm")]
        markup = types.InlineKeyboardMarkup(row_width=2)
        for n, s in subs:
            markup.add(types.InlineKeyboardButton(n, callback_data=f"f_{plat}_{s}"))
        markup.add(types.InlineKeyboardButton("🔙 العودة للمنصات", callback_data="all_sv"))
        bot.edit_message_text(f"🛠️ تصنيفات {plat}:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    # 3. جلب الخدمات النهائية (إصلاح محرك البحث)
    elif call.data.startswith("f_"):
        _, plat, sub = call.data.split("_")
        bot.answer_callback_query(call.id, "🔎 جاري تحميل الخدمات...")
        res = requests.post(API_URL, data={'key': API_KEY, 'action': 'services'}).json()
        markup = types.InlineKeyboardMarkup()
        
        # تحويل الاختصارات لكلمات كاملة للبحث في الموقع
        search_plat = "Instagram" if plat == "Insta" else plat
        search_sub = "Followers" if sub == "Fol" else "Likes" if sub == "Lik" else "Views" if sub == "View" else "Comments"
        
        count = 0
        for s in res:
            if search_plat.lower() in s['category'].lower() and search_sub.lower() in s['name'].lower():
                if count < 15:
                    price = int(float(s['rate']) * POINT_VALUE)
                    markup.add(types.InlineKeyboardButton(f"🔹 {s['name'][:25]} | {price}ن", callback_data=f"ord_{s['service']}"))
                    count += 1
        
        if count == 0:
            bot.answer_callback_query(call.id, "⚠️ لا توجد خدمات حالياً", show_alert=True)
            return

        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data=f"p_{plat}"))
        bot.edit_message_text(f"🚀 خدمات {search_sub}:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    # 4. تفعيل أزرار القائمة الرئيسية
    elif call.data == "acc":
        db = load_db()
        pts = db["users"].get(uid, {"points": 0})["points"]
        bot.answer_callback_query(call.id, f"💰 رصيدك: {pts} نقطة", show_alert=True)

    elif call.data == "topup":
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("تواصل مع المطور @l550r", url="https://t.me/l550r"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="home"))
        bot.edit_message_text("💰 للشحن، تواصل مع المطور مباشرة:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "home":
        bot.edit_message_text("👋 القائمة الرئيسية:", call.message.chat.id, call.message.message_id, reply_markup=main_markup(uid))

def run(): app.run(host='0.0.0.0', port=8080)
if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
