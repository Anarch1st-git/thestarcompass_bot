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


# # Функция для команды /start
# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     context.user_data.clear()
#     context.chat_data.clear()
#     chat_id = update.message.from_user.id
#     user = update.message.from_user
#     username = "user" if user.username is None else user.username

#     new_user = create_user(chat_id, username)

#     if new_user:
#         keyboard = [
#             [
#                 InlineKeyboardButton("Пользовательское соглашение", url='https://thestarcompass.ru/agreement.html'),
#             ],
#             [
#                 InlineKeyboardButton("Политика конфиденциальности", url='https://thestarcompass.ru/policy.html'),
#             ],
#             [
#                 InlineKeyboardButton("Подтверждаю", callback_data='btn_inl_confirm_agreement')
#             ]
#         ]
#         reply_markup = InlineKeyboardMarkup(keyboard)
#         agreement_text = f"<b>Добро пожаловать в астрологического бота Звёздный компас | Астро."

#         await update.message.reply_text(
#             text=agreement_text,
#             reply_markup=reply_markup,
#             parse_mode='HTML'
#         )
#         save_log_event(chat_id, f"create new user")
#     else:
#         reply_keyboard = [
#             #["Профиль"],
#             ["Астрологический расчёт"],
#             ["Поддержка"]
#         ]
#         reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
        
#         await update.message.reply_text(
#             text=f"С возвращением в астрологического бота Звёздный компас | Астро. Вы можете выбрать действие ниже:",
#             reply_markup=reply_markup
#         )
#         save_log_event(chat_id, f"return user after /start")
#     return ConversationHandler.END
# Функция для команды /start
# Функция для команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.chat_data.clear()
    chat_id = update.message.from_user.id
    user = update.message.from_user
    username = "user" if user.username is None else user.username

    new_user = create_user(chat_id, username)

    # Инлайн-кнопки для расчётов (прикрепляются к сообщению)
    inline_buttons = [
        [InlineKeyboardButton("🪐 Натальная карта", callback_data="start_input_natalchart")],
        [InlineKeyboardButton("🌌 Транзит", callback_data="start_input_transit")],
        [InlineKeyboardButton("💞 Синастрия", callback_data="start_input_synastry")]
    ]
    inline_markup = InlineKeyboardMarkup(inline_buttons)

    # Кнопки в основном меню (отображаются внизу экрана)
    reply_keyboard = [
        ["🔮 Астрологический расчёт"],
        ["📞 Поддержка"]
    ]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

    # Сообщение с inline-кнопками
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

    # Дополнительно отправляем пустое сообщение, чтобы обновить клавиатуру меню
    await update.message.reply_text(
        text="Вы можете выбрать действие в меню ниже:",
        reply_markup=reply_markup
    )

    save_log_event(chat_id, "user started the bot")
    return ConversationHandler.END


# # Обработка нажатия кнопки btn_inl_confirm_agreement
# async def confirm_agreement(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     query = update.callback_query
#     chat_id = query.message.chat_id

#     # Удаляем сообщение с соглашением
#     await query.message.delete()

#     # Добавляем новые кнопки в ReplyKeyboardMarkup
#     reply_keyboard = [
#         #["Профиль"],
#         ["Астрологический расчёт"],
#         ["Поддержка"]
#     ]
#     reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

#     # Отправляем обновлённое меню
#     await query.message.reply_text(
#         "Соглашение принято. Выберите действие:",
#         reply_markup=reply_markup
#     )

#     context.bot_data.setdefault("menu_commands", {})
#     context.bot_data["menu_commands"][chat_id] = "/agreement"
#     context.bot_data["menu_commands"][chat_id] = "/policy"

#     await query.answer()
#     save_log_event(chat_id, f"user confirm agreement")