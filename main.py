import telebot
from telebot import types
import json, os, random, string
from threading import Thread
from flask import Flask

# --- إعداداتك الخاصة ---
BOT_TOKEN = "8476427848:AAFvLp9QK8VYv4uZTCOkJR-H_mWnVvZQv3Q"
ADMIN_ID = "7154944941" # ايديك لإدارة الأكواد
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

@app.route('/')
def home(): return "BOT IS ACTIVE 🟢"

# --- إدارة قاعدة البيانات ---
def load_db():
    if not os.path.exists('db.json'): 
        return {"users": {}, "codes": {}, "orders_count": 6385597}
    with open('db.json', 'r') as f: return json.load(f)

def save_db(db):
    with open('db.json', 'w') as f: json.dump(db, f)

# --- واجهة الأزرار الاحترافية ---
def get_main_markup(uid):
    db = load_db()
    user_data = db["users"].get(uid, {"points": 0})
    pts = user_data.get("points", 0)
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(types.InlineKeyboardButton("🛍️ الخدمات", callback_data="services"))
    markup.add(types.InlineKeyboardButton(f"📟 الحساب ({pts})", callback_data="acc"), 
               types.InlineKeyboardButton("✳️ تجميع", callback_data="collect"))
    markup.add(types.InlineKeyboardButton("♻️ تحويل نقاط", callback_data="trans"), 
               types.InlineKeyboardButton("💳 استخدام كود", callback_data="use_code"))
    markup.add(types.InlineKeyboardButton("🚩 طلباتي", callback_data="my_orders"), 
               types.InlineKeyboardButton("📩 معلومات الطلب", callback_data="info"))
    markup.add(types.InlineKeyboardButton("📊 الاحصائيات", callback_data="stats"), 
               types.InlineKeyboardButton("💰 شحن نقاط", callback_data="topup"))
    markup.add(types.InlineKeyboardButton("📜 الشروط", callback_data="terms"), 
               types.InlineKeyboardButton("⚙️ التحديثات", callback_data="updates"))
    markup.row(types.InlineKeyboardButton(f"✅ عدد الطلبات : {db['orders_count']}", callback_data="none"))
    return markup

# --- رسالة الترحيب ونظام الإحالة ---
@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.chat.id)
    db = load_db()
    
    if uid not in db["users"]:
        db["users"][uid] = {"points": 0, "invited_by": None}
        # نظام تجميع النقاط عبر الرابط
        args = message.text.split()
        if len(args) > 1:
            inviter_id = args[1]
            if inviter_id in db["users"] and inviter_id != uid:
                db["users"][inviter_id]["points"] += 50 
                bot.send_message(inviter_id, "🔔 دخل شخص من رابطك وحصلت على 50 نقطة!")
    
    save_db(db)
    welcome_text = (f"👋 مرحباً بك في بوت الشموخ\n\n"
                    f"👤 نقاطك : {db['users'][uid]['points']}\n"
                    f"🆔 ايديك : {uid}")
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_markup(uid))

# --- وظيفة إنشاء كود (للمطور فقط) ---
# أرسل للأدمن: /gen 5000 (لإنشاء كود بقيمة 5000 نقطة)
@bot.message_handler(commands=['gen'])
def admin_gen_code(message):
    if str(message.chat.id) == ADMIN_ID:
        try:
            points = int(message.text.split()[1])
            code = "SHM-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            db = load_db()
            db["codes"][code] = points
            save_db(db)
            bot.send_message(ADMIN_ID, f"✅ تم إنشاء كود شحن جديد:\n`{code}`\nالقيمة: {points} نقطة", parse_mode="Markdown")
        except:
            bot.reply_to(message, "⚠️ استخدم الأمر هكذا: `/gen 1000`")

# --- معالجة الضغط على الأزرار ---
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    uid = str(call.message.chat.id)
    db = load_db()

    if call.data == "services":
        serv_text = ("📦 **أفضل خدمات الرشق:**\n\n"
                    "🔸 **إنستقرام**\n"
                    "├ 1000 متابع 👤 ⬅️ 1200 نقطة\n"
                    "└ 1000 لايك ❤️ ⬅️ 300 نقطة\n\n"
                    "🔹 **تيك توك**\n"
                    "├ 1000 متابع 👤 ⬅️ 1800 نقطة\n"
                    "└ 1000 مشاهدة 👀 ⬅️ 100 نقطة")
        bot.edit_message_text(serv_text, call.message.chat.id, call.message.message_id, 
                             reply_markup=types.InlineKeyboardMarkup().row(types.InlineKeyboardButton("🔙 رجوع", callback_data="back")), parse_mode="Markdown")

    elif call.data == "use_code":
        msg = bot.send_message(call.message.chat.id, "💳 يرجى إرسال كود الشحن الخاص بك:")
        bot.register_next_step_handler(msg, process_code_input)

    elif call.data == "collect":
        link = f"https://t.me/{bot.get_me().username}?start={uid}"
        bot.send_message(call.message.chat.id, f"✳️ **رابط الدعوة الخاص بك:**\n`{link}`\n\nشارك الرابط واحصل على 50 نقطة لكل شخص ينضم!", parse_mode="Markdown")

    elif call.data == "back":
        bot.edit_message_text("👋 القائمة الرئيسية:", call.message.chat.id, call.message.message_id, reply_markup=get_main_markup(uid))

# --- معالجة إدخال الكود من المستخدم ---
def process_code_input(message):
    user_code = message.text.strip()
    db = load_db()
    uid = str(message.chat.id)
    
    if user_code in db.get("codes", {}):
        points_to_add = db["codes"][user_code]
        db["users"][uid]["points"] += points_to_add
        del db["codes"][user_code] # حذف الكود لكي لا يستخدم مرتين
        save_db(db)
        bot.send_message(message.chat.id, f"✅ تم شحن {points_to_add} نقطة تلقائياً بنجاح!", reply_markup=get_main_markup(uid))
    else:
        bot.send_message(message.chat.id, "❌ الكود غير صحيح أو منتهي الصلاحية.", reply_markup=get_main_markup(uid))

def run(): app.run(host='0.0.0.0', port=8080)
if __name__ == "__main__":
    Thread(target=run).start()
    bot.polling(none_stop=True)
