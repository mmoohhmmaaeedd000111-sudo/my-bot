import telebot
from telebot import types
import json, os, random, requests
from datetime import datetime, timedelta

# --- [ الإعدادات ] ---
TOKEN = "8476427848:AAFvLp9QK8VYv4uZTCOkJR-H_mWnVvZQv3Q"
ADMIN_ID = "8463703998"
MY_USER = "@l550r" # معرف الشحن الخاص بك
API_KEY = "9967a35290cae1978403a8caa91c59d6" # مفتاح الموقع
API_URL = "https://kd1s.com/api/v2"

bot = telebot.TeleBot(TOKEN)

# التأكد من وجود المجلدات وقواعد البيانات
for f in ["data", "codes", "sudo"]:
    if not os.path.exists(f): os.makedirs(f)

# --- [ إدارة بيانات المستخدمين ] ---
def get_user(uid):
    path = f"data/{uid}.json"
    if not os.path.exists(path):
        data = {"coin": 0, "invite": 0, "used": 0, "last_gift": "2000-01-01 00:00:00"}
        with open(path, "w") as f: json.dump(data, f)
    return json.load(open(path))

def save_user(uid, data):
    with open(f"data/{uid}.json", "w") as f: json.dump(data, f, indent=4)

# --- [ الواجهة الرئيسية - مطابقة للصور ] ---
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

# --- [ أمر البداية ] ---
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
        f"🚀 يمكنك زيادة متابعينك وتفاعلاتك بسهولة من هنا."
    )
    bot.send_message(message.chat.id, welcome, reply_markup=main_markup())

# --- [ معالجة ضغطات الأزرار والخدمات ] ---
@bot.callback_query_handler(func=lambda call: True)
def handle_queries(call):
    uid = str(call.from_user.id)
    cid = call.message.chat.id
    mid = call.message.message_id
    user = get_user(uid)

    if call.data == "services":
        # عرض المنصات
        s_markup = types.InlineKeyboardMarkup(row_width=2)
        s_markup.add(
            types.InlineKeyboardButton("📸 إنستقرام", callback_data="plat_Instagram"),
            types.InlineKeyboardButton("🎬 تيك توك", callback_data="plat_TikTok"),
            types.InlineKeyboardButton("🔹 تليجرام", callback_data="plat_Telegram"),
            types.InlineKeyboardButton("🔙 رجوع", callback_data="home")
        )
        bot.edit_message_text("📂 اختر المنصة المطلوبة لعرض الخدمات:", cid, mid, reply_markup=s_markup)

    elif call.data.startswith("plat_"):
        platform = call.data.split("_")[1]
        bot.answer_callback_query(call.id, "⏳ جاري جلب الخدمات من الموقع...")
        
        # جلب الخدمات الحقيقية من API الموقع
        try:
            res = requests.post(API_URL, data={'key': API_KEY, 'action': 'services'}).json()
            markup = types.InlineKeyboardMarkup(row_width=1)
            count = 0
            for s in res:
                if platform.lower() in s['category'].lower() and count < 10:
                    price = int(float(s['rate']) * 2000) # تحويل السعر لنقاط
                    markup.add(types.InlineKeyboardButton(f"{s['name'][:30]} | {price}ن", callback_data=f"buy_{s['service']}_{price}"))
                    count += 1
            markup.add(types.InlineKeyboardButton("🔙 رجوع للخدمات", callback_data="services"))
            bot.edit_message_text(f"🚀 خدمات {platform} المتوفرة:\n(السعر لكل 1000 متابع)", cid, mid, reply_markup=markup)
        except:
            bot.send_message(cid, "❌ عذراً، فشل الاتصال بمزود الخدمة حالياً.")

    elif call.data == "topup":
        # تحديث معرف الشحن كما طلبت
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 رجوع", callback_data="home"))
        bot.edit_message_text(f"💰 لشحن النقاط، يرجى التواصل مع المدير:\n{MY_USER}\n\nأرسل له الأيدي الخاص بك: `{uid}`", cid, mid, parse_mode="Markdown", reply_markup=markup)

    elif call.data == "collect":
        c_markup = types.InlineKeyboardMarkup()
        c_markup.add(types.InlineKeyboardButton("🎁 الهدية اليومية", callback_data="gift"),
                     types.InlineKeyboardButton("🔗 رابط الدعوة", callback_data="link"))
        c_markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="home"))
        bot.edit_message_text("✳️ اختر طريقة تجميع النقاط:", cid, mid, reply_markup=c_markup)

    elif call.data == "gift":
        last = datetime.strptime(user["last_gift"], "%Y-%m-%d %H:%M:%S")
        if datetime.now() - last > timedelta(days=1):
            amount = random.randint(20, 100)
            user["coin"] += amount
            user["last_gift"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_user(uid, user)
            bot.answer_callback_query(call.id, f"🎉 مبروك! حصلت على {amount} نقطة هدية.", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "❌ حصلت على الهدية سابقاً، عد بعد 24 ساعة.", show_alert=True)

    elif call.data == "acc":
        bot.answer_callback_query(call.id, f"📟 حسابك:\n💰 الرصيد: {user['coin']}\n👥 الدعوات: {user['invite']}", show_alert=True)

    elif call.data == "home":
        start(call.message)

    elif call.data == "use_code":
        msg = bot.send_message(cid, "💳 أرسل الكود الترويجي الآن:")
        bot.register_next_step_handler(msg, process_promo)

# --- [ معالجة الكود الترويجي ] ---
def process_promo(message):
    uid = str(message.from_user.id)
    code = message.text
    path = f"codes/{code}.json"
    if os.path.exists(path):
        with open(path, "r") as f: c_data = json.load(f)
        if uid in c_data["users"]:
            bot.send_message(message.chat.id, "❌ استخدمت هذا الكود مسبقاً!")
        else:
            user = get_user(uid)
            user["coin"] += c_data["coins"]
            c_data["users"].append(uid)
            save_user(uid, user)
            with open(path, "w") as f: json.dump(c_data, f)
            bot.send_message(message.chat.id, f"✅ تم تفعيل الكود بنجاح! +{c_data['coins']} نقطة.")
    else:
        bot.send_message(message.chat.id, "❌ الكود غير صحيح أو منتهي.")

# --- [ تشغيل البوت ] ---
if __name__ == "__main__":
    print(f"✅ البوت شغال الآن. الشحن عبر: {MY_USER}")
    bot.infinity_polling()
