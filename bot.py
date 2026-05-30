from configs import (
    TOKEN_BOT,
    ERROR_MESSAGE_NOT_USER
)
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application,
    filters,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    PreCheckoutQueryHandler
)
from handlers import (
    get_user_by_chat_id,
    create_payment_and_get_link,
    save_log_event,
    load_natal
)
from natal_handler import (
    conv_handler_natalchart
)
from synastry_handler import (
    conv_handler_synastry
)
from transit_handler import (
    conv_handler_transit
)
from keyboards import (
    m_generation_keyboard,
    payment_link_keyboard
)
from start_handler import (
    start,
    #confirm_agreement
)
import json
from astrocalc import (
    lunar_phase_translate,
    planet_translate,
    astro_translate,
    sign_translate,
    house_translate,
    format_pretty_report,
    get_lunar_phase_description
)
from ukassa_handler import (
    buy_subscription,
    ukassa_pay_handler,
    pre_checkout
)


# Обработчик кнопки "Профиль"
# async def handle_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     chat_id = update.message.chat_id
#     user = get_user_by_chat_id(chat_id)

#     if not user:
#         await update.message.reply_text(ERROR_MESSAGE_NOT_USER)
#         return
    
#     username = user.username
#     # email = user.email
#     # phone = user.phone
#     sub_status = user.subscription_active

#     # Начало сообщения
#     profile_text = (
#         f"🌟 <b>Ваш профиль</b>\n\n"
#         f"- 👤 <b>Имя:</b> {username}\n"
#     )

#     keyboard = []

#     # if email:
#     #     profile_text += f"- 📧 <b>Email:</b> {email}\n"
#     # else:
#     #     profile_text += "- 📧 <b>Email:</b> отсутствует\n"
    
#     # if phone:
#     #     profile_text += f"- 📱 <b>Телефон:</b> {phone}\n"
#     # else:
#     #     profile_text += "- 📱 <b>Телефон:</b> отсутствует\n"

#     # # Проверка, нужно ли требовать ввод email или телефона
#     # if not email and not phone:
#     #     profile_text += "\n⚠️ <i>Для оплаты подписки нужен ваш email или телефон, на который поступит чек.</i>\n"
#     #     keyboard.append([InlineKeyboardButton("📧 Ввести email", callback_data='btn_inl_enter_email')])
#     #     keyboard.append([InlineKeyboardButton("📱 Ввести телефон", callback_data='btn_inl_enter_phone')])
#     # else:
#     #     keyboard.append([InlineKeyboardButton("✏ Изменить email или телефон", callback_data='btn_inl_edit_contact')])

#     # Информация о подписке
#     if sub_status:
#         tarif_end = user.subscription_end.strftime("%d-%m-%Y %H:%M")
#         profile_text += f"- 🔑 <b>Подписка:</b> активна\n  Действует до: <b>{tarif_end}</b>\n"
#     else:
#         profile_text += "- 🔑 <b>Подписка:</b> неактивна\nПодписка оформляется на 30 дней. Сейчас действует скидка: вместо <s>1490</s> руб, всего <b>990</b> руб.\n"
#         keyboard.append([InlineKeyboardButton("🛒 Оформить подписку", callback_data='buy_subscription')])

#     # Итоговое сообщение
#     profile_text += "\n✨ Управляйте своим астрологическим опытом!"

#     reply_markup = InlineKeyboardMarkup(keyboard)
#     await update.message.reply_text(
#         text=profile_text,
#         reply_markup=reply_markup,
#         parse_mode='HTML'
#     )
#     save_log_event(chat_id, "user press profile button")


# async def handle_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     #chat_id = update.message.chat_id
#     #text = update.message.text

#     if context.user_data.get("awaiting_email"):
#         await handle_email_input(update, context)
#         return
#     elif context.user_data.get("awaiting_phone"):
#         await handle_phone_input(update, context)
#         return
#     else:
#         await update.message.reply_text("Команда не распознана. Попробуйте снова.")


# Обработка кнопки ввести email
# async def btn_inl_enter_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     query = update.callback_query
#     chat_id = query.message.chat_id

