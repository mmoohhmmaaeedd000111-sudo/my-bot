import telebot
from telebot import types
import json
import os

# --- إعداداتك ---
BOT_TOKEN = "8476427848:AAFvLp9QK8VYv4uZTCOkJR-H_mWnVvZQv3Q"
ADMIN_ID = "7154944941"  # استبدله بـ ID حسابك الحقيقي
API_KEY_KD1S = "9967a35290cae1978403a8caa91c59d6"
API_URL = "https://kd1s.com/api/v2"

bot = telebot.TeleBot(BOT_TOKEN)

# --- نظام قاعدة البيانات ---
DB_FILE = 'db.json'
def load_db():
    if not os.path.exists(DB_FILE): return {"users": {}, "codes": {}}
    with open(DB_FILE, 'r') as f: return json.load(f)

def save_db(db):
    with open(DB_FILE, 'w') as f: json.dump(db, f)

# --- الأوامر الرئيسية ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.chat.id)
    db = load_db()
    if uid not in db["users"]: db["users"][uid] = 0
    save_db(db)

    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("📋 قائمة الأسعار", callback_data="price_list")
    btn2 = types.InlineKeyboardButton("💰 شحن كود هدية", callback_data="redeem")
    btn3 = types.InlineKeyboardButton("🚀 طلب رشق", callback_data="order")
    btn4 = types.InlineKeyboardButton(f"💎 نقاطك: {db['users'][uid]}", callback_data="balance")
    markup.add(btn1, btn2, btn3, btn4)
    
    bot.send_message(message.chat.id, "🌟 مرحباً بك في متجر الشموخ للرشق التلقائي\nاستخدم الأزرار أدناه للتحكم:", reply_markup=markup)

# --- معالجة الأزرار ---
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    db = load_db()
    uid = str(call.message.chat.id)

    if call.data == "price_list":
        text = "📊 **أسعار الخدمات (بالنقاط):**\n\n"
        text += "👤 1000 متابع ثابت: 1000 نقطة\n"
        text += "❤️ 1000 لايك سريع: 250 نقطة\n"
        text += "🎥 1000 مشاهدة تيك توك: 100 نقطة\n\n"
        text += "💡 للشحن، تواصل مع الإدارة لشراء كود."
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="Markdown")

    elif call.data == "redeem":
        msg = bot.send_message(call.message.chat.id, "🎟 أرسل كود الهدية الخاص بك:")
        bot.register_next_step_handler(msg, process_redeem)

# --- نظام شحن الكود تلقائياً ---
def process_redeem(message):
    code = message.text
    db = load_db()
    uid = str(message.chat.id)

    if code in db["codes"]:
        amount = db["codes"][code]
        db["users"][uid] += amount
        del db["codes"][code] # حذف الكود لكي لا يستخدم مرة أخرى
        save_db(db)
        bot.reply_to(message, f"✅ تم شحن {amount} نقطة في حسابك بنجاح!")
    else:
        bot.reply_to(message, "❌ الكود غير صحيح أو تم استخدامه مسبقاً.")

# --- أوامر الأدمن (إنشاء كود) ---
@bot.message_handler(commands=['gen'])
def generate_code(message):
    if str(message.chat.id) == ADMIN_ID:
        try:
            _, amount = message.text.split()
            amount = int(amount)
            import strgen
            code = "SH-" + strgen.StringGenerator("[\w\d]{8}").render()
            db = load_db()
            db["codes"][code] = amount
            save_db(db)
            bot.reply_to(message, f"🎟 كود جديد بقيمة {amount} نقطة:\n`{code}`")
        except:
            bot.reply_to(message, "⚠️ التنسيق: /gen [المبلغ]")

bot.polling()
