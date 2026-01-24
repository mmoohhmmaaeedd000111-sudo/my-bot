import telebot
from telebot import types
import json, os, random, requests
from datetime import datetime, timedelta

# --- [ الإعدادات ] ---
TOKEN = "8476427848:AAFvLp9QK8VYv4uZTCOkJR-H_mWnVvZQv3Q"
ADMIN_ID = "8463703998"
MY_USER = "@l550r"  # معرف الشحن الخاص بك
API_KEY = "9967a35290cae1978403a8caa91c59d6" 
API_URL = "https://kd1s.com/api/v2"

bot = telebot.TeleBot(TOKEN)

# إنشاء المجلدات
for f in ["data", "codes"]:
    if not os.path.exists(f): os.makedirs(f)

# --- [ إدارة البيانات ] ---
def get_user(uid):
    path = f"data/{uid}.json"
    if not os.path.exists(path):
        data = {"coin": 0, "invite": 0, "used": 0, "last_gift": "2000-01-01 00:00:00"}
        with open(path, "w") as f: json.dump(data, f)
    return json.load(open(path))

def save_user(uid, data):
    with open(f"data/{uid}.json", "w") as f: json.dump(data, f, indent=4)

# --- [ القائمة الرئيسية ] ---
def main_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(types.InlineKeyboardButton("🛍️ قائمة الخدمات", callback_data="services"))
    markup.add(
        types.InlineKeyboardButton("📟 الحساب", callback_data="acc"),
        types.InlineKeyboardButton("✳️ تجميع نقاط", callback_data="collect")
    )
    markup.add(
        types.InlineKeyboardButton("💳 استخدام كود", callback_data="use_code"),
        types.InlineKeyboardButton("🚩 تتبع طلب", callback_data="track")
    )
    markup.row(types.InlineKeyboardButton("💰 شحن نقاط", callback_data="topup"))
    return markup

# --- [ معالجة الأوامر ] ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    user = get_user(uid)
    welcome = (
        f"👋 أهلاً بك يا {message.from_user.first_name}\n"
        f"————————————————\n"
        f"💰 نقاطك : {user['coin']}\n"
        f"👥 دعواتك : {user['invite']}\n"
        f"————————————————\n"
        f"🚀 أرخص خدمات الرشق بين يديك."
    )
    bot.send_message(message.chat.id, welcome, reply_markup=main_markup())

# --- [ معالجة ضغطات الأزرار ] ---
@bot.callback_query_handler(func=lambda call: True)
def handle_queries(call):
    uid = str(call.from_user.id)
    cid = call.message.chat.id
    mid = call.message.message_id
    user = get_user(uid)

    if call.data == "services":
        # عرض تصنيفات الخدمات (Instagram, TikTok, Telegram)
        s_markup = types.InlineKeyboardMarkup(row_width=2)
        s_markup.add(
            types.InlineKeyboardButton("📸 متابعين انستقرام", callback_data="show_insta"),
            types.InlineKeyboardButton("🔹 أعضاء تليجرام", callback_data="show_tele"),
            types.InlineKeyboardButton("🎬 متابعين تيك توك", callback_data="show_tik"),
            types.InlineKeyboardButton("🔙 رجوع", callback_data="home")
        )
        bot.edit_message_text("📂 اختر التصنيف المطلوب:", cid, mid, reply_markup=s_markup)

    elif call.data.startswith("show_"):
        platform = call.data.split("_")[1]
        bot.answer_callback_query(call.id, "⏳ جاري جلب الخدمات...")
        
        # جلب الخدمات وتصفيتها يدوياً للتأكد من ظهورها
        try:
            res = requests.post(API_URL, data={'key': API_KEY, 'action': 'services'}).json()
            markup = types.InlineKeyboardMarkup(row_width=1)
            for s in res[:50]: # فحص أول 50 خدمة
                if platform.lower() in s['name'].lower() or platform.lower() in s['category'].lower():
                    # تحويل السعر: السعر بالموقع * 2000 (مثال لتحويله لنقاط)
                    price = int(float(s['rate']) * 2000) 
                    markup.add(types.InlineKeyboardButton(f"{s['name'][:35]} | {price}ن", callback_data=f"buy_{s['service']}"))
            
            markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="services"))
            bot.edit_message_text(f"🚀 أهم خدمات {platform}:", cid, mid, reply_markup=markup)
        except:
            bot.answer_callback_query(call.id, "❌ فشل الاتصال بالموقع")

    elif call.data == "topup":
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 رجوع", callback_data="home"))
        bot.edit_message_text(f"💰 لشحن النقاط، تواصل مع المدير مباشرة عبر:\n{MY_USER}", cid, mid, reply_markup=markup)

    elif call.data == "acc":
        info = f"📟 حسابك:\n💰 النقاط: {user['coin']}\n👥 الدعوات: {user['invite']}"
        bot.answer_callback_query(call.id, info, show_alert=True)

    elif call.data == "collect":
        c_markup = types.InlineKeyboardMarkup()
        c_markup.add(types.InlineKeyboardButton("🎁 الهدية اليومية", callback_data="gift"))
        c_markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="home"))
        bot.edit_message_text("✳️ طرق تجميع النقاط المتوفرة حالياً:", cid, mid, reply_markup=c_markup)

    elif call.data == "gift":
        last = datetime.strptime(user["last_gift"], "%Y-%m-%d %H:%M:%S")
        if datetime.now() - last > timedelta(days=1):
            amount = random.randint(30, 80)
            user["coin"] += amount
            user["last_gift"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_user(uid, user)
            bot.answer_callback_query(call.id, f"✅ حصلت على {amount} نقطة هدية!", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "❌ حصلت على الهدية مسبقاً، عد غداً!", show_alert=True)

    elif call.data == "home":
        start(call.message)

    elif call.data == "use_code":
        msg = bot.send_message(cid, "💳 أرسل الكود الترويجي الآن:")
        bot.register_next_step_handler(msg, process_code)

def process_code(message):
    bot.send_message(message.chat.id, "❌ الكود غير صحيح حالياً.")

# --- [ تشغيل البوت ] ---
if __name__ == "__main__":
    print(f"✅ البوت يعمل الآن.. الشحن عبر {MY_USER}")
    bot.infinity_polling()