#     user = get_user_by_chat_id(chat_id)

#     if not user:
#         await update.edit_message_text(ERROR_MESSAGE_NOT_USER)
#         return

#     email = user.email

#     if email:
#         await query.edit_message_text(
#             "Вы уже ввели email."
#         )
#         return

#     await query.edit_message_text(
#         "Пожалуйста, отправьте ваш email сообщением."
#     )

#     context.user_data["awaiting_email"] = True
#     save_log_event(chat_id, f"user press inline-button <btn_inl_enter_email>")
#     return


# Обработчик текстовых сообщений для ввода email
# async def handle_email_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     chat_id = update.message.chat_id

#     # Проверяем, ожидается ли ввод email
#     if context.user_data.get("awaiting_email"):
#         email = update.message.text

#         if "@" not in email or "." not in email:
#             await update.message.reply_text("Введите корректный email.")
#             return

#         # Обновляем email пользователя в базе данных
#         user = get_user_by_chat_id(chat_id)
#         if user:
#             user.email = email
#             user.save()

#             # Убираем флаг ожидания email
#             context.user_data["awaiting_email"] = False

#             keyboard = []
#             keyboard.append([InlineKeyboardButton("Оформить подписку", callback_data='btn_inl_subscribe_full')])
#             reply_markup = InlineKeyboardMarkup(keyboard)

#             await update.message.reply_text(
#                 text=f"Ваш email успешно сохранён: {email}\n",
#                 reply_markup=reply_markup,
#                 parse_mode='HTML'
#             )
#         else:
#             await update.message.reply_text(ERROR_MESSAGE_NOT_USER)
#         save_log_event(chat_id, f"system receive email from user message")
#     else:
#         await update.message.reply_text("Команда не распознана. Попробуйте снова.")
#         save_log_event(chat_id, f"error receive email from user message")
#     return


# # Обработка кнопки "Ввести телефон"
# async def btn_inl_enter_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     query = update.callback_query
#     chat_id = query.message.chat_id

#     user = get_user_by_chat_id(chat_id)

#     if not user:
#         await update.edit_message_text(ERROR_MESSAGE_NOT_USER)
#         return

#     phone = user.phone

#     if phone:
#         await query.edit_message_text("Вы уже ввели телефон.")
#         return

#     await query.edit_message_text("Пожалуйста, отправьте ваш номер телефона сообщением (пример: +79991234567).")
#     context.user_data["awaiting_phone"] = True
#     save_log_event(chat_id, "user press inline-button <btn_inl_enter_phone>")


# # Обработчик текстовых сообщений для ввода телефона
# async def handle_phone_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     chat_id = update.message.chat_id

#     if context.user_data.get("awaiting_phone"):
#         phone = update.message.text

#         if not phone.startswith("+") or not phone[1:].isdigit() or len(phone) < 10:
#             await update.message.reply_text("Введите корректный номер телефона (пример: +79991234567).")
#             return

#         user = get_user_by_chat_id(chat_id)
#         if user:
#             user.phone = phone
#             user.save()

#             context.user_data["awaiting_phone"] = False

#             keyboard = [[InlineKeyboardButton("Оформить подписку", callback_data='btn_inl_subscribe_full')]]
#             reply_markup = InlineKeyboardMarkup(keyboard)

#             await update.message.reply_text(
#                 text=f"Ваш телефон успешно сохранён: {phone}\n",
#                 reply_markup=reply_markup,
#                 parse_mode='HTML'
#             )
#         else:
#             await update.message.reply_text(ERROR_MESSAGE_NOT_USER)

#         save_log_event(chat_id, "system receive phone from user message")
#     else:
#         await update.message.reply_text("Команда не распознана. Попробуйте снова.")
#         save_log_event(chat_id, "error receive phone from user message")
#     return


# # Обработка кнопки "Изменить email или телефон"
# async def btn_inl_edit_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     query = update.callback_query
#     chat_id = query.message.chat_id

#     user = get_user_by_chat_id(chat_id)

#     if not user:
#         await query.edit_message_text(ERROR_MESSAGE_NOT_USER)
#         return

