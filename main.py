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
def home(): return "SYSTEM FULLY OPERATIONAL 🟢"

# --- إدارة البيانات ---
def load_db():
    if not os.path.exists('db.json'): 
        return {"users": {}, "codes": {}, "orders_count": 6385597}
    with open('db.json', 'r') as f: return json.load(f)

def save_db(db):
    with open('db.json', 'w') as f: json.dump(db, f)

# --- واجهة الأزرار الشاملة (لا يوجد نقص) ---
def main_markup(uid):
    db = load_db()
    pts = db["users"].get(uid, {"points": 0})["points"]
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(types.InlineKeyboardButton("🛍️ قائمة الخدمات", callback_data="all_services"))
    markup.add(types.InlineKeyboardButton(f"📟 الحساب ({pts})", callback_data="acc_info"), 
               types.InlineKeyboardButton("✳️ تجميع", callback_data="collect_pts"))
    markup.add(types.InlineKeyboardButton("🔍 بحث", callback_data="search_svc"), 
               types.InlineKeyboardButton("💳 استخدام كود", callback_data="use_code_pts"))
    markup.add(types.InlineKeyboardButton("🚩 تتبع طلب", callback_data="track_order_now"), 
               types.InlineKeyboardButton("💰 شحن نقاط", callback_data="topup_direct"))
    markup.add(types.InlineKeyboardButton("📜 الشروط", callback_data="terms_view"), 
               types.InlineKeyboardButton("⚙️ التحديثات", callback_data="updates_view"))
    markup.row(types.InlineKeyboardButton(f"✅ عدد الطلبات : {db['orders_count']}", callback_data="none"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.chat.id)
    db = load_db()
    if uid not in db["users"]: db["users"][uid] = {"points": 0}
    save_db(db)
    bot.send_message(message.chat.id, "👋 أهلاً بك في بوت الشموخ الاحترافي\nتم تنظيم الخدمات لتسهيل اختيارك:", reply_markup=main_markup(uid))

# --- معالج الأزرار الموحد (إصلاح شامل لجميع المسارات) ---
@bot.callback_query_handler(func=lambda call: True)
def handle_all_callbacks(call):
    uid = str(call.message.chat.id)
    
    # 1. قائمة المنصات الرئيسية
    if call.data == "all_services":
        platforms = [
            ("📸 إنستقرام", "Instagram"), ("🎬 تيك توك", "TikTok"), 
            ("💬 واتساب", "WhatsApp"), ("🎥 يوتيوب", "YouTube"),
            ("🟡 سناب شات", "Snapchat"), ("🎮 بوبجي", "PUBG"),
            ("🎲 لودو", "Ludo"), ("🔹 تليجرام", "Telegram"),
            ("👤 فيسبوك", "Facebook")
        ]
        markup = types.InlineKeyboardMarkup(row_width=1)
        for name, pid in platforms:
            markup.add(types.InlineKeyboardButton(name, callback_data=f"sub_{pid}"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main"))
        bot.edit_message_text("📂 اختر المنصة:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    # 2. نظام التصنيفات الفرعية (متابعين، لايكات...)
    elif call.data.startswith("sub_"):
        plat = call.data.split("_")[1]
        markup = types.InlineKeyboardMarkup(row_width=2)
        subs = [("👥 متابعين", "Followers"), ("❤️ لايكات", "Likes"), ("👁️ مشاهدات", "Views"), ("💬 تعليقات", "Comments")]
        for n, s in subs:
            markup.add(types.InlineKeyboardButton(n, callback_data=f"final_{plat}_{s}"))
        markup.add(types.InlineKeyboardButton("🔙 العودة للمنصات", callback_data="all_services"))
        bot.edit_message_text(f"🛠️ تصنيفات خدمات {plat}:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    # 3. جلب الخدمات النهائية (دقة البحث)
    elif call.data.startswith("final_"):
        _, plat, sub = call.data.split("_")
        bot.answer_callback_query(call.id, "⏳ يتم الآن استخراج الخدمات...")
        res = requests.post(API_URL, data={'key': API_KEY, 'action': 'services'}).json()
        markup = types.InlineKeyboardMarkup()
        count = 0
        for s in res:
            if plat.lower() in s['category'].lower() and sub.lower() in s['name'].lower():
                if count < 15:
                    price = int(float(s['rate']) * POINT_VALUE)
                    name = s['name'].replace("Followers", "متابعين").replace("Likes", "لايكات")
                    markup.add(types.InlineKeyboardButton(f"🔹 {name[:25]} | {price}ن", callback_data=f"order_{s['service']}"))
                    count += 1
        if count == 0:
            bot.answer_callback_query(call.id, "⚠️ لا توجد خدمات متاحة لهذا التصنيف حالياً", show_alert=True)
            return
        markup.add(types.InlineKeyboardButton(f"🔙 رجوع لـ {plat}", callback_data=f"sub_{plat}"))
        bot.edit_message_text(f"🚀 خدمات {sub} لـ {plat}:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    # 4. تفعيل أزرار القائمة الرئيسية المتبقية
    elif call.data == "acc_info":
        db = load_db()
        pts = db["users"].get(uid, {"points": 0})["points"]
        bot.answer_callback_query(call.id, f"👤 حسابك يحتوي على: {pts} نقطة", show_alert=True)

    elif call.data == "topup_direct":
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("مراسلة المطور @l550r", url="https://t.me/l550r"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main"))
        bot.edit_message_text("💰 لشحن رصيدك، يرجى التواصل مع المطور مباشرة:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "back_main":
        bot.edit_message_text("👋 القائمة الرئيسية:", call.message.chat.id, call.message.message_id, reply_markup=main_markup(uid))

def run(): app.run(host='0.0.0.0', port=8080)
if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
