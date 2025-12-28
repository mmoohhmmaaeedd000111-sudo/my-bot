import telebot
from telebot import types
import requests
from flask import Flask
from threading import Thread

# --- إعداداتك الثابتة ---
API_KEY_KD1S = "9967a35290cae1978403a8caa91c59d6" 
BOT_TOKEN = "8476427848:AAFvLp9QK8VYv4uZTCOkJR-H_mWnVvZQv3Q"
API_URL = "https://kd1s.com/api/v2"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

@app.route('/')
def home(): return "🟢 SYSTEM ONLINE"

# --- دالة إرسال الطلب للموقع ---
def send_order(s_id, link, qty):
    payload = {'key': API_KEY_KD1S, 'action': 'add', 'service': s_id, 'link': link, 'quantity': qty}
    return requests.post(API_URL, data=payload).json()

# --- واجهة الأوامر الرئيسية ---
@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    item1 = types.KeyboardButton("👤 متابعين انستقرام")
    item2 = types.KeyboardButton("❤️ لايكات انستقرام")
    item3 = types.KeyboardButton("🎥 مشاهدات تيك توك")
    item4 = types.KeyboardButton("📊 فحص الرصيد")
    markup.add(item1, item2, item3, item4)
    
    bot.send_message(message.chat.id, "🌟 أهلاً بك في بوت الرشق الاحترافي!\nاختر الخدمة من الأزرار بالأسفل:", reply_markup=markup)

# --- معالجة الأزرار ---
@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    if message.text == "📊 فحص الرصيد":
        res = requests.post(API_URL, data={'key': API_KEY_KD1S, 'action': 'balance'}).json()
        bot.reply_to(message, f"💰 رصيدك الحالي هو: {res.get('balance', '0')} {res.get('currency', 'USD')}")
    
    elif "متابعين" in message.text or "لايكات" in message.text or "مشاهدات" in message.text:
        bot.reply_to(message, f"📝 أرسل الطلب الآن بالتنسيق التالي:\n`الرابط|الكمية|ID_الخدمة`\n\n💡 مثال: `https://instgram.com/x|1000|1234`", parse_mode="Markdown")

# --- تشغيل السيرفر ---
def run(): app.run(host='0.0.0.0', port=8080)
if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