#     keyboard = []
#     if user.email:
#         keyboard.append([InlineKeyboardButton("❌ Удалить email", callback_data='btn_inl_delete_email')])

#     if user.phone:
#         keyboard.append([InlineKeyboardButton("❌ Удалить телефон", callback_data='btn_inl_delete_phone')])

#     keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data='btn_inl_back_to_profile')])
#     reply_markup = InlineKeyboardMarkup(keyboard)

#     await query.edit_message_text(
#         "Выберите действие:",
#         reply_markup=reply_markup
#     )
#     save_log_event(chat_id, "user press inline-button <btn_inl_edit_contact>")


# # Удаление email
# async def btn_inl_delete_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     query = update.callback_query
#     chat_id = query.message.chat_id

#     user = get_user_by_chat_id(chat_id)
#     if user and user.email:
#         user.email = None
#         user.save()
#         await query.edit_message_text("📧 Ваш email удалён.")
#         save_log_event(chat_id, "user delete email")
#     else:
#         await query.edit_message_text("У вас нет сохранённого email.")

# # Удаление телефона
# async def btn_inl_delete_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     query = update.callback_query
#     chat_id = query.message.chat_id

#     user = get_user_by_chat_id(chat_id)
#     if user and user.phone:
#         user.phone = None
#         user.save()
#         await query.edit_message_text("📱 Ваш телефон удалён.")
#         save_log_event(chat_id, "user delete phone")
#     else:
#         await query.edit_message_text("У вас нет сохранённого телефона.")


# Обработчик кнопки "Назад в профиль"
# async def back_to_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     query = update.callback_query
#     chat_id = query.message.chat_id

#     user = get_user_by_chat_id(chat_id)

#     if not user:
#         await update.message.reply_text(ERROR_MESSAGE_NOT_USER)
#         return
    
#     username = user.username
#     email = user.email
#     phone = user.phone
#     sub_status = user.subscription_active

#     # Начало сообщения
#     profile_text = (
#         f"🌟 <b>Ваш профиль</b>\n\n"
#         f"- 👤 <b>Имя:</b> {username}\n"
#     )

#     keyboard = []

#     # if email:
#     #     profile_text += f"- 📧 <b>Email:</b> {email}\n"
#     # else:
#     #     profile_text += "- 📧 <b>Email:</b> отсутствует\n"
    
#     # if phone:
#     #     profile_text += f"- 📱 <b>Телефон:</b> {phone}\n"
#     # else:
#     #     profile_text += "- 📱 <b>Телефон:</b> отсутствует\n"

#     # # Проверка, нужно ли требовать ввод email или телефона
#     # if not email and not phone:
#     #     profile_text += "\n⚠️ <i>Для оплаты подписки нужен ваш email или телефон, на который поступит чек.</i>\n"
#     #     keyboard.append([InlineKeyboardButton("📧 Ввести email", callback_data='btn_inl_enter_email')])
#     #     keyboard.append([InlineKeyboardButton("📱 Ввести телефон", callback_data='btn_inl_enter_phone')])
#     # else:
#     #     keyboard.append([InlineKeyboardButton("✏ Изменить email или телефон", callback_data='btn_inl_edit_contact')])

#     # Информация о подписке
#     if sub_status:
#         tarif_end = user.subscription_end.strftime("%d-%m-%Y %H:%M")
#         profile_text += f"- 🔑 <b>Подписка:</b> активна\n  Действует до: <b>{tarif_end}</b>\n"
#     else:
#         profile_text += "- 🔑 <b>Подписка:</b> неактивна\nПодписка оформляется на 30 дней. Сейчас действует скидка: вместо <s>1490</s> руб, всего <b>990</b> руб.\n"
#         keyboard.append([InlineKeyboardButton("🛒 Оформить подписку", callback_data='buy_subscription')])

#     # Итоговое сообщение
#     profile_text += "\n✨ Управляйте своим астрологическим опытом!"

#     reply_markup = InlineKeyboardMarkup(keyboard)
#     await query.edit_message_text(
#         text=profile_text,
#         reply_markup=reply_markup,
#         parse_mode='HTML'
#     )
#     save_log_event(chat_id, "user press profile button")


