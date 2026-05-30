from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    filters,
    ContextTypes,
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler,
    MessageHandler
)
from handlers import (
    get_user_by_chat_id,
    can_generate,
    save_log_input,
    save_log_event,
    record_usage,
    get_next_available_time
)
from states_for_dialogs import (
    TRANSIT_SELECT_YEAR_FIRST,
    TRANSIT_SELECT_MONTH_FIRST,
    TRANSIT_SELECT_DAY_FIRST,
    TRANSIT_INPUT_TIME_FIRST,
    TRANSIT_INPUT_CITY_FIRST,
    TRANSIT_SELECT_YEAR_SECOND,
    TRANSIT_SELECT_MONTH_SECOND,
    TRANSIT_SELECT_DAY_SECOND,
    TRANSIT_INPUT_TIME_SECOND,
    TRANSIT_INPUT_CITY_SECOND,
    TRANSIT_CONFIRM_DATA
)
from configs import (
    ERROR_MESSAGE_NOT_USER
)
from keyboards import (
    get_years_keyboard,
    get_months_keyboard,
    get_days_keyboard
)
from utils_handler import delete_message
from validate import validate_time, find_city
from redis_worker import queue
from tasks import generate_transit


# Запрос для ввода данных для транзита
async def start_input_transit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.from_user.id
    user = get_user_by_chat_id(chat_id)

    if not user:
        await update.callback_query.edit_message_text(ERROR_MESSAGE_NOT_USER)
        save_log_event(chat_id, f"user press inline-button <start_input_transit>, but ERROR_MESSAGE_NOT_USER")
        return ConversationHandler.END
    
    # if not user.subscription_active:
    #     if not can_generate(user, "transit"):
    #         next_available_time = get_next_available_time(user, "transit")
    #         next_time_str = next_available_time.strftime("%d-%m-%Y %H:%M")

    #         await query.message.reply_text(
    #             text=(
    #                 "🚫 <b>Лимит исчерпан</b> 🚫\n\n"
    #                 "Вы исчерпали дневной лимит расчёта транзитов. 😔\n\n"
    #                 "📅 <b>Следующая доступная генерация:</b>\n"
    #                 f"🕰 <b>{next_time_str}</b>\n\n"
    #                 "🔑 <b>Хотите снять ограничения?</b>\n"
    #                 "Оформите подписку и получайте <b>неограниченный доступ</b> ко всем расчётам! 🎁\n\n"
    #                 "✨ <i>Посмотрите подписку в своём профиле.</i>"
    #             ),
    #             parse_mode='HTML'
    #         )
    #         save_log_event(chat_id, "user tried generating transit chart but limit reached")
    #         return ConversationHandler.END

    keyboard = get_years_keyboard(4)
    keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel_create_transit")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    message_text = (
        "Выберете год рождения:"
    )

    # Редактируем сообщение (меняем текст и добавляем клавиатуру)
    await query.edit_message_text(
        text=message_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

    context.user_data["transit_data_first"] = {
        "year": "2000",
        "month": "01",
        "day": "01",
        "time": "12:00",
        "city": "Москва",
        "country": "Россия"
    }

    context.user_data["transit_data_second"] = {
        "year": "2025",
        "month": "01",
        "day": "01",
        "time": "12:00",
        "city": "Москва",
        "country": "Россия"
    }

    save_log_event(chat_id, f"user press inline-button <start_input_transit>")

    return TRANSIT_SELECT_YEAR_FIRST


# Обработка выбора года
async def select_year_first(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    _, year = query.data.split("|")
    
    context.user_data["transit_data_first"]["year"] = year

    keyboard = get_months_keyboard()
    keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel_create_transit")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(
        text="Выберите месяц рождения:",
        reply_markup=reply_markup
    )

    return TRANSIT_SELECT_MONTH_FIRST


# Обработка смены страницы годов
async def change_year_first_page(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    _, page = query.data.split("|")

    keyboard = get_years_keyboard(int(page))
    keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel_create_transit")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(
        text="Выберите год рождения:",
        reply_markup=reply_markup
    )

    return TRANSIT_SELECT_YEAR_FIRST


# Обработка выбора месяца
async def select_month_first(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    _, month = query.data.split("|")

    # Добавляем ведущий ноль, если число меньше 10
    month = month.zfill(2)

    context.user_data["transit_data_first"]["month"] = month

    keyboard = get_days_keyboard(int(context.user_data["transit_data_first"]["year"]), int(month))
    keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel_create_transit")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(
        text="Выберите день рождения:",
        reply_markup=reply_markup
    )

    return TRANSIT_SELECT_DAY_FIRST


# Обработка выбора дня
async def select_day_first(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    _, day = query.data.split("|")

    # Добавляем ведущий ноль, если число меньше 10
    day = day.zfill(2)

    context.user_data["transit_data_first"]["day"] = day

    keyboard = [[InlineKeyboardButton("Отмена", callback_data="cancel_create_transit")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    sent_message = await query.message.edit_text(
        text="Введите время рождения. Пример: 14:00",
        reply_markup=reply_markup
    )

    context.user_data['chat_id'] = query.message.chat_id
    context.user_data['message_id'] = sent_message.message_id
    
    return TRANSIT_INPUT_TIME_FIRST


# Ввод времени
async def input_time_first(update: Update, context: CallbackContext) -> int:
    if 'message_id' in context.user_data and 'chat_id' in context.user_data:
        await delete_message(context, context.user_data.get('chat_id'), context.user_data.get('message_id'))
    
    chat_id = context.user_data.get('chat_id')
    time = validate_time(update.message.text)

    if not time:
        keyboard = [[InlineKeyboardButton("Отмена", callback_data="cancel_create_transit")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        sent_message = await update.message.reply_text(
            text="⌛ Время не распознано. Введите его в формате ЧЧ:ММ.",
            reply_markup=reply_markup
        )

        context.user_data['chat_id'] = context.user_data.get('chat_id')
        context.user_data['message_id'] = sent_message.message_id

        return TRANSIT_INPUT_TIME_FIRST

    context.user_data["transit_data_first"]["time"] = time

    keyboard = [[InlineKeyboardButton("Отмена", callback_data="cancel_create_transit")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    sent_message = await update.message.reply_text(
        text="Введите город рождения:",
        reply_markup=reply_markup
    )

    context.user_data['chat_id'] = chat_id
    context.user_data['message_id'] = sent_message.message_id

    return TRANSIT_INPUT_CITY_FIRST


# Ввод города
async def input_city_first(update: Update, context: CallbackContext) -> int:
    if 'message_id' in context.user_data and 'chat_id' in context.user_data:
        await delete_message(context, context.user_data.get('chat_id'), context.user_data.get('message_id'))

    chat_id = context.user_data.get('chat_id')

    city_name = update.message.text
    print(city_name)
    found_cities = find_city(city_name)
    print(found_cities)

    if not found_cities:
        keyboard = [[InlineKeyboardButton("Отмена", callback_data="cancel_create_transit")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        sent_message = await update.message.reply_text(
            text="Город не найден. Попробуйте ввести другое название.",
            reply_markup=reply_markup
        )

        context.user_data['chat_id'] = chat_id
        context.user_data['message_id'] = sent_message.message_id

        return TRANSIT_INPUT_CITY_FIRST

    # Найдено несколько городов → даем выбрать через inline-кнопки
    if len(found_cities) > 1:
        keyboard = [
            [InlineKeyboardButton(f"{city}, {country}", callback_data=f"s_c_t_1|{city}|{country}")]
            for city, country in found_cities
        ]
        keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel_create_transit")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            text="🔎 Найдено несколько городов. Выберите нужный:",
            reply_markup=reply_markup
        )
        
        return TRANSIT_INPUT_CITY_FIRST

    # Если найден только один город → продолжаем
    selected_city, selected_country = found_cities[0]

    context.user_data["transit_data_first"]["city"] = selected_city
    context.user_data["transit_data_first"]["country"] = selected_country

    keyboard = get_years_keyboard(4)
    keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel_create_transit")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    message_text = (
        "Выберете год транзита:"
    )

    sent_message = await update.message.reply_text(
        text=message_text,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

    # Сохраняем chat_id и message_id для дальнейшего использования
    context.user_data['chat_id'] = chat_id
    context.user_data['message_id'] = sent_message.message_id

    save_log_event(chat_id, f"user used <transit_select_year_second>")

    return TRANSIT_SELECT_YEAR_SECOND


# Выбор городов из подсказки
async def select_city_transit_first(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.from_user.id
    _, city, country = query.data.split("|")

    context.user_data["transit_data_first"]["city"] = city
    context.user_data["transit_data_first"]["country"] = country

    keyboard = get_years_keyboard(6, 2100)
    keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel_create_transit")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    message_text = (
        "Выберете год транзита:"
    )

    await query.message.edit_text(
        text=message_text,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

    save_log_event(chat_id, f"user select city for transit")

    return TRANSIT_SELECT_YEAR_SECOND


# Обработка выбора года
async def select_year_second(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    _, year = query.data.split("|")

    context.user_data["transit_data_second"]["year"] = year

    keyboard = get_months_keyboard()
    keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel_create_transit")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(
        text="Выберите месяц транзита:",
        reply_markup=reply_markup
    )

    return TRANSIT_SELECT_MONTH_SECOND


# Обработка смены страницы годов
async def change_year_second_page(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    _, page = query.data.split("|")

    keyboard = get_years_keyboard(int(page), 2100)
    keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel_create_transit")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(
        text="Выберите год транзита:",
        reply_markup=reply_markup
    )
    
    return TRANSIT_SELECT_YEAR_SECOND


# Обработка выбора месяца
async def select_month_second(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    _, month = query.data.split("|")

    # Добавляем ведущий ноль, если число меньше 10
    month = month.zfill(2)

    context.user_data["transit_data_second"]["month"] = month

    keyboard = get_days_keyboard(int(context.user_data["transit_data_second"]["year"]), int(month))
    keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel_create_transit")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(
        text="Выберите день транзита:",
        reply_markup=reply_markup
    )
    
    return TRANSIT_SELECT_DAY_SECOND


# Обработка выбора дня
async def select_day_second(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    _, day = query.data.split("|")

    # Добавляем ведущий ноль, если число меньше 10
    day = day.zfill(2)

    context.user_data["transit_data_second"]["day"] = day

    keyboard = [[InlineKeyboardButton("Отмена", callback_data="cancel_create_transit")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    sent_message = await query.message.edit_text(
        text="Введите время транзита. Пример: 14:00",
        reply_markup=reply_markup
    )

    context.user_data['chat_id'] = query.message.chat_id
    context.user_data['message_id'] = sent_message.message_id

    return TRANSIT_INPUT_TIME_SECOND


# Ввод времени
async def input_time_second(update: Update, context: CallbackContext) -> int:
    if 'message_id' in context.user_data and 'chat_id' in context.user_data:
        await delete_message(context, context.user_data.get('chat_id'), context.user_data.get('message_id'))

    chat_id = context.user_data.get('chat_id')
    time = validate_time(update.message.text)

    if not time:
        keyboard = [[InlineKeyboardButton("Отмена", callback_data="cancel_create_transit")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        sent_message = await update.message.reply_text(
            text="⌛ Время не распознано. Введите его в формате ЧЧ:ММ.",
            reply_markup=reply_markup
        )

        context.user_data['chat_id'] = chat_id
        context.user_data['message_id'] = sent_message.message_id

        return TRANSIT_INPUT_TIME_SECOND

    context.user_data["transit_data_second"]["time"] = time

    keyboard = [[InlineKeyboardButton("Отмена", callback_data="cancel_create_transit")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    sent_message = await update.message.reply_text(
        text="Введите город транзита:",
        reply_markup=reply_markup
    )

    context.user_data['chat_id'] = chat_id
    context.user_data['message_id'] = sent_message.message_id
    
    return TRANSIT_INPUT_CITY_SECOND


# Ввод города
async def input_city_second(update: Update, context: CallbackContext) -> int:
    if 'message_id' in context.user_data and 'chat_id' in context.user_data:
        await delete_message(context, context.user_data.get('chat_id'), context.user_data.get('message_id'))
    
    city_name = update.message.text
    found_cities = find_city(city_name)

    if not found_cities:
        keyboard = [[InlineKeyboardButton("Отмена", callback_data="cancel_create_transit")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        sent_message = await update.message.reply_text(
            text="Город не найден. Попробуйте ввести другое название.",
            reply_markup=reply_markup
        )

        context.user_data['chat_id'] = context.user_data.get('chat_id')
        context.user_data['message_id'] = sent_message.message_id

        return TRANSIT_INPUT_CITY_SECOND

    # Найдено несколько городов → даем выбрать через inline-кнопки
    if len(found_cities) > 1:
        keyboard = [
            [InlineKeyboardButton(f"{city}, {country}", callback_data=f"s_c_t_2|{city}|{country}")]
            for city, country in found_cities
        ]
        keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel_create_transit")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            text="🔎 Найдено несколько городов. Выберите нужный:",
            reply_markup=reply_markup
        )
        
        return TRANSIT_INPUT_CITY_SECOND

    # Если найден только один город → продолжаем
    selected_city, selected_country = found_cities[0]

    context.user_data["transit_data_second"]["city"] = selected_city
    context.user_data["transit_data_second"]["country"] = selected_country

    return await confirm_transit_data(update, context)


# Выбор городов из подсказки
async def select_city_transit_second(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.from_user.id
    _, city, country = query.data.split("|")

    # Обновляем данные в user_data
    context.user_data["transit_data_second"]["city"] = city
    context.user_data["transit_data_second"]["country"] = country

    save_log_event(chat_id, f"user select city for transit")

    return await confirm_transit_data(update, context)


# Подтверждение данных для генерации натальной карты
async def confirm_transit_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = None
    if update.callback_query:
        query = update.callback_query
        chat_id = query.from_user.id
    elif update.message:
        chat_id = update.message.from_user.id
    else:
        return ConversationHandler.END

    data_first = context.user_data["transit_data_first"]
    data_second = context.user_data["transit_data_second"]

    data_message = (
        f"🌟 <b>Ваши данные:</b>\n\n"
        f"<b>Страна</b>: <i>{data_first['country']}</i>\n"
        f"<b>Город</b>: <i>{data_first['city']}</i>\n"
        f"<b>Дата</b>: <i>{data_first['day']}-{data_first['month']}-{data_first['year']}</i>\n"
        f"<b>Время</b>: <i>{data_first['time']}</i>\n\n"
        f"<b>Данные для транзита</b>:\n"
        f"<b>Страна</b>: <i>{data_second['country']}</i>\n"
        f"<b>Город</b>: <i>{data_second['city']}</i>\n"
        f"<b>Дата</b>: <i>{data_second['day']}-{data_second['month']}-{data_second['year']}</i>\n"
        f"<b>Время</b>: <i>{data_second['time']}</i>\n"
    )

    keyboard = [
        [InlineKeyboardButton("✅ Подтвердить", callback_data="create_transit")],
        [InlineKeyboardButton("❌ Отменить", callback_data="cancel_create_transit")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if query:
        await query.message.edit_text(
            text=data_message,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    elif update.message:
        await update.message.reply_text(
            text=data_message,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    
    save_log_event(chat_id, f"user whaiting confirm data to create transit")

    return TRANSIT_CONFIRM_DATA


# обработка кнопки создать карту транзита
async def create_transit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_user.id
    data_first = context.user_data["transit_data_first"]
    data_second = context.user_data["transit_data_second"]
    user = get_user_by_chat_id(chat_id)
        
    if not user:
        await update.callback_query.edit_message_text("Ошибка: Пользователь не найден.")
        return ConversationHandler.END

    # Запускаем процесс создания карты
    await update.callback_query.edit_message_text(f"Ожидайте, карта создаётся.")

    record_usage(user, "transit")
    
    # Создание задачи для очереди Redis
    queue.enqueue(generate_transit, chat_id, data_first, data_second)

    context.user_data.clear()  # Очистка user_data
    context.chat_data.clear()  # Очистка chat_data

    save_log_event(chat_id, f"user press inline-button <create_transit>")
    
    return ConversationHandler.END


# Обработка нажатия на кнопку "Отменить" для транзита
async def cancel_create_transit(update: Update, context: CallbackContext):
    # Получаем объект callback (для удаления сообщения с кнопками)
    query = update.callback_query
    chat_id = query.from_user.id

    # Удаляем сообщение с кнопками
    await query.message.delete()

    context.user_data.clear()  # Очистка user_data
    context.chat_data.clear()  # Очистка chat_data

    # Уведомляем пользователя об отмене
    await query.message.reply_text(
        "Процесс создания карты транзита был отменён.",
        parse_mode="HTML"
    )

    save_log_event(chat_id, f"user press inline-button <cancel_create_transit>")

    # Завершаем диалог
    return ConversationHandler.END


conv_handler_transit = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(start_input_transit, pattern="^start_input_transit$")
    ],
    states={
        TRANSIT_SELECT_YEAR_FIRST: [
            CallbackQueryHandler(select_year_first, pattern="^select_year\|\d+$"),
            CallbackQueryHandler(change_year_first_page, pattern="^change_year_page\|[-\d]+$"),
            CallbackQueryHandler(cancel_create_transit, pattern="^cancel_create_transit$")
        ],
        TRANSIT_SELECT_MONTH_FIRST: [
            CallbackQueryHandler(select_month_first, pattern="^month\|\d+$"),
            CallbackQueryHandler(cancel_create_transit, pattern="^cancel_create_transit$")
        ],
        TRANSIT_SELECT_DAY_FIRST: [
            CallbackQueryHandler(select_day_first, pattern="^day\|\d+$"),
            CallbackQueryHandler(cancel_create_transit, pattern="^cancel_create_transit$")
        ],
        TRANSIT_INPUT_TIME_FIRST: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, input_time_first),
            CallbackQueryHandler(cancel_create_transit, pattern="^cancel_create_transit$")
        ],
        TRANSIT_INPUT_CITY_FIRST: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, input_city_first),
            CallbackQueryHandler(select_city_transit_first, pattern="^s_c_t_1\|.*$"),
            CallbackQueryHandler(cancel_create_transit, pattern="^cancel_create_transit$")
        ],
        TRANSIT_SELECT_YEAR_SECOND: [
            CallbackQueryHandler(select_year_second, pattern="^select_year\|\d+$"),
            CallbackQueryHandler(change_year_second_page, pattern="^change_year_page\|[-\d]+$"),
            CallbackQueryHandler(cancel_create_transit, pattern="^cancel_create_transit$")
        ],
        TRANSIT_SELECT_MONTH_SECOND: [
            CallbackQueryHandler(select_month_second, pattern="^month\|\d+$"),
            CallbackQueryHandler(cancel_create_transit, pattern="^cancel_create_transit$")
        ],
        TRANSIT_SELECT_DAY_SECOND: [
            CallbackQueryHandler(select_day_second, pattern="^day\|\d+$"),
            CallbackQueryHandler(cancel_create_transit, pattern="^cancel_create_transit$")
        ],
        TRANSIT_INPUT_TIME_SECOND: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, input_time_second),
            CallbackQueryHandler(cancel_create_transit, pattern="^cancel_create_transit$")
        ],
        TRANSIT_INPUT_CITY_SECOND: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, input_city_second),
            CallbackQueryHandler(select_city_transit_second, pattern="^s_c_t_2\|.*$"),
            CallbackQueryHandler(cancel_create_transit, pattern="^cancel_create_transit$")
        ],
        TRANSIT_CONFIRM_DATA: [
            CallbackQueryHandler(create_transit, pattern="^create_transit$"),
            CallbackQueryHandler(cancel_create_transit, pattern="^cancel_create_transit$")
        ]
    },
    fallbacks=[CallbackQueryHandler(cancel_create_transit, pattern="^cancel_create_transit$")],
    allow_reentry=True,
)