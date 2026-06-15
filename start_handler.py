from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import ContextTypes, ConversationHandler
from handlers import (
    create_user,
    save_log_event
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.chat_data.clear()
    chat_id = update.message.from_user.id
    user = update.message.from_user
    username = "user" if user.username is None else user.username

    new_user = create_user(chat_id, username)

                                                            
    inline_buttons = [
        [InlineKeyboardButton("🪐 Натальная карта", callback_data="start_input_natalchart")],
        [InlineKeyboardButton("🌌 Транзит", callback_data="start_input_transit")],
        [InlineKeyboardButton("💞 Синастрия", callback_data="start_input_synastry")]
    ]
    inline_markup = InlineKeyboardMarkup(inline_buttons)

                                                        
    reply_keyboard = [
        ["🔮 Астрологический расчёт"],
        ["📞 Поддержка"]
    ]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

                                 
    await update.message.reply_text(
        text=(
            "🔮 <b>Астрологический расчёт карт</b>\n"
            "Создавайте уникальные карты для себя и близких!\n\n"
            "- 🪐 <b>Натальная карта:</b> откройте тайны своего рождения.\n"
            "- 🌌 <b>Транзиты:</b> следите за влиянием звёзд в настоящем и будущем.\n"
            "- 💞 <b>Синастрия:</b> узнайте секреты совместимости с другими.\n\n"
            "Выберите тип расчёта:"
        ),
        reply_markup=inline_markup,
        parse_mode='HTML'
    )

                                                                               
    await update.message.reply_text(
        text="Вы можете выбрать действие в меню ниже:",
        reply_markup=reply_markup
    )

    save_log_event(chat_id, "user started the bot")
    return ConversationHandler.END
