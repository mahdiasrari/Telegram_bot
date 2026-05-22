import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import json
import random
import time
import re

# ========== تنظیمات شما (این قسمت را خودتان پر کنید) ==========
TOKEN = "8608366141:AAF--055H5ChffBhg-EosXLFPB_c1piu3mo"  # توکن خود را اینجا بگذارید
CHANNEL_ID = "-1003540254127"  # آیدی عددی کانال
CHANNEL_LINK = "https://t.me/internetazadie"  # لینک کانال
# ============================================================

bot = telebot.TeleBot(TOKEN)

# تابع چک کردن عضویت در کانال
def is_member(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

# منوی اصلی
def main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    btn_vless = InlineKeyboardButton("🇮🇷 کانفیگ VLESS+REALITY", callback_data="vless")
    btn_warp = InlineKeyboardButton("✨ کانفیگ Warp (UDP)", callback_data="warp")
    markup.add(btn_vless, btn_warp)
    return markup

# دریافت کانفیگ رندوم از منابع عمومی (VLESS)
def get_random_vless():
    # منابع عمومی کانفیگ (می‌توانید بیشتر اضافه کنید)
    sources = [
        "https://raw.githubusercontent.com/yitr80/configsv2ray/main/configs.txt",
        "https://raw.githubusercontent.com/v2fly/configs/master/vless.txt",
    ]
    
    for source in sources:
        try:
            response = requests.get(source, timeout=10)
            if response.status_code == 200:
                lines = response.text.splitlines()
                vless_configs = [line for line in lines if line.startswith("vless://")]
                if vless_configs:
                    return random.choice(vless_configs)
        except:
            continue
    return None

# دریافت کانفیگ Warp رندوم
def get_random_warp():
    try:
        # استفاده از API عمومی Warp
        response = requests.get("https://api.zeroteam.top/warp", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return data.get("config")
    except:
        pass
    return None

# هندلر استارت
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    
    if not is_member(user_id):
        markup = InlineKeyboardMarkup()
        btn_join = InlineKeyboardButton("📢 عضویت در کانال", url=CHANNEL_LINK)
        btn_check = InlineKeyboardButton("✅ تایید عضویت", callback_data="check_membership")
        markup.add(btn_join, btn_check)
        
        bot.send_message(
            message.chat.id,
            f"❌ ابتدا باید در کانال ما عضو شوید:\n{CHANNEL_LINK}\n\nپس از عضویت، دکمه تایید را بزنید.",
            reply_markup=markup
        )
        return
    
    bot.send_message(
        message.chat.id,
        "🎉 به ربات خوش آمدید!\n\nاز منوی زیر نوع کانفیگ مورد نظر خود را انتخاب کنید:",
        reply_markup=main_menu()
    )

# بررسی عضویت با دکمه تایید
@bot.callback_query_handler(func=lambda call: call.data == "check_membership")
def check_membership(call):
    user_id = call.from_user.id
    if is_member(user_id):
        bot.edit_message_text(
            "✅ عضویت شما تأیید شد!\n\nاز منوی زیر نوع کانفیگ را انتخاب کنید:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=main_menu()
        )
    else:
        bot.answer_callback_query(call.id, "❌ هنوز عضو کانال نشده‌اید!", show_alert=True)

# هندلر دکمه‌های منو
@bot.callback_query_handler(func=lambda call: call.data in ["vless", "warp"])
def handle_configs(call):
    user_id = call.from_user.id
    if not is_member(user_id):
        bot.answer_callback_query(call.id, "❌ ابتدا باید در کانال عضو شوید!", show_alert=True)
        return
    
    bot.edit_message_text("🔄 در حال دریافت کانفیگ، لطفاً چند ثانیه صبر کنید...", 
                          call.message.chat.id, call.message.message_id)
    
    if call.data == "vless":
        config = get_random_vless()
        title = "🇮🇷 کانفیگ VLESS+REALITY"
    else:
        config = get_random_warp()
        title = "✨ کانفیگ Warp"
    
    if config:
        response_text = f"🔰 {title} :\n\n```\n{config}\n```\n\n📌 کانفیگ به صورت رندوم از منابع عمومی دریافت شده است."
        bot.send_message(call.message.chat.id, response_text, parse_mode="Markdown")
    else:
        bot.send_message(call.message.chat.id, "⚠️ در حال حاضر کانفیگ فعالی یافت نشد. لطفاً چند دقیقه دیگر تلاش کنید.")
    
    # برگشت به منوی اصلی
    bot.send_message(call.message.chat.id, "منوی اصلی:", reply_markup=main_menu())

# اجرای ربات
if __name__ == "__main__":
    print("ربات روشن شد...")
    bot.infinity_polling()
