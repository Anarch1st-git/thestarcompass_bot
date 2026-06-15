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
    NATAL_SELECT_YEAR,
    NATAL_SELECT_MONTH,
    NATAL_SELECT_DAY,
    NATAL_INPUT_TIME,
    NATAL_INPUT_CITY,
    NATAL_CONFIRM_DATA
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
from tasks import generate_natalchart


async def start_input_natalchart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.from_user.id
    user = get_user_by_chat_id(chat_id)

    if not user:
        await query.message.edit_text(ERROR_MESSAGE_NOT_USER)
        save_log_event(chat_id, f"user press inline-button <start_input_natalchart>, but ERROR_MESSAGE_NOT_USER")
        return ConversationHandler.END
    
                                      
    keyboard = get_years_keyboard(4)
    keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel_create_natalchart")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    message_text = (
        "Выберите год рождения:"
    )

                                                                 
    await query.edit_message_text(
        text=message_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

    context.user_data["natalchart_data"] = {
        "year": "2000",
        "month": "01",
        "day": "01",
        "time": "12:00",
        "city": "Москва",
        "country": "Россия"
    }

    save_log_event(chat_id, f"user press inline-button <start_input_natalchart>")

    return NATAL_SELECT_YEAR


async def select_year(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    _, year = query.data.split("|")

    context.user_data["natalchart_data"]["year"] = year
    keyboard = get_months_keyboard()
    keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel_create_natalchart")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(
        text="Выберите месяц рождения:",
        reply_markup=reply_markup
    )

    return NATAL_SELECT_MONTH


async def change_year_page(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    _, page = query.data.split("|")

    keyboard = get_years_keyboard(int(page))
    keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel_create_natalchart")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(
        text="Выберите год рождения:",
        reply_markup=reply_markup
    )

    return NATAL_SELECT_YEAR


async def select_month(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    _, month = query.data.split("|")

                                                  
    month = month.zfill(2)

    context.user_data["natalchart_data"]["month"] = month

    keyboard = get_days_keyboard(int(context.user_data["natalchart_data"]["year"]), int(month))
    keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel_create_natalchart")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(
        text="Выберите день рождения:",
        reply_markup=reply_markup
    )

    return NATAL_SELECT_DAY


async def select_day(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    _, day = query.data.split("|")

                                                  
    day = day.zfill(2)

    context.user_data["natalchart_data"]["day"] = day

    keyboard = [[InlineKeyboardButton("Отмена", callback_data="cancel_create_natalchart")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    sent_message = await query.message.edit_text(
        text="Введите время рождения. Пример: 14:00",
        reply_markup=reply_markup
    )

    context.user_data['chat_id'] = query.message.chat_id
    context.user_data['message_id'] = sent_message.message_id

    return NATAL_INPUT_TIME


async def input_time(update: Update, context: CallbackContext) -> int:
    if 'message_id' in context.user_data and 'chat_id' in context.user_data:
        await delete_message(context, context.user_data.get('chat_id'), context.user_data.get('message_id'))

    chat_id = context.user_data.get('chat_id')
    time = validate_time(update.message.text)

    if not time:
        keyboard = [[InlineKeyboardButton("Отменить", callback_data="cancel_create_natalchart")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        sent_message = await update.message.reply_text(
            text="⌛ Время не распознано. Введите его в формате ЧЧ:ММ.",
            reply_markup=reply_markup
        )

        context.user_data['chat_id'] = context.user_data.get('chat_id')
        context.user_data['message_id'] = sent_message.message_id

        return NATAL_INPUT_TIME

    context.user_data["natalchart_data"]["time"] = time

    keyboard = [[InlineKeyboardButton("Отмена", callback_data="cancel_create_natalchart")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    sent_message = await update.message.reply_text(
        text="Введите город рождения:",
        reply_markup=reply_markup
    )

    context.user_data['chat_id'] = chat_id
    context.user_data['message_id'] = sent_message.message_id

    return NATAL_INPUT_CITY


async def input_city(update: Update, context: CallbackContext) -> int:
    if 'message_id' in context.user_data and 'chat_id' in context.user_data:
        await delete_message(context, context.user_data.get('chat_id'), context.user_data.get('message_id'))

    city_name = update.message.text
    found_cities = find_city(city_name)

    if not found_cities:
        keyboard = [[InlineKeyboardButton("Отмена", callback_data="cancel_create_natalchart")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        sent_message = await update.message.reply_text(
            text="Город не найден. Попробуйте ввести другое название.",
            reply_markup=reply_markup
        )

        context.user_data['chat_id'] = context.user_data.get('chat_id')
        context.user_data['message_id'] = sent_message.message_id

        return NATAL_INPUT_CITY

                                                                  
    if len(found_cities) > 1:
        keyboard = [
            [InlineKeyboardButton(f"{city}, {country}", callback_data=f"s_c_n|{city}|{country}")]
            for city, country in found_cities
        ]
        keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel_create_natalchart")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            text="🔎 Найдено несколько городов. Выберите нужный:",
            reply_markup=reply_markup
        )
        
        return NATAL_INPUT_CITY

                                                
    selected_city, selected_country = found_cities[0]

    context.user_data["natalchart_data"]["city"] = selected_city
    context.user_data["natalchart_data"]["country"] = selected_country

    return await confirm_natalchart_data(update, context)


async def select_city_natal(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    chat_id = query.from_user.id

    _, city, country = query.data.split("|")

                                  
    context.user_data["natalchart_data"]["city"] = city
    context.user_data["natalchart_data"]["country"] = country

    save_log_event(chat_id, f"user select city for natalchart")

    return await confirm_natalchart_data(update, context)


async def confirm_natalchart_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = None
    if update.callback_query:
        query = update.callback_query
        chat_id = query.from_user.id
    elif update.message:
        chat_id = update.message.from_user.id
    else:
        return ConversationHandler.END

    data = context.user_data["natalchart_data"]

    data_message = (
        f"🌟 <b>Ваши данные:</b>\n\n"
        f"<b>Страна</b>: <i>{data['country']}</i>\n"
        f"<b>Город</b>: <i>{data['city']}</i>\n"
        f"<b>Дата</b>: <i>{data['day']}-{data['month']}-{data['year']}</i>\n"
        f"<b>Время</b>: <i>{data['time']}</i>\n"
    )

    keyboard = [
        [InlineKeyboardButton("✅ Подтвердить", callback_data="create_natalchart")],
        [InlineKeyboardButton("❌ Отменить", callback_data="cancel_create_natalchart")]
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
    
    save_log_event(chat_id, f"user whaiting confirm data to create natalchart")

    return NATAL_CONFIRM_DATA


async def create_natalchart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_user.id
    data_input_for_natalchart = context.user_data["natalchart_data"]
    user = get_user_by_chat_id(chat_id)

    if not user:
        await update.callback_query.edit_message_text("Ошибка: Пользователь не найден.")
        return ConversationHandler.END

                                      
    await update.callback_query.edit_message_text(f"Ожидайте, карта создаётся.")

    record_usage(user, "natal")
    
                                       
    queue.enqueue(generate_natalchart, chat_id, data_input_for_natalchart)

    context.user_data.clear()
    context.chat_data.clear()

    save_log_event(chat_id, f"user press inline-button <create_natalchart>")

    return ConversationHandler.END


async def cancel_create_natalchart(update: Update, context: CallbackContext):
                                                                  
    query = update.callback_query
    chat_id = query.from_user.id

                                  
    await query.message.delete()

    context.user_data.clear()
    context.chat_data.clear()

                                       
    await query.message.reply_text(
        "Процесс создания натальной карты был отменён.",
        parse_mode="HTML"
    )

    save_log_event(chat_id, f"user press inline-button <cancel_create_natalchart>")

                      
    return ConversationHandler.END


conv_handler_natalchart = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(start_input_natalchart, pattern="^start_input_natalchart$")
    ],
    states={
        NATAL_SELECT_YEAR: [
            CallbackQueryHandler(select_year, pattern=r"^select_year\|\d+$"),
            CallbackQueryHandler(change_year_page, pattern=r"^change_year_page\|[-\d]+$"),
            CallbackQueryHandler(cancel_create_natalchart, pattern="^cancel_create_natalchart$")
        ],
        NATAL_SELECT_MONTH: [
            CallbackQueryHandler(select_month, pattern=r"^month\|\d+$"),
            CallbackQueryHandler(cancel_create_natalchart, pattern="^cancel_create_natalchart$")
        ],
        NATAL_SELECT_DAY: [
            CallbackQueryHandler(select_day, pattern=r"^day\|\d+$"),
            CallbackQueryHandler(cancel_create_natalchart, pattern="^cancel_create_natalchart$")
        ],
        NATAL_INPUT_TIME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, input_time),
            CallbackQueryHandler(cancel_create_natalchart, pattern="^cancel_create_natalchart$")
        ],
        NATAL_INPUT_CITY: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, input_city),
            CallbackQueryHandler(select_city_natal, pattern=r"^s_c_n\|.*$"),
            CallbackQueryHandler(cancel_create_natalchart, pattern="^cancel_create_natalchart$")
        ],
        NATAL_CONFIRM_DATA: [
            CallbackQueryHandler(create_natalchart, pattern="^create_natalchart$"),
            CallbackQueryHandler(cancel_create_natalchart, pattern="^cancel_create_natalchart$")
        ]
    },
    fallbacks=[CallbackQueryHandler(cancel_create_natalchart, pattern="^cancel_create_natalchart$")],
    allow_reentry=True,
)