# Обработчик кнопки "Генерация"
async def m_generation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    user = get_user_by_chat_id(chat_id)

    if not user:
        await update.message.reply_text(ERROR_MESSAGE_NOT_USER)
        return
    
    keyboard = m_generation_keyboard()
    
    # Сообщение
    generation_text = (
        "🔮 <b>Астрологический расчёт карт</b>\n"
        "Создавайте уникальные карты для себя и близких!\n\n"
        "- 🪐 <b>Натальная карта:</b> откройте тайны своего рождения.\n"
        "- 🌌 <b>Транзиты:</b> следите за влиянием звёзд в настоящем и будущем.\n"
        "- 💞 <b>Синастрия:</b> узнайте секреты совместимости с другими.\n\n"
    )
    
    # if not user.subscription_active:
    #     generation_text += "✨ При оформлении подписки вы получите неограниченное количество астрологических расчётов, а так же расширенные трактовки. Чтобы оформить подписку, перейдите в Профиль, по кнопке в меню."
    #     keyboard.append([InlineKeyboardButton("🛒 Оформить подписку", callback_data='buy_subscription')])

    reply_markup = InlineKeyboardMarkup(keyboard)

    send_message = await update.message.reply_text(
        text=generation_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

    context.user_data['chat_id'] = update.message.chat_id
    context.user_data['message_id_m_generation'] = send_message.message_id

    save_log_event(chat_id, f"user press keyboard-button <m_generation>")


# Обработчик кнопки клавиатуры Поддержка
async def m_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.from_user.id
    await update.message.reply_text(
        text="Техническая поддержка доступна по адресу почты: <b>support@thestarcompass.ru</b>",
        parse_mode="HTML"
    )
    save_log_event(chat_id, f"user press keyboard-button <m_support>")


# Хендлер для команды /agreement
async def agreement(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.from_user.id
    await update.message.reply_text("Вы можете ознакомиться с пользовательским соглашением по ссылке: https://thestarcompass.ru/agreement.html")
    save_log_event(chat_id, f"user enter command /agreement")


# Хендлер для команды /policy
async def policy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.from_user.id
    await update.message.reply_text("Вы можете ознакомиться с политикой конфиденциальности по ссылке: https://thestarcompass.ru/policy.html")
    save_log_event(chat_id, f"user enter command /policy")


# Обработчик возврата в меню "Генерация"
async def back_to_generation_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = query.from_user.id

    user = get_user_by_chat_id(chat_id)

    if not user:
        await update.message.reply_text(ERROR_MESSAGE_NOT_USER)
        return
    
    keyboard = m_generation_keyboard()

    # Сообщение
    generation_text = (
        "🔮 <b>Астрологический расчёт карт</b>\n"
        "Создавайте уникальные карты для себя и близких!\n\n"
        "- 🪐 <b>Натальная карта:</b> откройте тайны своего рождения.\n"
        "- 🌌 <b>Транзиты:</b> следите за влиянием звёзд в настоящем и будущем.\n"
        "- 💞 <b>Синастрия:</b> узнайте секреты совместимости с другими.\n\n"
    )
    
    # if not user.subscription_active:
    #     generation_text += "✨ При оформлении подписки вы получите неограниченное количество астрологических расчётов, а так же расширенные трактовки. Чтобы оформить подписку, перейдите в Профиль, по кнопке в меню."
    #     keyboard.append([InlineKeyboardButton("🛒 Оформить подписку", callback_data='buy_subscription')])

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Возвращаем пользователя в главное меню генерации
    await query.edit_message_text(
        text=generation_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )
    save_log_event(chat_id, f"user press inline-button <back_to_generation_menu>")
    return ConversationHandler.END


# Обработчик кнопки получить подписку
# async def btn_inl_subscribe_full(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     query = update.callback_query
#     await query.answer()

#     chat_id = query.message.chat_id
#     user = get_user_by_chat_id(chat_id)

#     if not user:
#         await query.edit_message_text(ERROR_MESSAGE_NOT_USER)
#         return

#     payment_link = create_payment_and_get_link(chat_id, 990)

#     await query.edit_message_text(
#         text="Ваша ссылка на оплату успешно сформирована. Нажмите на кнопку Оплатить, чтобы перейти на страницу оплаты.",
#         reply_markup=payment_link_keyboard(payment_link),
#         parse_mode='HTML'
#     )
#     save_log_event(chat_id, f"user press inline-button <btn_inl_subscribe_full>")


# Обработчик кнопки Карта
# async def graphic(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     query = update.callback_query
#     await query.answer()

#     chat_id = query.message.chat_id
#     user = get_user_by_chat_id(chat_id)

#     if not user:
#         await query.edit_message_text(ERROR_MESSAGE_NOT_USER)
#         return
    
#     natal = load_natal(chat_id)
#     if natal is None:
#         keyboard = [
#             [{"text": "✨ Натальная карта", "callback_data": "start_input_natalchart"}]
#         ]
#         reply_markup = InlineKeyboardMarkup(keyboard)

#         await update.message.reply_text(
#             text="У вас нет созданной натальной карты. Создайте натальную карту по кнопке ниже:",
#             reply_markup=reply_markup,
#             parse_mode='HTML'
#         )
#         return
    
#     keyboard = [[InlineKeyboardButton("Назад", callback_data="back_natalchart_message")]]
#     reply_markup = InlineKeyboardMarkup(keyboard)

#     graphic_png = natal.graphic # картинка в бинарном формате

#     if graphic_png:
#         await query.edit_message_text(
#             text="График натальной карты:",
#             reply_markup=reply_markup
#         )
#         await query.message.reply_photo(photo=graphic_png, reply_markup=reply_markup)
#     else:
#         await query.edit_message_text("Ошибка: изображение не найдено", reply_markup=reply_markup)


# Обработчик кнопки Планеты
# Обработчик кнопки Планеты
async def planets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat_id
    user = get_user_by_chat_id(chat_id)

    if not user:
        await query.edit_message_text(ERROR_MESSAGE_NOT_USER)
        return
    
    natal = load_natal(chat_id)
    if natal is None:
        keyboard = [[InlineKeyboardButton("✨ Натальная карта", callback_data="start_input_natalchart")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text="У вас нет созданной натальной карты. Создайте натальную карту по кнопке ниже:",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        return
    
    report = json.loads(natal.report)
    planets_list = list(report["planets"].items())  # Преобразуем в список для среза

    #subscription = user.subscription_active  # Проверяем подписку
    #max_planets = len(planets_list) if subscription else 4  # Лимит для без подписки

    planets_info = "\n\n".join([
        f"{planet_translate.get(name, name)}: {astro_translate.get(planet['quality'], planet['quality'])}, "
        f"{astro_translate.get(planet['element'], planet['element'])}, "
        f"{sign_translate.get(planet['sign'], planet['sign'])}, "
        f"{house_translate.get(planet['house'], planet['house'])} "
        f"{astro_translate['Retrograde'] if planet['retrograde'] else astro_translate['Direct']} "
        f"({round(planet['degree'], 2)}°)"
        for name, planet in planets_list #[:max_planets]  # Ограничиваем список
    ])

    keyboard = [[InlineKeyboardButton("Назад", callback_data="back_natalchart_message")]]

    # if not subscription:  # Если нет подписки, добавляем кнопку "Дополнительно"
    #     keyboard.insert(0, [InlineKeyboardButton("🔒 Дополнительно", callback_data="buy_subscription")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text=planets_info,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


# Обработчик кнопки Дома
async def houses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat_id
    user = get_user_by_chat_id(chat_id)

    if not user:
        await query.edit_message_text(ERROR_MESSAGE_NOT_USER)
        return
    
    natal = load_natal(chat_id)
    if natal is None:
        keyboard = [[InlineKeyboardButton("✨ Натальная карта", callback_data="start_input_natalchart")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text="У вас нет созданной натальной карты. Создайте натальную карту по кнопке ниже:",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        return
    
    report = json.loads(natal.report)
    houses_list = list(report["houses"].items())  # Преобразуем в список для ограничения

    #subscription = user.subscription_active  # Проверяем подписку
    #max_houses = len(houses_list) if subscription else 4  # Лимит для без подписки

    houses_info = "\n\n".join([
        f"{house_translate.get(name, name)}: {astro_translate.get(house['quality'], house['quality'])}, "
        f"{astro_translate.get(house['element'], house['element'])}, "
        f"{sign_translate.get(house['sign'], house['sign'])} "
        f"({round(house['degree'], 2)}°)"
        for name, house in houses_list #[:max_houses]  # Ограничиваем список
    ])

    keyboard = [[InlineKeyboardButton("Назад", callback_data="back_natalchart_message")]]

    # if not subscription:  # Если нет подписки, добавляем кнопку "Дополнительно"
    #     keyboard.insert(0, [InlineKeyboardButton("🔒 Дополнительно", callback_data="buy_subscription")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text=houses_info,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


# Обработчик кнопки Фаза луны
async def lunar_phase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat_id
    user = get_user_by_chat_id(chat_id)

    if not user:
        await query.edit_message_text(ERROR_MESSAGE_NOT_USER)
        return
    
    natal = load_natal(chat_id)
    if natal is None:
        keyboard = [[InlineKeyboardButton("✨ Натальная карта", callback_data="start_input_natalchart")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text="У вас нет созданной натальной карты. Создайте натальную карту по кнопке ниже:",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        return
    
    # Проверяем подписку
    # if not user.subscription_active:
    #     keyboard = [[InlineKeyboardButton("🔒 Открыть доступ", callback_data="buy_subscription")]]
    #     reply_markup = InlineKeyboardMarkup(keyboard)

    #     await query.edit_message_text(
    #         text="🔒 Доступ к информации о лунной фазе доступен только для подписчиков.",
    #         reply_markup=reply_markup,
    #         parse_mode='HTML'
    #     )
    #     return

    # Если подписка есть, показываем лунную фазу
    report = json.loads(natal.report)
    lunar = report["lunar_phase"]

    lunar_text = (
        f"{lunar['emoji']} <b>{lunar_phase_translate.get(lunar['name'], lunar['name'])}</b>\n\n"
        f"🔄 Угол между Солнцем и Луной: {round(lunar['degrees_between_s_m'], 2)}°\n"
        f"🌑 Фаза Луны: {lunar['moon_phase']}\n"
        f"☀️ Фаза Солнца: {lunar['sun_phase']}\n\n"
        f"ℹ️ <b>Значение фазы Луны:</b>\n{get_lunar_phase_description(lunar['name'])}"
    )

    keyboard = [[InlineKeyboardButton("Назад", callback_data="back_natalchart_message")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text=lunar_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


# Обработчик кнопки Трактовки планеты
async def tracts_planets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat_id
    user = get_user_by_chat_id(chat_id)

    if not user:
        await query.edit_message_text(ERROR_MESSAGE_NOT_USER)
        return
    
    natal = load_natal(chat_id)
    if natal is None:
        keyboard = [[InlineKeyboardButton("✨ Натальная карта", callback_data="start_input_natalchart")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text="У вас нет созданной натальной карты. Создайте натальную карту по кнопке ниже:",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        return
    
    # Проверяем подписку
    # if not user.subscription_active:
    #     keyboard = [[InlineKeyboardButton("🔒 Открыть доступ", callback_data="buy_subscription")]]
    #     reply_markup = InlineKeyboardMarkup(keyboard)

    #     await query.edit_message_text(
    #         text="🔒 Доступ к трактовкам доступен только для подписчиков.",
    #         reply_markup=reply_markup,
    #         parse_mode='HTML'
    #     )
    #     return

    tracts = natal.tracts_planets

    keyboard = [[InlineKeyboardButton("Назад", callback_data="back_natalchart_message")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text=tracts,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


# Обработчик кнопки Трактовки дома
async def tracts_houses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat_id
    user = get_user_by_chat_id(chat_id)

    if not user:
        await query.edit_message_text(ERROR_MESSAGE_NOT_USER)
        return
    
    natal = load_natal(chat_id)
    if natal is None:
        keyboard = [[InlineKeyboardButton("✨ Натальная карта", callback_data="start_input_natalchart")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text="У вас нет созданной натальной карты. Создайте натальную карту по кнопке ниже:",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        return
    
    # Проверяем подписку
    # if not user.subscription_active:
    #     keyboard = [[InlineKeyboardButton("🔒 Открыть доступ", callback_data="buy_subscription")]]
    #     reply_markup = InlineKeyboardMarkup(keyboard)

    #     await query.edit_message_text(
    #         text="🔒 Доступ к трактовкам доступен только для подписчиков.",
    #         reply_markup=reply_markup,
    #         parse_mode='HTML'
    #     )
    #     return

    tracts = natal.tracts_houses

    keyboard = [[InlineKeyboardButton("Назад", callback_data="back_natalchart_message")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text=tracts,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


# Обработчик кнопки Назад для натальной карты
async def back_natalchart_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat_id
    user = get_user_by_chat_id(chat_id)

    if not user:
        await query.edit_message_text(ERROR_MESSAGE_NOT_USER)
        return

    natal = load_natal(chat_id)
    if natal is None:
        keyboard = [
            [{"text": "✨ Натальная карта", "callback_data": "start_input_natalchart"}]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            text="У вас нет созданной натальной карты. Создайте натальную карту по кнопке ниже:",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        return
    
    keyboard = [
            [{"text": "🪐 Планеты", "callback_data": "planets"}],
            [{"text": "🏠 Дома", "callback_data": "houses"}]
        ]

    #if user.subscription_active:
    keyboard.append([{"text": "🌙 Лунная фаза", "callback_data": "lunar_phase"}])
    keyboard.append([{"text": "📖 Трактовки (планеты)", "callback_data": "tracts_planets"}])
    keyboard.append([{"text": "📖 Трактовки (дома)", "callback_data": "tracts_houses"}])
    # else:
    #     keyboard.append([{"text": "🔒 Лунная фаза", "callback_data": "lunar_phase"}])
    #     keyboard.append([{"text": "🔒 Трактовки (планеты)", "callback_data": "tracts_planets"}])
    #     keyboard.append([{"text": "🔒 Трактовки (дома)", "callback_data": "tracts_houses"}])

    reply_markup = InlineKeyboardMarkup(keyboard)

    report = format_pretty_report(json.loads(natal.report))

    summary_text = (
            f"🌟 <b>Натальная карта</b>\n"
            f"📅 Дата: {report['natal_chart']['date']}\n"
            f"⏰ Время: {report['natal_chart']['time']}\n"
            f"📍 Город: {report['natal_chart']['city']}, {report['natal_chart']['country']}\n"
            f"⏳ Часовой пояс: {report['natal_chart']['time_zone']}\n\n"
            f"🔮 <b>Стихийный баланс:</b>\n"
            f"🔥 Огонь: {report['elements_balance']['fire']}\n"
            f"🌍 Земля: {report['elements_balance']['earth']}\n"
            f"💨 Воздух: {report['elements_balance']['air']}\n"
            f"🌊 Вода: {report['elements_balance']['water']}\n\n"
            f"🌙 <b>Лунная фаза:</b> {report['lunar_phase']['emoji']} {lunar_phase_translate.get(report['lunar_phase']['name'], report['lunar_phase']['name'])}"
        )

    await query.edit_message_text(
        text=summary_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


# @dp.callback_query_handler(lambda call: call.data in ["summary", "elements", "planets", "houses", "lunar_phase"])
# async def callback_query_handler(call: CallbackQuery):
#     chat_id = call.message.chat.id
#     user_data = get_user_data(chat_id)  # Получаем данные пользователя
#     result = format_astrology_report(user_data)

#     # Тексты для обновления сообщений
#     new_text = result.get(call.data, "Ошибка: данных нет.")

#     # Обновляем клавиатуру
#     keyboard = [
#         [{"text": "🔙 Назад", "callback_data": "back_to_main"}]
#     ]
#     reply_markup = {"inline_keyboard": keyboard}

#     await bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=new_text, reply_markup=reply_markup, parse_mode="HTML")


# @dp.callback_query_handler(lambda call: call.data in ["planets", "houses"])
# async def callback_list(call: CallbackQuery):
#     chat_id = call.message.chat.id
#     user_data = get_user_data(chat_id)  
#     result = format_astrology_report(user_data)

#     items = result.get(call.data, [])

#     # Формируем кнопки для каждой планеты/дома
#     keyboard = [[{"text": item["title"], "callback_data": f"detail_{call.data}_{i}"}] for i, item in enumerate(items)]
#     keyboard.append([{"text": "🔙 Назад", "callback_data": "back_to_main"}])

#     reply_markup = {"inline_keyboard": keyboard}

#     await bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=f"Выберите {call.data}:", reply_markup=reply_markup, parse_mode="HTML")


# @dp.callback_query_handler(lambda call: call.data.startswith("detail_"))
# async def callback_detail(call: CallbackQuery):
#     _, category, index = call.data.split("_")
#     index = int(index)
    
#     chat_id = call.message.chat.id
#     user_data = get_user_data(chat_id)
#     result = format_astrology_report(user_data)
    
#     items = result.get(category, [])
    
#     if 0 <= index < len(items):
#         item = items[index]
#         new_text = f"{item['title']}\n\n{item['details']}"

#         keyboard = [[{"text": "🔙 Назад", "callback_data": category}]]
#         reply_markup = {"inline_keyboard": keyboard}

#         await bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=new_text, reply_markup=reply_markup, parse_mode="HTML")


def main() -> None:
    application = Application.builder().token(TOKEN_BOT).connect_timeout(10).read_timeout(10).build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(ukassa_pay_handler)
    application.add_handler(conv_handler_natalchart)
    application.add_handler(conv_handler_synastry)
    application.add_handler(conv_handler_transit)

    #application.add_handler(CommandHandler("profile", handle_profile))
    #application.add_handler(CallbackQueryHandler(confirm_agreement, pattern="^btn_inl_confirm_agreement$"))
    #application.add_handler(CallbackQueryHandler(back_to_profile, pattern="^btn_inl_back_to_profile$"))
    #application.add_handler(CallbackQueryHandler(buy_subscription, pattern="^buy_subscription$"))
    #application.add_handler(MessageHandler(filters.Text("Профиль"), handle_profile))
    application.add_handler(MessageHandler(filters.Text("🔮 Астрологический расчёт"), m_generation))
    application.add_handler(MessageHandler(filters.Text("📞 Поддержка"), m_support))
    application.add_handler(CommandHandler("agreement", agreement))
    application.add_handler(CommandHandler("policy", policy))
    
    # application.add_handler(CallbackQueryHandler(btn_inl_enter_email, pattern="^btn_inl_enter_email$"))
    # application.add_handler(CallbackQueryHandler(btn_inl_enter_phone, pattern="^btn_inl_enter_phone$"))
    # application.add_handler(CallbackQueryHandler(btn_inl_edit_contact, pattern="^btn_inl_edit_contact$"))

    # application.add_handler(CallbackQueryHandler(btn_inl_delete_email, pattern="^btn_inl_delete_email$"))
    # application.add_handler(CallbackQueryHandler(btn_inl_delete_phone, pattern="^btn_inl_delete_phone$"))
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_input))

    #application.add_handler(CallbackQueryHandler(graphic, pattern="^graphic$"))
    application.add_handler(CallbackQueryHandler(planets, pattern="^planets$"))
    application.add_handler(CallbackQueryHandler(houses, pattern="^houses$"))
    application.add_handler(CallbackQueryHandler(lunar_phase, pattern="^lunar_phase$"))
    application.add_handler(CallbackQueryHandler(tracts_planets, pattern="^tracts_planets$"))
    application.add_handler(CallbackQueryHandler(tracts_houses, pattern="^tracts_houses$"))
    
    application.add_handler(CallbackQueryHandler(back_natalchart_message, pattern="^back_natalchart_message$"))

    application.add_handler(PreCheckoutQueryHandler(pre_checkout))
    
    application.run_polling(
        timeout=10,
        drop_pending_updates=True
    )

if __name__ == "__main__":
    main()