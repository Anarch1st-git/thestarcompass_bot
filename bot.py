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


async def m_generation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    user = get_user_by_chat_id(chat_id)

    if not user:
        await update.message.reply_text(ERROR_MESSAGE_NOT_USER)
        return
    
    keyboard = m_generation_keyboard()
    
               
    generation_text = (
        "🔮 <b>Астрологический расчёт карт</b>\n"
        "Создавайте уникальные карты для себя и близких!\n\n"
        "- 🪐 <b>Натальная карта:</b> откройте тайны своего рождения.\n"
        "- 🌌 <b>Транзиты:</b> следите за влиянием звёзд в настоящем и будущем.\n"
        "- 💞 <b>Синастрия:</b> узнайте секреты совместимости с другими.\n\n"
    )
    
                                      
    reply_markup = InlineKeyboardMarkup(keyboard)

    send_message = await update.message.reply_text(
        text=generation_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

    context.user_data['chat_id'] = update.message.chat_id
    context.user_data['message_id_m_generation'] = send_message.message_id

    save_log_event(chat_id, f"user press keyboard-button <m_generation>")


async def m_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.from_user.id
    await update.message.reply_text(
        text="Техническая поддержка доступна по адресу почты: <b>support@thestarcompass.ru</b>",
        parse_mode="HTML"
    )
    save_log_event(chat_id, f"user press keyboard-button <m_support>")


async def agreement(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.from_user.id
    await update.message.reply_text("Вы можете ознакомиться с пользовательским соглашением по ссылке: https://thestarcompass.ru/agreement.html")
    save_log_event(chat_id, f"user enter command /agreement")


async def policy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.from_user.id
    await update.message.reply_text("Вы можете ознакомиться с политикой конфиденциальности по ссылке: https://thestarcompass.ru/policy.html")
    save_log_event(chat_id, f"user enter command /policy")


async def back_to_generation_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = query.from_user.id

    user = get_user_by_chat_id(chat_id)

    if not user:
        await update.message.reply_text(ERROR_MESSAGE_NOT_USER)
        return
    
    keyboard = m_generation_keyboard()

               
    generation_text = (
        "🔮 <b>Астрологический расчёт карт</b>\n"
        "Создавайте уникальные карты для себя и близких!\n\n"
        "- 🪐 <b>Натальная карта:</b> откройте тайны своего рождения.\n"
        "- 🌌 <b>Транзиты:</b> следите за влиянием звёзд в настоящем и будущем.\n"
        "- 💞 <b>Синастрия:</b> узнайте секреты совместимости с другими.\n\n"
    )
    
                                      
    reply_markup = InlineKeyboardMarkup(keyboard)

                                                      
    await query.edit_message_text(
        text=generation_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )
    save_log_event(chat_id, f"user press inline-button <back_to_generation_menu>")
    return ConversationHandler.END


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
    planets_list = list(report["planets"].items())

                                                                  
    planets_info = "\n\n".join([
        f"{planet_translate.get(name, name)}: {astro_translate.get(planet['quality'], planet['quality'])}, "
        f"{astro_translate.get(planet['element'], planet['element'])}, "
        f"{sign_translate.get(planet['sign'], planet['sign'])}, "
        f"{house_translate.get(planet['house'], planet['house'])} "
        f"{astro_translate['Retrograde'] if planet['retrograde'] else astro_translate['Direct']} "
        f"({round(planet['degree'], 2)}°)"
        for name, planet in planets_list
    ])

    keyboard = [[InlineKeyboardButton("Назад", callback_data="back_natalchart_message")]]

                                                                                 
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text=planets_info,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


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
    houses_list = list(report["houses"].items())

                                                                  
    houses_info = "\n\n".join([
        f"{house_translate.get(name, name)}: {astro_translate.get(house['quality'], house['quality'])}, "
        f"{astro_translate.get(house['element'], house['element'])}, "
        f"{sign_translate.get(house['sign'], house['sign'])} "
        f"({round(house['degree'], 2)}°)"
        for name, house in houses_list
    ])

    keyboard = [[InlineKeyboardButton("Назад", callback_data="back_natalchart_message")]]

                                                                                 
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text=houses_info,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


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
    
                        
    tracts = natal.tracts_planets

    keyboard = [[InlineKeyboardButton("Назад", callback_data="back_natalchart_message")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text=tracts,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


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
    
                        
    tracts = natal.tracts_houses

    keyboard = [[InlineKeyboardButton("Назад", callback_data="back_natalchart_message")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text=tracts,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


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

                                 
    keyboard.append([{"text": "🌙 Лунная фаза", "callback_data": "lunar_phase"}])
    keyboard.append([{"text": "📖 Трактовки (планеты)", "callback_data": "tracts_planets"}])
    keyboard.append([{"text": "📖 Трактовки (дома)", "callback_data": "tracts_houses"}])
           
                                                                                      
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


def main() -> None:
    application = Application.builder().token(TOKEN_BOT).connect_timeout(10).read_timeout(10).build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(ukassa_pay_handler)
    application.add_handler(conv_handler_natalchart)
    application.add_handler(conv_handler_synastry)
    application.add_handler(conv_handler_transit)

                                                                       
    application.add_handler(MessageHandler(filters.Text("🔮 Астрологический расчёт"), m_generation))
    application.add_handler(MessageHandler(filters.Text("📞 Поддержка"), m_support))
    application.add_handler(CommandHandler("agreement", agreement))
    application.add_handler(CommandHandler("policy", policy))
    
                                                                                                         
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
