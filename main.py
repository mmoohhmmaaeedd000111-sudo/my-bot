import telebot
from telebot import types
import json, os, time, random
from datetime import datetime, timedelta

# --- [ الإعدادات ] ---
TOKEN = "8476427848:AAFvLp9QK8VYv4uZTCOkJR-H_mWnVvZQv3Q"
ADMIN_ID = "8463703998"
bot = telebot.TeleBot(TOKEN)

# إنشاء المجلدات
for folder in ["data", "sudo", "codes"]:
    if not os.path.exists(folder): os.makedirs(folder)

# --- [ إدارة البيانات ] ---
def get_user_data(uid):
    path = f"data/{uid}.json"
    if not os.path.exists(path):
        data = {"coin": 0, "invite": 0, "used": 0, "last_gift": "2000-01-01 00:00:00", "referred_by": None}
        with open(path, "w") as f: json.dump(data, f)
    return json.load(open(path))

def save_user_data(uid, data):
    with open(f"data/{uid}.json", "w") as f: json.dump(data, f, indent=4)

# --- [ لوحة تحكم الأدمن لإنشاء كود ] ---
@bot.message_handler(commands=['addcode'])
def add_promo_code(message):
    if str(message.from_user.id) == ADMIN_ID:
        try:
            # الأمر يكون: /addcode اسم_الكود عدد_النقاط
            msg_parts = message.text.split()
            code_name = msg_parts[1]
            coins = int(msg_parts[2])
            
            code_data = {"coins": coins, "users": []} # users لحفظ من استخدم الكود لمنع التكرار
            with open(f"codes/{code_name}.json", "w") as f:
                json.dump(code_data, f)
            bot.reply_to(message, f"✅ تم إنشاء كود: `{code_name}`\n💰 بقيمة: {coins} نقطة", parse_mode="Markdown")
        except:
            bot.reply_to(message, "❌ خطأ! استخدم الصيغة: /addcode كود 100")

# --- [ الواجهة الرئيسية ] ---
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

@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    user = get_user_data(uid)
    welcome_text = (
        f"👋 أهلاً بك يا {message.from_user.first_name}\n"
        f"💰 نقاطك: {user['coin']}\n"
        f"👥 دعواتك: {user['invite']}\n"
        f"————————————————\n"
        f"🚀 اختر من القائمة أدناه للبدء:"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_markup())

# --- [ معالجة ضغطات الأزرار ] ---
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    uid = str(call.from_user.id)
    
    if call.data == "use_code":
        msg = bot.send_message(call.message.chat.id, "💳 أرسل الكود الترويجي الآن:")
        bot.register_next_step_handler(msg, process_promo_code)

    elif call.data == "daily_gift":
        user = get_user_data(uid)
        last_gift = datetime.strptime(user["last_gift"], "%Y-%m-%d %H:%M:%S")
        if datetime.now() - last_gift > timedelta(days=1):
            gift = random.randint(10, 100)
            user["coin"] += gift
            user["last_gift"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_user_data(uid, user)
            bot.answer_callback_query(call.id, f"🎉 مبروك حصلت على {gift} نقطة!", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "❌ عد غداً للحصول على هدية جديدة.", show_alert=True)

    elif call.data == "collect":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🎁 الهدية اليومية", callback_data="daily_gift"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="home"))
        bot.edit_message_text("✳️ طرق تجميع النقاط:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == "home":
        start(call.message)

# --- [ وظيفة معالجة الكود الترويجي ] ---
def process_promo_code(message):
    uid = str(message.from_user.id)
    code_name = message.text
    path = f"codes/{code_name}.json"
    
    if os.path.exists(path):
        with open(path, "r") as f:
            code_data = json.load(f)
        
        if uid in code_data["users"]:
            bot.send_message(message.chat.id, "❌ لقد استخدمت هذا الكود مسبقاً!")
        else:
            user = get_user_data(uid)
            user["coin"] += code_data["coins"]
            code_data["users"].append(uid)
            save_user_data(uid, user)
            with open(path, "w") as f: json.dump(code_data, f)
            bot.send_message(message.chat.id, f"✅ تم تفعيل الكود بنجاح! حصلت على {code_data['coins']} نقطة.")
    else:
        bot.send_message(message.chat.id, "❌ هذا الكود غير صحيح أو انتهت صلاحيته.")

if __name__ == "__main__":
    print("🚀 البوت يعمل الآن بكامل مميزاته..")
    bot.infinity_polling()
