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
def home(): return "SYSTEM FULLY OPTIMIZED 🟢"

def load_db():
    if not os.path.exists('db.json'): return {"users": {}, "orders_count": 6385597}
    return json.load(open('db.json', 'r'))

# --- واجهة الأزرار الكاملة كما في صورتك ---
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
    json.dump(db, open('db.json', 'w'))
    bot.send_message(message.chat.id, "👋 أهلاً بك في بوت الشموخ\nتم إصلاح جلب الخدمات بدقة عالية:", reply_markup=main_markup(uid))

@bot.callback_query_handler(func=lambda call: True)
def handle_actions(call):
    uid = str(call.message.chat.id)
    
    # 1. قائمة المنصات الرئيسية
    if call.data == "all_sv":
        platforms = [
            ("📸 إنستقرام", "Instagram"), ("🎬 تيك توك", "TikTok"), 
            ("🎥 يوتيوب", "YouTube"), ("🔹 تليجرام", "Telegram"), 
            ("🎮 بوبجي", "PUBG"), ("🎲 لودو", "Ludo"), ("👤 فيسبوك", "Facebook")
        ]
        markup = types.InlineKeyboardMarkup(row_width=1)
        for name, pid in platforms:
            markup.add(types.InlineKeyboardButton(name, callback_data=f"p_{pid}"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="home"))
        bot.edit_message_text("📂 اختر المنصة المطلوبة:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    # 2. عرض الخدمات مباشرة (إلغاء التصنيفات الفرعية المعطلة)
    elif call.data.startswith("p_"):
        plat = call.data.split("_")[1]
        bot.answer_callback_query(call.id, f"🔎 جاري استخراج خدمات {plat}...")
        
        try:
            res = requests.post(API_URL, data={'key': API_KEY, 'action': 'services'}).json()
            markup = types.InlineKeyboardMarkup()
            
            count = 0
            for s in res:
                # البحث الذكي: إذا كان اسم المنصة موجود في القسم أو اسم الخدمة
                if plat.lower() in s['category'].lower() or plat.lower() in s['name'].lower():
                    if count < 15: # عرض أول 15 خدمة لسرعة الاستجابة
                        price = int(float(s['rate']) * POINT_VALUE)
                        # تعريب مختصر لاسم الخدمة
                        s_name = s['name'].replace("Followers", "متابعين").replace("Likes", "لايكات").replace("Views", "مشاهدات")
                        markup.add(types.InlineKeyboardButton(f"🔹 {s_name[:30]} | {price}ن", callback_data=f"ord_{s['service']}"))
                        count += 1
            
            if count == 0:
                bot.answer_callback_query(call.id, "⚠️ لا توجد خدمات متاحة حالياً لهذا القسم", show_alert=True)
                return

            markup.add(types.InlineKeyboardButton("🔙 العودة للأقسام", callback_data="all_sv"))
            bot.edit_message_text(f"🚀 خدمات {plat} المتوفرة:", call.message.chat.id, call.message.message_id, reply_markup=markup)
            
        except:
            bot.answer_callback_query(call.id, "❌ خطأ في الاتصال بالموقع المزود", show_alert=True)

    elif call.data == "home":
        bot.edit_message_text("👋 القائمة الرئيسية:", call.message.chat.id, call.message.message_id, reply_markup=main_markup(uid))

def run(): app.run(host='0.0.0.0', port=8080)
if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
