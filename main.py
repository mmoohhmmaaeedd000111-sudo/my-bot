import telebot
from telebot import types
import json, os, random
from datetime import datetime, timedelta

# --- [ الإعدادات ] ---
TOKEN = "8476427848:AAFvLp9QK8VYv4uZTCOkJR-H_mWnVvZQv3Q"
ADMIN_ID = "8463703998"
bot = telebot.TeleBot(TOKEN)

# التأكد من وجود المجلدات
for f in ["data", "codes"]:
    if not os.path.exists(f): os.makedirs(f)

# --- [ إدارة البيانات ] ---
def get_user(uid):
    path = f"data/{uid}.json"
    if not os.path.exists(path):
        data = {"coin": 0, "invite": 0, "used": 0, "last_gift": "2000-01-01 00:00:00"}
        json.dump(data, open(path, "w"))
    return json.load(open(path))

def save_user(uid, data):
    json.dump(data, open(f"data/{uid}.json", "w"), indent=4)

# --- [ الأزرار الرئيسية (مطابقة للصورة تماماً) ] ---
def main_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    # 🛍️ قائمة الخدمات (سطر كامل)
    markup.row(types.InlineKeyboardButton("🛍️ قائمة الخدمات", callback_data="services"))
    # 📟 الحساب و ✳️ تجميع نقاط
    markup.add(
        types.InlineKeyboardButton("📟 الحساب", callback_data="acc"),
        types.InlineKeyboardButton("✳️ تجميع نقاط", callback_data="collect")
    )
    # 💳 استخدام كود و 🚩 تتبع طلب
    markup.add(
        types.InlineKeyboardButton("💳 استخدام كود", callback_data="use_code"),
        types.InlineKeyboardButton("🚩 تتبع طلب", callback_data="track")
    )
    # 💰 شحن نقاط (سطر كامل)
    markup.row(types.InlineKeyboardButton("💰 شحن نقاط", callback_data="topup"))
    return markup

# --- [ الأوامر ] ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    user = get_user(uid)
    welcome = (
        f"👋 أهلاً بك يا {message.from_user.first_name} في بوت دعمكم\n"
        f"————————————————\n"
        f"💰 نقاطك الحالية : {user['coin']}\n"
        f"✳️ نقاطك المستخدمة : {user['used']}\n"
        f"👥 عدد دعواتك : {user['invite']}\n"
        f"————————————————\n"
        f"🚀 يمكنك زيادة متابعينك وتفاعلاتك بسهولة."
    )
    bot.send_message(message.chat.id, welcome, reply_markup=main_markup())

# --- [ معالجة جميع الأزرار ] ---
@bot.callback_query_handler(func=lambda call: True)
def handle_queries(call):
    uid = str(call.from_user.id)
    cid = call.message.chat.id
    mid = call.message.message_id
    user = get_user(uid)

    if call.data == "services":
        # قسم الخدمات
        s_markup = types.InlineKeyboardMarkup(row_width=2)
        s_markup.add(
            types.InlineKeyboardButton("📸 إنستقرام", callback_data="buy_insta"),
            types.InlineKeyboardButton("🎬 تيك توك", callback_data="buy_tiktok"),
            types.InlineKeyboardButton("🔹 تليجرام", callback_data="buy_tele"),
            types.InlineKeyboardButton("🔙 رجوع", callback_data="home")
        )
        bot.edit_message_text("📂 اختر المنصة التي تريد الرشق لها:", cid, mid, reply_markup=s_markup)

    elif call.data == "acc":
        # قسم الحساب (إظهار المعلومات في رسالة منبثقة)
        info = f"📟 تفاصيل حسابك:\n💰 النقاط: {user['coin']}\n👥 الدعوات: {user['invite']}\n✳️ المستخدم: {user['used']}"
        bot.answer_callback_query(call.id, info, show_alert=True)

    elif call.data == "collect":
        # قسم تجميع النقاط
        c_markup = types.InlineKeyboardMarkup()
        c_markup.add(types.InlineKeyboardButton("🎁 الهدية اليومية", callback_data="gift"))
        c_markup.add(types.InlineKeyboardButton("🔗 رابط الدعوة", callback_data="link"))
        c_markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="home"))
        bot.edit_message_text("✳️ اختر طريقة تجميع النقاط:", cid, mid, reply_markup=c_markup)

    elif call.data == "gift":
        # منطق الهدية اليومية
        last = datetime.strptime(user["last_gift"], "%Y-%m-%d %H:%M:%S")
        if datetime.now() - last > timedelta(days=1):
            amount = random.randint(10, 50)
            user["coin"] += amount
            user["last_gift"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_user(uid, user)
            bot.answer_callback_query(call.id, f"✅ حصلت على {amount} نقطة هدية!", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "❌ حصلت على الهدية سابقاً، عد بعد 24 ساعة.", show_alert=True)

    elif call.data == "use_code":
        # استخدام الكود
        msg = bot.send_message(cid, "💳 أرسل الكود الترويجي الآن:")
        bot.register_next_step_handler(msg, process_code)

    elif call.data == "track":
        bot.answer_callback_query(call.id, "🚩 لا توجد طلبات نشطة حالياً لتتبعها.", show_alert=True)

    elif call.data == "topup":
        bot.edit_message_text("💰 لشحن النقاط، يرجى التواصل مع المطور:\n@BBI4BB", cid, mid, 
                             reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 رجوع", callback_data="home")))

    elif call.data == "home":
        # العودة للقائمة الرئيسية
        user = get_user(uid)
        welcome = f"👋 أهلاً بك مجدداً..\n💰 نقاطك الحالية: {user['coin']}"
        bot.edit_message_text(welcome, cid, mid, reply_markup=main_markup())

# --- [ وظيفة الكود ] ---
def process_code(message):
    uid = str(message.from_user.id)
    code = message.text
    path = f"codes/{code}.json"
    if os.path.exists(path):
        c_data = json.load(open(path))
        if uid in c_data["users"]:
            bot.send_message(message.chat.id, "❌ استخدمت هذا الكود من قبل!")
        else:
            user = get_user(uid)
            user["coin"] += c_data["coins"]
            c_data["users"].append(uid)
            save_user(uid, user)
            json.dump(c_data, open(path, "w"))
            bot.send_message(message.chat.id, f"✅ تم تفعيل الكود بنجاح! حصلت على {c_data['coins']} نقطة.")
    else:
        bot.send_message(message.chat.id, "❌ الكود غير صحيح.")

# --- [ أمر الأدمن لإنشاء الأكواد ] ---
@bot.message_handler(commands=['addcode'])
def admin_add_code(message):
    if str(message.from_user.id) == ADMIN_ID:
        try:
            _, name, coins = message.text.split()
            data = {"coins": int(coins), "users": []}
            json.dump(data, open(f"codes/{name}.json", "w"))
            bot.reply_to(message, f"✅ تم إنشاء كود `{name}` بقيمة {coins} نقطة.")
        except:
            bot.reply_to(message, "الاستخدام: /addcode اسم_الكود عدد_النقاط")

# تشغيل البوت
print("🚀 البوت يعمل الآن بكامل الأزرار والوظائف...")
bot.infinity_polling()
