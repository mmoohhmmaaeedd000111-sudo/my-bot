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
def home(): return "SUPER FAST SYSTEM ACTIVE 🟢"

# قاموس الترجمة الفورية لتحويل الخدمات للغة العربية
TRANSLATION = {
    "followers": "متابعين",
    "likes": "لايكات",
    "views": "مشاهدات",
    "comments": "تعليقات",
    "subscribers": "مشتركين",
    "real": "حقيقي",
    "guaranteed": "ضمان",
    "high quality": "جودة عالية"
}

def translate_name(name):
    name = name.lower()
    for eng, arb in TRANSLATION.items():
        name = name.replace(eng, arb)
    return name.title()

# --- جلب الخدمات وتخزينها لسرعة الاستجابة ---
SERVICES_CACHE = []
def update_cache():
    global SERVICES_CACHE
    try:
        res = requests.post(API_URL, data={'key': API_KEY, 'action': 'services'}).json()
        SERVICES_CACHE = res
    except: pass

# تحديث البيانات كل ساعة تلقائياً
update_cache()

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("🛍️ قائمة الخدمات المعربة", callback_data="all_sv"))
    markup.add(types.InlineKeyboardButton("📟 حسابك", callback_data="acc"), 
               types.InlineKeyboardButton("💰 شحن رصيد", callback_data="topup"))
    bot.send_message(message.chat.id, "👋 مرحباً بك في النسخة المطورة والسريعة\nالآن الخدمات معربة وتظهر فوراً!", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_actions(call):
    if call.data == "all_sv":
        platforms = [("📸 إنستقرام", "Instagram"), ("🎬 تيك توك", "TikTok"), ("🎥 يوتيوب", "YouTube"), ("🔹 تليجرام", "Telegram")]
        markup = types.InlineKeyboardMarkup(row_width=1)
        for name, pid in platforms:
            markup.add(types.InlineKeyboardButton(name, callback_data=f"p_{pid}"))
        bot.edit_message_text("📂 اختر المنصة (التحميل فوري):", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith("p_"):
        plat = call.data.split("_")[1]
        markup = types.InlineKeyboardMarkup(row_width=2)
        # تصنيفات فرعية واضحة
        subs = [("👥 متابعين", "Followers"), ("❤️ لايكات", "Likes"), ("👁️ مشاهدات", "Views")]
        for n, s in subs:
            markup.add(types.InlineKeyboardButton(n, callback_data=f"f_{plat}_{s}"))
        bot.edit_message_text(f"🛠️ خدمات {plat}:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith("f_"):
        _, plat, sub = call.data.split("_")
        markup = types.InlineKeyboardMarkup()
        
        # استخدام التخزين المؤقت (السرعة)
        count = 0
        for s in SERVICES_CACHE:
            if plat.lower() in s['category'].lower() and sub.lower() in s['name'].lower():
                if count < 10:
                    price = int(float(s['rate']) * POINT_VALUE)
                    # تعريب الاسم قبل العرض
                    arb_name = translate_name(s['name'])
                    markup.add(types.InlineKeyboardButton(f"🔹 {arb_name[:25]} | {price}ن", callback_data=f"ord_{s['service']}"))
                    count += 1
        
        bot.edit_message_text(f"🚀 تم تعريب خدمات {sub}:", call.message.chat.id, call.message.message_id, reply_markup=markup)

def run(): app.run(host='0.0.0.0', port=8080)
if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)

