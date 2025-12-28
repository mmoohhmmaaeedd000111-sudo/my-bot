import telebot
import requests
from flask import Flask
from threading import Thread

# بياناتك الجاهزة
API_KEY_KD1S = "9967a35290cae1978403a8caa91c59d6" 
BOT_TOKEN = "8476427848:AAFvLp9QK8VYv4uZTCOkJR-H_mWnVvZQv3Q"
API_URL = "https://kd1s.com/api/v2"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

@app.route('/')
def home(): return "🟢 SHΔDØW SYSTEM ONLINE"

def run(): app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🔥 نظام الرشق جاهز للعمل!\nأرسل: الرابط|الكمية|ID")

@bot.message_handler(func=lambda message: "|" in message.text)
def handle_order(message):
    try:
        data = message.text.split('|')
        payload = {'key': API_KEY_KD1S, 'action': 'add', 'service': data[2].strip(), 'link': data[0].strip(), 'quantity': data[1].strip()}
        response = requests.post(API_URL, data=payload).json()
        if 'order' in response:
            bot.send_message(message.chat.id, f"✅ تم الطلب بنجاح!\nرقم الطلب: {response['order']}")
        else:
            bot.send_message(message.chat.id, f"❌ فشل من الموقع: {response.get('error')}")
    except:
        bot.reply_to(message, "⚠️ تأكد من التنسيق الصحيح: رابط|كمية|ID")

if __name__ == "__main__":
    keep_alive()
    bot.polling(none_stop=True)
