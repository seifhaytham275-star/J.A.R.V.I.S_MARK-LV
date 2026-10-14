import telebot

# التوكن الصحيح للبوت الخاص بك
TOKEN = '8541874973:AAGmnu235cTPtqziM959YsNiPfyOgbblizk'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_text = message.text
    
    # هنا جارفيس يستقبل رسالتك ويرد عليك
    response_text = f"جارفيس (اللابتوب) استلم رسالتك: {user_text}"
    
    bot.reply_to(message, response_text)

print("Jarvis Telegram Bridge is running...")
bot.infinity_polling()