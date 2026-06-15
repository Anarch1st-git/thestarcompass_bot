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
    SYNASTRY_SELECT_YEAR_FIRST,
    SYNASTRY_SELECT_MONTH_FIRST,
    SYNASTRY_SELECT_DAY_FIRST,
    SYNASTRY_INPUT_TIME_FIRST,
    SYNASTRY_INPUT_CITY_FIRST,
    SYNASTRY_SELECT_YEAR_SECOND,
    SYNASTRY_SELECT_MONTH_SECOND,
    SYNASTRY_SELECT_DAY_SECOND,
    SYNASTRY_INPUT_TIME_SECOND,
    SYNASTRY_INPUT_CITY_SECOND,
    SYNASTRY_CONFIRM_DATA
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
from tasks import generate_synastry


async def start_input_synastry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.from_user.id
    user = get_user_by_chat_id(chat_id)

    if not user:
        await update.callback_query.edit_message_text(ERROR_MESSAGE_NOT_USER)
        save_log_event(chat_id, f"user press inline-button <start_input_synastry>, but ERROR_MESSAGE_NOT_USER")
        return ConversationHandler.END
    
                                      
    keyboard = get_years_keyboard(4)
    keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel_create_synastry")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    message_text = (
        "Выберете год рождения первого человека:"
    )

                                                                 
    await query.edit_message_text(
        text=message_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

    context.user_data["synastry_data_first"] = {
        "year": "2000",
        "month": "12",
        "day": "31",
        "time": "12:00",
        "city": "Москва",
        "country": "Россия"
    }

    context.user_data["synastry_data_second"] = {
        "year": "2000",
        "month": "01",
        "day": "01",
        "time": "00:00",
        "city": "Москва",
        "country": "Россия"
    }

    save_log_event(chat_id, f"user press inline-button <start_input_synastry>")

    return SYNASTRY_SELECT_YEAR_FIRST


async def select_year_first(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    _, year = query.data.split("|")

    context.user_data["synastry_data_first"]["year"] = year

    keyboard = get_months_keyboard()
    keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel_create_synastry")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(
        text="Выберите месяц рождения первого человека:",
        reply_markup=reply_markup
    )

    return SYNASTRY_SELECT_MONTH_FIRST


async def change_year_first_page(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    _, page = query.data.split("|")

    keyboard = get_years_keyboard(int(page))
    keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel_create_synastry")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(
        text="Выберете год рождения первого человека:",
        reply_markup=reply_markup
    )

    return SYNASTRY_SELECT_YEAR_FIRST


async def select_month_first(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    _, month = query.data.split("|")

                                                  
    month = month.zfill(2)

    context.user_data["synastry_data_first"]["month"] = month

    keyboard = get_days_keyboard(int(context.user_data["synastry_data_first"]["year"]), int(month))
    keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel_create_synastry")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(
        text="Выберите день рождения первого человека:",
        reply_markup=reply_markup
    )

    return SYNASTRY_SELECT_DAY_FIRST


async def select_day_first(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    _, day = query.data.split("|")

                                                  
    day = day.zfill(2)

    context.user_data["synastry_data_first"]["day"] = day

    keyboard = [[InlineKeyboardButton("Отмена", callback_data="cancel_create_synastry")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    sent_message = await query.message.edit_text(
        text="Введите время рождения первого человека. Пример: 14:00",
        reply_markup=reply_markup
    )

    context.user_data['chat_id'] = query.message.chat_id
    context.user_data['message_id'] = sent_message.message_id

    return SYNASTRY_INPUT_TIME_FIRST


async def input_time_first(update: Update, context: CallbackContext) -> int:
    if 'message_id' in context.user_data and 'chat_id' in context.user_data:
        await delete_message(context, context.user_data.get('chat_id'), context.user_data.get('message_id'))

    chat_id = context.user_data.get('chat_id')
    time = validate_time(update.message.text)

    if not time:
        keyboard = [[InlineKeyboardButton("Отмена", callback_data="cancel_create_synastry")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        sent_message = await update.message.reply_text(
            text="⌛ Время не распознано. Введите его в формате ЧЧ:ММ.",
            reply_markup=reply_markup
        )

        context.user_data['chat_id'] = context.user_data.get('chat_id')
        context.user_data['message_id'] = sent_message.message_id

        return SYNASTRY_INPUT_TIME_FIRST

    context.user_data["synastry_data_first"]["time"] = time

    keyboard = [[InlineKeyboardButton("Отмена", callback_data="cancel_create_synastry")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    sent_message = await update.message.reply_text(
        text="Введите город рождения первого человека:",
        reply_markup=reply_markup
    )

    context.user_data['chat_id'] = chat_id
    context.user_data['message_id'] = sent_message.message_id

    return SYNASTRY_INPUT_CITY_FIRST


async def input_city_first(update: Update, context: CallbackContext) -> int:
    if 'message_id' in context.user_data and 'chat_id' in context.user_data:
        await delete_message(context, context.user_data.get('chat_id'), context.user_data.get('message_id'))

    chat_id = context.user_data.get('chat_id')

    city_name = update.message.text
    found_cities = find_city(city_name)

    if not found_cities:
        keyboard = [[InlineKeyboardButton("Отмена", callback_data="cancel_create_synastry")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        sent_message = await update.message.reply_text(
            text="Город не найден. Попробуйте ввести другое название.",
            reply_markup=reply_markup
        )

        context.user_data['chat_id'] = chat_id
        context.user_data['message_id'] = sent_message.message_id

        return SYNASTRY_INPUT_CITY_FIRST

                                                                  
    if len(found_cities) > 1:
        keyboard = [
            [InlineKeyboardButton(f"{city}, {country}", callback_data=f"s_c_s_1|{city}|{country}")]
            for city, country in found_cities
        ]
        keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel_create_synastry")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            text="🔎 Найдено несколько городов. Выберите нужный:",
            reply_markup=reply_markup
        )
        
        return SYNASTRY_INPUT_CITY_FIRST

                                                
    selected_city, selected_country = found_cities[0]

    context.user_data["synastry_data_first"]["city"] = selected_city
    context.user_data["synastry_data_first"]["country"] = selected_country

    keyboard = get_years_keyboard(4)
    keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel_create_synastry")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    message_text = (
        "Выберете год рождения второго человека:"
    )

    sent_message = await update.message.reply_text(
        text=message_text,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

                                                                  
    context.user_data['chat_id'] = chat_id
    context.user_data['message_id'] = sent_message.message_id

    save_log_event(chat_id, f"user used <synastry_select_year_second>")

    return SYNASTRY_SELECT_YEAR_SECOND


async def select_city_synastry_first(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.from_user.id
    _, city, country = query.data.split("|")

    context.user_data["synastry_data_first"]["city"] = city
    context.user_data["synastry_data_first"]["country"] = country

    keyboard = get_years_keyboard(4)
    keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel_create_synastry")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    message_text = (
        "Выберете год рождения второго человека:"
    )

    await query.message.edit_text(
        text=message_text,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

    save_log_event(chat_id, f"user select city for synastry")

    return SYNASTRY_SELECT_YEAR_SECOND


async def select_year_second(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    _, year = query.data.split("|")

    context.user_data["synastry_data_second"]["year"] = year

    keyboard = get_months_keyboard()
    keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel_create_synastry")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(
        text="Выберите месяц рождения второго человека:",
        reply_markup=reply_markup
    )

    return SYNASTRY_SELECT_MONTH_SECOND


async def change_year_second_page(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    _, page = query.data.split("|")

    keyboard = get_years_keyboard(int(page))
    keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel_create_synastry")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(
        text="Выберете год рождения второго человека:",
        reply_markup=reply_markup
    )
    
    return SYNASTRY_SELECT_YEAR_SECOND


async def select_month_second(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    _, month = query.data.split("|")

                                                  
    month = month.zfill(2)

    context.user_data["synastry_data_second"]["month"] = month

    keyboard = get_days_keyboard(int(context.user_data["synastry_data_second"]["year"]), int(month))
    keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel_create_synastry")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(
        text="Выберите день рождения второго человека:",
        reply_markup=reply_markup
    )
    
    return SYNASTRY_SELECT_DAY_SECOND


async def select_day_second(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    _, day = query.data.split("|")

                                                  
    day = day.zfill(2)

    context.user_data["synastry_data_second"]["day"] = day

    keyboard = [[InlineKeyboardButton("Отмена", callback_data="cancel_create_synastry")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    sent_message = await query.message.edit_text(
        text="Введите время рождения второго человека. Пример: 14:00",
        reply_markup=reply_markup
    )

    context.user_data['chat_id'] = query.message.chat_id
    context.user_data['message_id'] = sent_message.message_id
    
    return SYNASTRY_INPUT_TIME_SECOND


async def input_time_second(update: Update, context: CallbackContext) -> int:
    if 'message_id' in context.user_data and 'chat_id' in context.user_data:
        await delete_message(context, context.user_data.get('chat_id'), context.user_data.get('message_id'))

    chat_id = context.user_data.get('chat_id')
    time = validate_time(update.message.text)

    if not time:
        keyboard = [[InlineKeyboardButton("Отмена", callback_data="cancel_create_synastry")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        sent_message = await update.message.reply_text(
            text="⌛ Время не распознано. Введите его в формате ЧЧ:ММ. Пример: 14:30",
            reply_markup=reply_markup
        )

        context.user_data['chat_id'] = chat_id
        context.user_data['message_id'] = sent_message.message_id

        return SYNASTRY_INPUT_TIME_SECOND

    context.user_data["synastry_data_second"]["time"] = time

    keyboard = [[InlineKeyboardButton("Отмена", callback_data="cancel_create_synastry")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    sent_message = await update.message.reply_text(
        text="Введите город рождения второго человека:",
        reply_markup=reply_markup
    )

    context.user_data['chat_id'] = chat_id
    context.user_data['message_id'] = sent_message.message_id
    
    return SYNASTRY_INPUT_CITY_SECOND


async def input_city_second(update: Update, context: CallbackContext) -> int:
    if 'message_id' in context.user_data and 'chat_id' in context.user_data:
        await delete_message(context, context.user_data.get('chat_id'), context.user_data.get('message_id'))

    city_name = update.message.text
    found_cities = find_city(city_name)

    if not found_cities:
        keyboard = [[InlineKeyboardButton("Отмена", callback_data="cancel_create_synastry")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        sent_message = await update.message.reply_text(
            text="Город не найден. Попробуйте ввести другое название.",
            reply_markup=reply_markup
        )

        context.user_data['chat_id'] = context.user_data.get('chat_id')
        context.user_data['message_id'] = sent_message.message_id

        return SYNASTRY_INPUT_CITY_SECOND

                                                                  
    if len(found_cities) > 1:
        keyboard = [
            [InlineKeyboardButton(f"{city}, {country}", callback_data=f"s_c_s_2|{city}|{country}")]
            for city, country in found_cities
        ]
        keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel_create_synastry")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            text="🔎 Найдено несколько городов. Выберите нужный:",
            reply_markup=reply_markup
        )
        
        return SYNASTRY_INPUT_CITY_SECOND

                                                
    selected_city, selected_country = found_cities[0]

    context.user_data["synastry_data_second"]["city"] = selected_city
    context.user_data["synastry_data_second"]["country"] = selected_country

    return await confirm_synastry_data(update, context)


async def select_city_synastry_second(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.from_user.id
    _, city, country = query.data.split("|")

                                  
    context.user_data["synastry_data_second"]["city"] = city
    context.user_data["synastry_data_second"]["country"] = country

    return await confirm_synastry_data(update, context)


async def confirm_synastry_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = None
    if update.callback_query:
        query = update.callback_query
        chat_id = query.from_user.id
    elif update.message:
        chat_id = update.message.from_user.id
    else:
        return ConversationHandler.END

    data_first = context.user_data["synastry_data_first"]
    data_second = context.user_data["synastry_data_second"]

    data_message = (
        f"🌟 <b>Данные для первого человека</b>:\n"
        f"<b>Страна</b>: <i>{data_first['country']}</i>\n"
        f"<b>Город</b>: <i>{data_first['city']}</i>\n"
        f"<b>Дата</b>: <i>{data_first['day']}-{data_first['month']}-{data_first['year']}</i>\n"
        f"<b>Время</b>: <i>{data_first['time']}</i>\n\n"
        f"🌟 <b>Данные для второго человека</b>:\n"
        f"<b>Страна</b>: <i>{data_second['country']}</i>\n"
        f"<b>Город</b>: <i>{data_second['city']}</i>\n"
        f"<b>Дата</b>: <i>{data_second['day']}-{data_second['month']}-{data_second['year']}</i>\n"
        f"<b>Время</b>: <i>{data_second['time']}</i>\n"
    )

    keyboard = [
        [InlineKeyboardButton("✅ Подтвердить", callback_data="create_synastry")],
        [InlineKeyboardButton("❌ Отменить", callback_data="cancel_create_synastry")]
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
    
    save_log_event(chat_id, f"user whaiting confirm data to create synastry")

    return SYNASTRY_CONFIRM_DATA


async def create_synastry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_user.id
    data_first = context.user_data["synastry_data_first"]
    data_second = context.user_data["synastry_data_second"]
    user = get_user_by_chat_id(chat_id)
        
    if not user:
        await update.callback_query.edit_message_text("Ошибка: Пользователь не найден.")
        return ConversationHandler.END

                                      
    await update.callback_query.edit_message_text(f"Ожидайте, карта создаётся.")

    record_usage(user, "synastry")
    
                                       
    queue.enqueue(generate_synastry, chat_id, data_first, data_second)

    context.user_data.clear()
    context.chat_data.clear()

    save_log_event(chat_id, f"user press inline-button <create_synastry>")
    
    return ConversationHandler.END


async def cancel_create_synastry(update: Update, context: CallbackContext):
                                                                  
    query = update.callback_query
    chat_id = query.from_user.id

                                  
    await query.message.delete()

    context.user_data.clear()
    context.chat_data.clear()

                                       
    await query.message.reply_text(
        "Процесс создания карты синастрии был отменён.",
        parse_mode="HTML"
    )

    save_log_event(chat_id, f"user press inline-button <cancel_create_synastry>")

                      
    return ConversationHandler.END


conv_handler_synastry = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(start_input_synastry, pattern="^start_input_synastry$")
    ],
    states={
        SYNASTRY_SELECT_YEAR_FIRST: [
            CallbackQueryHandler(select_year_first, pattern=r"^select_year\|\d+$"),
            CallbackQueryHandler(change_year_first_page, pattern=r"^change_year_page\|[-\d]+$"),
            CallbackQueryHandler(cancel_create_synastry, pattern="^cancel_create_synastry$")
        ],
        SYNASTRY_SELECT_MONTH_FIRST: [
            CallbackQueryHandler(select_month_first, pattern=r"^month\|\d+$"),
            CallbackQueryHandler(cancel_create_synastry, pattern="^cancel_create_synastry$")
        ],
        SYNASTRY_SELECT_DAY_FIRST: [
            CallbackQueryHandler(select_day_first, pattern=r"^day\|\d+$"),
            CallbackQueryHandler(cancel_create_synastry, pattern="^cancel_create_synastry$")
        ],
        SYNASTRY_INPUT_TIME_FIRST: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, input_time_first),
            CallbackQueryHandler(cancel_create_synastry, pattern="^cancel_create_synastry$")
        ],
        SYNASTRY_INPUT_CITY_FIRST: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, input_city_first),
            CallbackQueryHandler(select_city_synastry_first, pattern=r"^s_c_s_1\|.*$"),
            CallbackQueryHandler(cancel_create_synastry, pattern="^cancel_create_synastry$")
        ],
        SYNASTRY_SELECT_YEAR_SECOND: [
            CallbackQueryHandler(select_year_second, pattern=r"^select_year\|\d+$"),
            CallbackQueryHandler(change_year_second_page, pattern=r"^change_year_page\|[-\d]+$"),
            CallbackQueryHandler(cancel_create_synastry, pattern="^cancel_create_synastry$")
        ],
        SYNASTRY_SELECT_MONTH_SECOND: [
            CallbackQueryHandler(select_month_second, pattern=r"^month\|\d+$"),
            CallbackQueryHandler(cancel_create_synastry, pattern="^cancel_create_synastry$")
        ],
        SYNASTRY_SELECT_DAY_SECOND: [
            CallbackQueryHandler(select_day_second, pattern=r"^day\|\d+$"),
            CallbackQueryHandler(cancel_create_synastry, pattern="^cancel_create_synastry$")
        ],
        SYNASTRY_INPUT_TIME_SECOND: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, input_time_second),
            CallbackQueryHandler(cancel_create_synastry, pattern="^cancel_create_synastry$")
        ],
        SYNASTRY_INPUT_CITY_SECOND: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, input_city_second),
            CallbackQueryHandler(select_city_synastry_second, pattern=r"^s_c_s_2\|.*$"),
            CallbackQueryHandler(cancel_create_synastry, pattern="^cancel_create_synastry$")
        ],
        SYNASTRY_CONFIRM_DATA: [
            CallbackQueryHandler(create_synastry, pattern="^create_synastry$"),
            CallbackQueryHandler(cancel_create_synastry, pattern="^cancel_create_synastry$")
        ]
    },
    fallbacks=[CallbackQueryHandler(cancel_create_synastry, pattern="^cancel_create_synastry$")],
    allow_reentry=True,
)
