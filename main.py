import telebot
from telebot import types
import requests
import os
from threading import Thread
from flask import Flask

# --- الإعدادات ---
BOT_TOKEN = "8476427848:AAFvLp9QK8VYv4uZTCOkJR-H_mWnVvZQv3Q"
API_KEY = "9967a35290cae1978403a8caa91c59d6"
API_URL = "https://kd1s.com/api/v2"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

@app.route('/')
def home(): return "SYSTEM ONLINE 🟢"

# --- القائمة الرئيسية ---
def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("🛍️ الخدمات", callback_data="open_services"))
    markup.add(types.InlineKeyboardButton("📟 الحساب", callback_data="open_acc"),
               types.InlineKeyboardButton("💰 شحن نقاط", callback_data="open_topup"))
    markup.add(types.InlineKeyboardButton("👨‍💻 تواصل مع المطور", url="https://t.me/l550r"))
    return markup

# --- ترتيب الأقسام باللغة العربية ---
MY_CATS = [
    {"n": "📸 إنستقرام", "id": "Instagram"},
    {"n": "🎬 تيك توك", "id": "TikTok"},
    {"n": "💬 واتساب", "id": "WhatsApp"},
    {"n": "🎥 يوتيوب", "id": "YouTube"},
    {"n": "🟡 سناب شات", "id": "Snapchat"},
    {"n": "🎮 بوبجي (PUBG)", "id": "PUBG"},
    {"n": "🎲 لودو (Ludo)", "id": "Ludo"},
    {"n": "🔹 تليجرام", "id": "Telegram"},
    {"n": "👤 فيسبوك", "id": "Facebook"}
]

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, "👋 أهلاً بك في بوت الشموخ\nيرجى اختيار أحد الخيارات أدناه:", reply_markup=main_menu())

# --- محرك معالجة الأزرار (Callback) ---
@bot.callback_query_handler(func=lambda call: True)
def handle_clicks(call):
    # 1. فتح قائمة الخدمات
    if call.data == "open_services":
        markup = types.InlineKeyboardMarkup(row_width=1)
        for cat in MY_CATS:
            markup.add(types.InlineKeyboardButton(cat["n"], callback_data=f"show_{cat['id']}"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_home"))
        bot.edit_message_text("📂 اختر المنصة المطلوبة (المنصات الرئيسية في الأعلى):", call.message.chat.id, call.message.message_id, reply_markup=markup)

    # 2. عرض الخدمات داخل قسم معين
    elif call.data.startswith("show_"):
        cat_id = call.data.split("_")[1]
        bot.answer_callback_query(call.id, "⏳ جاري تحميل الخدمات من kd1s...")
        
        try:
            res = requests.post(API_URL, data={'key': API_KEY, 'action': 'services'}).json()
            markup = types.InlineKeyboardMarkup()
            count = 0
            for s in res:
                if cat_id.lower() in s['category'].lower() and count < 15:
                    # تعريب أسماء الخدمات تلقائياً
                    s_name = s['name'].replace("Followers", "متابعين").replace("Likes", "لايكات").replace("Views", "مشاهدات")
                    markup.add(types.InlineKeyboardButton(f"🔹 {s_name}", callback_data=f"order_{s['service']}"))
                    count += 1
            markup.add(types.InlineKeyboardButton("🔙 العودة للأقسام", callback_data="open_services"))
            bot.edit_message_text(f"🚀 خدمات {cat_id}:", call.message.chat.id, call.message.message_id, reply_markup=markup)
        except:
            bot.send_message(call.message.chat.id, "❌ خطأ في الاتصال بالموقع المزود.")

    # 3. زر الحساب
    elif call.data == "open_acc":
        bot.answer_callback_query(call.id, "👤 حسابك: 0 نقطة\nلشحن الرصيد تواصل مع المطور.", show_alert=True)

    # 4. زر الشحن
    elif call.data == "open_topup":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("إضغط هنا لمراسلة المطور", url="https://t.me/l550r"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_home"))
        bot.edit_message_text("💰 لشحن نقاط في البوت، أرسل رسالة للمطور @l550r:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    # 5. زر الرجوع للخلف
    elif call.data == "back_home":
        bot.edit_message_text("👋 القائمة الرئيسية:", call.message.chat.id, call.message.message_id, reply_markup=main_menu())

# --- تشغيل البوت والسيرفر ---
def run(): app.run(host='0.0.0.0', port=8080)
if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
