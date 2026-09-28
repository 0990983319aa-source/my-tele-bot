import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from pyrogram.errors import SessionPasswordNeeded, PhoneCodeExpired, PhoneCodeInvalid, PeerIdInvalid
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioVideoPiped

API_ID = 38579074
API_HASH = "e01afc2c6b108526045c9590650ce9a0"
BOT_TOKEN = "8945311575:AAGip7iyclkRbCAJFOpuvQcahmztWAJXk_o"

bot = Client("GlobalStreamBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
users_db = {}

def get_welcome_text(user_name):
    return f"✨ أهلاً بك يا القيادة 🌟 {user_name}\n\n🎛 **اللوحة التحكمية الشاملة للبث المباشر:**\n\n🔹 **تحديد قناة/مجموعة:** لتحديد وجهة البث\n🔹 **رفع الفيديو:** لرفع مقطع الميديا\n🔹 **تشغيل / إيقاف البث:** للتحكم في البث الحي\n🔹 **تسجيل الدخول:** لربط حسابك وتأكيده بأمان\n\nالاشتراك: 🟢 **دائم (حساب المطور)**"

def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 تحديد قناة / مجموعة", callback_data="select_chat")],
        [InlineKeyboardButton("📥 رفع الفيديو", callback_data="upload_video")],
        [
            InlineKeyboardButton("⏹ إيقاف البث", callback_data="stop_stream"),
            InlineKeyboardButton("▶️ تشغيل البث", callback_data="start_stream")
        ],
        [InlineKeyboardButton("🔐 تسجيل الدخول بالحساب", callback_data="login")],
        [
            InlineKeyboardButton("🗑 حذف القناة", callback_data="delete_channel"),
            InlineKeyboardButton("🎬 حذف الفيديو", callback_data="delete_video")
        ],
        [InlineKeyboardButton("🧹 مسح جميع البيانات", callback_data="clear_data")],
        [InlineKeyboardButton("📊 معلومات الحساب", callback_data="account_info")],
        [InlineKeyboardButton("👨‍💻 تواصل مع المطور", url="https://t.me/RogStsr")],
        [InlineKeyboardButton("⚡️ قائمة الأدمن", callback_data="admin_menu")]
    ])

def get_user_data(user_id):
    if user_id not in users_db:
        users_db[user_id] = {
            "user_client": None,
            "call_app": None,
            "chat": None,
            "video": None,
            "state": None,
            "phone": None,
            "phone_hash": None,
            "temp_client": None
        }
    return users_db[user_id]

@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(client: Client, message: Message):
    get_user_data(message.from_user.id)
    user_name = message.from_user.first_name or "المستخدم"
    await message.reply_text(get_welcome_text(user_name), reply_markup=main_keyboard())

@bot.on_callback_query()
async def handle_callbacks(client: Client, query: CallbackQuery):
    u_id = query.from_user.id
    u_data = get_user_data(u_id)
    data = query.data

    if data == "login":
        u_data["state"] = "WAITING_PHONE"
        await query.message.reply_text("📱 **أرسل رقم هاتفك الآن مع رمز الدولة**\nمثال: `+249912345678`")
        await query.answer()

    elif data == "select_chat":
        u_data["state"] = "WAITING_CHAT"
        await query.message.reply_text("📢 **أرسل معرف القناة/المجموعة** (مثال: `@mychannel`)\nأو قم بتوجيه رسالة منها هنا:")
        await query.answer()

    elif data == "upload_video":
        u_data["state"] = "WAITING_VIDEO"
        await query.message.reply_text("📥 **أرسل ملف الفيديو الآن لتخزينه:**")
        await query.answer()

    elif data == "start_stream":
        if not u_data.get("user_client"):
            await query.answer("❌ يجب عليك تسجيل الدخول بحسابك أولاً!", show_alert=True)
            return
        if not u_data.get("chat"):
            await query.answer("❌ يرجى تحديد القناة/المجموعة أولاً!", show_alert=True)
            return
        if not u_data.get("video"):
            await query.answer("❌ يرجى رفع الفيديو أولاً!", show_alert=True)
            return

        try:
            await query.answer("🚀 جاري بدء البث المباشر...")
            await u_data["call_app"].join_group_call(
                u_data["chat"],
                AudioVideoPiped(u_data["video"])
            )
            await query.message.reply_text("🔴 **البث المباشر يعمل الآن داخل القناة بنجاح!**")
        except Exception as e:
            await query.message.reply_text(f"❌ حدث خطأ أثناء تشغيل البث: `{e}`")

    elif data == "stop_stream":
        if u_data.get("call_app"):
            try:
                await u_data["call_app"].leave_group_call(u_data["chat"])
                await query.answer("⏹ تم إيقاف البث المباشر بنجاح", show_alert=True)
            except Exception as e:
                await query.answer("❌ لا يوجد بث شغال حالياً", show_alert=True)
        else:
            await query.answer("❌ لم تقم بتسجيل الدخول بعد", show_alert=True)

    elif data == "delete_channel":
        u_data["chat"] = None
        await query.answer("🗑 تم حذف القناة المحددة", show_alert=True)

    elif data == "delete_video":
        if u_data.get("video") and os.path.exists(u_data["video"]):
            try:
                os.remove(u_data["video"])
            except:
                pass
        u_data["video"] = None
        await query.answer("🎬 تم حذف الفيديو المحفوظ", show_alert=True)

    elif data == "clear_data":
        u_data["chat"] = None
        if u_data.get("video") and os.path.exists(u_data["video"]):
            try:
                os.remove(u_data["video"])
            except:
                pass
        u_data["video"] = None
        await query.answer("🧹 تم مسح جميع البيانات بنجاح", show_alert=True)

    elif data == "account_info":
        logged = "مرتبط بنجاح ✅" if u_data.get("user_client") else "غير مرتبط ❌"
        info = f"👤 حالة الحساب: {logged}\n📢 القناة: {u_data.get('chat') or 'غير محددة'}\n🎬 الفيديو: {'موجود ✅' if u_data.get('video') else 'غير موجود ❌'}\n⭐️ الاشتراك: دائم"
        await query.answer(info, show_alert=True)

    elif data == "admin_menu":
        await query.answer("⚡️ لوحة الأدمن جاهزة...", show_alert=False)

