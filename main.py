import telebot
from telebot import types
import json, os, time

# --- الإعدادات ---
TOKEN = "8476427848:AAFvLp9QK8VYv4uZTCOkJR-H_mWnVvZQv3Q"
ADMIN_ID = "8463703998"
bot = telebot.TeleBot(TOKEN)

# --- دالة جلب بيانات المستخدم ---
def get_user(uid):
    path = f"data/{uid}.json"
    if not os.path.exists("data"): os.makedirs("data")
    if not os.path.exists(path):
        data = {"coin": 0, "invite": 0, "used": 0, "name": ""}
        with open(path, "w") as f: json.dump(data, f)
    return json.load(open(path))

def save_user(uid, data):
    with open(f"data/{uid}.json", "w") as f: json.dump(data, f)

# --- الواجهة الرئيسية (مطابقة للصور) ---
def main_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    # السطر الأول: الخدمات
    markup.row(types.InlineKeyboardButton("🛍️ قائمة الخدمات", callback_data="services"))
    # السطر الثاني: الحساب وتجميع النقاط
    markup.add(
        types.InlineKeyboardButton("📟 الحساب", callback_data="acc"),
        types.InlineKeyboardButton("✳️ تجميع نقاط", callback_data="collect")
    )
    # السطر الثالث: استخدام كود وتتبع طلب
    markup.add(
        types.InlineKeyboardButton("💳 استخدام كود", callback_data="use_code"),
        types.InlineKeyboardButton("🚩 تتبع طلب", callback_data="track")
    )
    # السطر الأخير: شحن النقاط
    markup.row(types.InlineKeyboardButton("💰 شحن نقاط", callback_data="topup"))
    return markup

# --- أمر التشغيل ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    user = get_user(uid)
    
    # رسالة الترحيب بنفس نمط الصورة
    welcome_text = (
        f"👋 أهلاً بك يا {message.from_user.first_name} في بوت دعمكم\n"
        f"————————————————\n"
        f"💰 نقاطك الحالية: {user['coin']}\n"
        f"✳️ نقاطك المستخدمة: {user['used']}\n"
        f"👥 عدد دعواتك: {user['invite']}\n"
        f"————————————————\n"
        f"🚀 يمكنك زيادة متابعينك وتفاعلاتك بسهولة من هنا."
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_markup())

# --- معالجة الأزرار ---
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    uid = str(call.from_user.id)
    
    if call.data == "acc":
        user = get_user(uid)
        text = f"🗃️ تفاصيل حسابك:\n\n💰 الرصيد: {user['coin']}\n👥 الدعوات: {user['invite']}"
        bot.answer_callback_query(call.id, text, show_alert=True)
        
    elif call.data == "services":
        # واجهة الخدمات الفرعية
        s_markup = types.InlineKeyboardMarkup(row_width=2)
        s_markup.add(
            types.InlineKeyboardButton("📸 إنستقرام", callback_data="ser_insta"),
            types.InlineKeyboardButton("🎬 تيك توك", callback_data="ser_tik")
        )
        s_markup.row(types.InlineKeyboardButton("🔙 رجوع", callback_data="home"))
        bot.edit_message_text("📂 اختر المنصة المطلوبة:", call.message.chat.id, call.message.message_id, reply_markup=s_markup)

    elif call.data == "home":
        user = get_user(uid)
        welcome_text = f"👋 أهلاً بك مجدداً..\n💰 نقاطك: {user['coin']}"
        bot.edit_message_text(welcome_text, call.message.chat.id, call.message.message_id, reply_markup=main_markup())

# --- تشغيل البوت ---
print("✅ البوت يعمل الآن بنفس تصميم الصور...")
bot.infinity_polling()
