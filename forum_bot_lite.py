from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
import os

TOKEN = os.getenv("TOKEN")
CHANNELS = ["@top_mods_1", "@soft_na_grand", "@GMP_Rynok"]
LANGUAGES = {}

def start(update: Update, context):
    user_id = update.effective_user.id
    buttons = [[InlineKeyboardButton("🔄 Проверить подписку", callback_data="check_sub")]]
    text = (
        "👋 Привет!\n\n"
        "Чтобы продолжить, подпишитесь на следующие каналы:\n\n"
        "📢 @top_mods_1\n"
        "👥 @soft_na_grand\n"
        "👥 @GMP_Rynok\n\n"
        "После этого нажмите кнопку ниже 👇"
    )
    update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

def check_subscription(update: Update, context):
    query = update.callback_query
    user_id = query.from_user.id
    bot = context.bot
    not_subscribed = []

    for ch in CHANNELS:
        try:
            member = bot.get_chat_member(ch, user_id)
            if member.status in ["left", "kicked"]:
                not_subscribed.append(ch)
        except:
            not_subscribed.append(ch)

    if not_subscribed:
        query.edit_message_text(
            "❌ Вы не подписались на все каналы.\nПожалуйста, подпишитесь:\n" +
            "\n".join(not_subscribed)
        )
    else:
        LANGUAGES[user_id] = "ru"
        buttons = [
            [InlineKeyboardButton("📝 Создать тему", callback_data="create_topic")],
            [InlineKeyboardButton("📞 Связаться с админом", url="https://t.me/rude_lxz")]
        ]
        query.edit_message_text("✅ Спасибо за подписку!\nВыберите действие:", reply_markup=InlineKeyboardMarkup(buttons))

def button_handler(update: Update, context):
    query = update.callback_query
    if query.data == "check_sub":
        check_subscription(update, context)
    elif query.data == "create_topic":
        query.message.reply_text("ℹ️ Добавьте бота в группу и дайте права администратора. Напишите сюда название группы.")
        context.user_data["step"] = "awaiting_group"

def message_handler(update: Update, context):
    user_id = update.effective_user.id
    step = context.user_data.get("step")

    if step == "awaiting_group":
        context.user_data["group"] = update.message.text
        context.user_data["step"] = "awaiting_count"
        update.message.reply_text("🧮 Сколько тем создать? (макс. 50)")
    elif step == "awaiting_count":
        try:
            count = int(update.message.text)
            if count > 50 or count <= 0:
                raise ValueError
            context.user_data["count"] = count
            context.user_data["topics"] = []
            context.user_data["step"] = "collecting_topics"
            update.message.reply_text(f"✍️ Введите названия тем ({count}):")
        except:
            update.message.reply_text("❗ Введите корректное число от 1 до 50.")
    elif step == "collecting_topics":
        context.user_data["topics"].append(update.message.text)
        if len(context.user_data["topics"]) == context.user_data["count"]:
            group = context.user_data["group"]
            topics = context.user_data["topics"]
            for topic in topics:
                try:
                    context.bot.create_forum_topic(chat_id=group, name=topic)
                except Exception as e:
                    update.message.reply_text(f"⚠️ Ошибка при создании темы '{topic}': {e}")
            update.message.reply_text("✅ Все темы успешно созданы!")
            context.user_data.clear()
        else:
            left = context.user_data["count"] - len(context.user_data["topics"])
            update.message.reply_text(f"📝 Осталось ввести тем: {left}")

updater = Updater(token=TOKEN, use_context=True)
dp = updater.dispatcher
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CallbackQueryHandler(button_handler))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))

updater.start_polling()
print("Bot started")
updater.idle()
