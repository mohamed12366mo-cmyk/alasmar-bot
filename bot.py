import logging
import random
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    filters
)

# إعدادات التسجيل لمتابعة التشغيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# قاموس لتسجيل تحذيرات الأعضاء مؤقتاً
warnings_dict = {}

# 1. نظام الحماية وحذف الروابط والتحذير التلقائي
async def protect_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if message and message.text:
        # التحقق مما إذا كانت الرسالة تحتوى على روابط
        if "http://" in message.text or "https://" in message.text or "t.me/" in message.text:
            try:
                # حذف رسالة الرابط فوراً
                await message.delete()
                
                user_id = message.from_user.id
                user_name = message.from_user.first_name
                chat_id = message.chat_id
                
                # تهيئة عداد التحذيرات للعضو إذا لم يكن موجوداً
                if user_id not in warnings_dict:
                    warnings_dict[user_id] = 0
                
                warnings_dict[user_id] += 1
                current_warnings = warnings_dict[user_id]
                
                if current_warnings < 3:
                    # إرسال تحذير
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=f"⚠️ العضو {user_name}\nممنوع إرسال الروابط في هذه المجموعة!\nالتحذير ({current_warnings}/3)."
                    )
                else:
                    # الحظر التلقائي بعد الوصول لـ 3 تحذيرات
                    await context.bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=f"🚫 تم حظر العضو {user_name} لتجاوزه الحد الأقصى من التحذيرات (3 تحذيرات بسبب نشر الروابط)."
                    )
                    warnings_dict[user_id] = 0 # إعادة التعيين
            except Exception as e:
                print(f"خطأ في نظام الحماية: {e}")

# 2. أمر الترحيب بالأعضاء الجدد
async def welcome_new_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        welcome_text = (
            f"مرحباً بك يا {member.Al_Asmar Realm 🫅🏾 🫶🏾 ( عالم ـ الأسمر ) 🫶🏾} في مجموعتنا! 💜\n"
            f"أنا بوت **الأسمر** حارس المجموعة، سعداء بوجودك معنا.\n"
            f"يرجى الالتزام بالقوانين وعدم نشر الروابط حفاظاً على أمان الجميع."
        )
        await update.message.reply_text(welcome_text)

# 3. أمر هل تعلم (المعدل برمجياً إلى info)
async def did_you_know(update: Update, context: ContextTypes.DEFAULT_TYPE):
    facts = [
        "هل تعلم أن العسل لا يُفسد أبداً ويمكن أن يبقى صالحاً لآلاف السنين؟",
        "هل تعلم أن الدماغ البشري يستهلك نحو 20% من طاقة الجسم؟",
        "هل تعلم أن الحيتان الزرقاء هي أكبر الحيوانات على وجه الأرض؟",
        "هل تعلم أن الماء النقي لا يوصل التيار الكهربائي بمفرده؟",
        "هل تعلم أن القراءة لمدة 6 دقائق يومياً تقلل من مستويات التوتر بنسبة كبيرة؟"
    ]
    chosen_fact = random.choice(facts)
    await update.message.reply_text(f"💡 **هل تعلم:**\n{chosen_fact}")

# 4. أمر الطقس التجريبي (المعدل برمجياً إلى weather)
async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌤️ حالة الطقس اليوم: الجو لطيف ومستقر، نتمنى لك يوماً جميلاً وموفقاً!")

# 5. أمر المساعدة والأوامر المتاحة (المعدل برمجياً إلى help)
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🤖 **أهلاً بك في قائمة أوامر بوت الأسمر:**\n\n"
        "• `/info` - لعرض معلومة شيقة (هل تعلم).\n"
        "• `/weather` - لمعرفة حالة الطقس.\n"
        "• `/help` - لعرض قائمة الأوامر هذه.\n\n"
        "🛡️ **نظام الحماية:**\n"
        "البوت يحذف الروابط تلقائياً ويقوم بتحذير العضو (3 تحذيرات ثم الحظر التلقائي)."
    )
    await update.message.reply_text(help_text)

def main():
    # استبدل YOUR_BOT_TOKEN بالتوكن الحقيقي الخاص بك من BotFather
    TOKEN ="129409995:AAGHqE73pkrvxpNGhIrW6qmePD_MzWI5i2I""
    application = ApplicationBuilder().token(TOKEN).build()

    # ربط الوظائف والأوامر
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("info", did_you_know))
    application.add_handler(CommandHandler("weather", weather_command))
    
    # رصد الأعضاء الجدد للترحيب
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_members))
    # رصد جميع الرسائل لتفعيل نظام حماية الروابط
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), protect_group))

    print("🤖 بوت الأسمر يعمل الآن بنجاح...")
    application.run_polling()

if __name__ == '__main__':
    main()