@bot.on_message(filters.private & ~filters.command("start"))
async def handle_inputs(client: Client, message: Message):
    u_id = message.from_user.id
    u_data = get_user_data(u_id)
    state = u_data.get("state")

    if state == "WAITING_PHONE" and message.text:
        phone = message.text.strip()
        if u_data.get("temp_client"):
            try:
                await u_data["temp_client"].disconnect()
            except:
                pass

        session_name = f"user_{u_id}"
        u_client = Client(session_name, api_id=API_ID, api_hash=API_HASH, in_memory=False)
        await u_client.connect()
        try:
            code_info = await u_client.send_code(phone)
            u_data["temp_client"] = u_client
            u_data["phone"] = phone
            u_data["phone_hash"] = code_info.phone_code_hash
            u_data["state"] = "WAITING_CODE"
            await message.reply_text("🔑 **تم إرسال كود التحقق.** أرسل الكود هنا:")
        except Exception as e:
            await u_client.disconnect()
            await message.reply_text(f"❌ حدث خطأ أثناء إرسال الكود: `{e}`")
            u_data["state"] = None

    elif state == "WAITING_CODE" and message.text:
        code = message.text.replace(" ", "").strip()
        u_client = u_data.get("temp_client")
        if not u_client:
            await message.reply_text("❌ أعد طلب تسجيل الدخول من جديد.")
            u_data["state"] = None
            return

        try:
            await u_client.sign_in(u_data["phone"], u_data["phone_hash"], code)
            call = PyTgCalls(u_client)
            await call.start()
            u_data["user_client"] = u_client
            u_data["call_app"] = call
            u_data["state"] = None
            await message.reply_text("✅ **تم تسجيل دخول حسابك بنجاح وحفظ الجلسة!**")
        except SessionPasswordNeeded:
            u_data["state"] = "WAITING_PASSWORD"
            await message.reply_text("🔐 **الحساب محمي بتحقق بخطوتين.** أرسل كلمة المرور:")
        except PhoneCodeExpired:
            await message.reply_text("❌ **انتهت صلاحية الكود.** اطلب تسجيل الدخول مجدداً.")
            u_data["state"] = None
        except PhoneCodeInvalid:
            await message.reply_text("❌ **الكود غير صحيح!**")
        except Exception as e:
            await message.reply_text(f"❌ فشل تسجيل الدخول: `{e}`")

    elif state == "WAITING_PASSWORD" and message.text:
        password = message.text.strip()
        u_client = u_data.get("temp_client")
        try:
            await u_client.check_password(password)
            call = PyTgCalls(u_client)
            await call.start()
            u_data["user_client"] = u_client
            u_data["call_app"] = call
            u_data["state"] = None
            await message.reply_text("✅ **تم التحقق وتسجيل الدخول بنجاح!**")
        except Exception as e:
            await message.reply_text(f"❌ خطأ في كلمة المرور: `{e}`")

    elif state == "WAITING_CHAT":
        chat_input = message.forward_from_chat.id if message.forward_from_chat else (message.text.strip() if message.text else None)
        if chat_input:
            try:
                target_chat = await client.get_chat(chat_input)
                u_data["chat"] = target_chat.id
                u_data["state"] = None
                await message.reply_text(f"✅ **تم تحديد القناة:** `{target_chat.title}` ({target_chat.id})")
            except Exception as e:
                await message.reply_text(f"❌ تعذر التعرف على القناة: `{e}`")
        else:
            await message.reply_text("❌ أرسل معرفاً صحيحاً أو وجّه رسالة من القناة.")

    elif state == "WAITING_VIDEO" and message.video:
        msg = await message.reply_text("📥 **جاري تحميل الفيديو...**")
        path = await message.download()
        u_data["video"] = path
        u_data["state"] = None
        await msg.edit_text("✅ **تم حفظ الفيديو بنجاح! جاهز للبث.**")

if __name__ == "__main__":
    print("🚀 البوت يعمل الآن بكفاءة...")
    bot.run()
