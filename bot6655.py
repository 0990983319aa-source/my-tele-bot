import os
from threading import Thread
from flask import Flask
from pyrogram import Client, filters

# سيرفر ويب خفيف لفتح البورت وإرضاء Render
app = Flask('')

@app.route('/')
def home():
    return "Bot is active!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# تشغيل السيرفر في خيط منفصل
Thread(target=run_web).start()

# كود البوت الأساسي (ضع بياناتك هنا إذا احتجت)
API_ID = os.environ.get("API_ID", "123456")
API_HASH = os.environ.get("API_HASH", "your_api_hash")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "your_bot_token")

bot = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.command("start"))
def start(client, message):
    message.reply_text("أهلاً بك! البوت شغال بنجاح على Render 🚀")

bot.run()
