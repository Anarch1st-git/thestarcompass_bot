import aiohttp
import asyncio
                                                                                    
from converters import convert_svg_to_png
import traceback
from configs import TOKEN_BOT
from handlers import get_user_by_chat_id, save_natal
from tenacity import retry, stop_after_attempt, wait_exponential
from astrocalc import (
    calculate_natalchart,
    format_pretty_report,
    lunar_phase_translate,
    calculate_transit,
    calculate_synastry
)
import json


def generate_natalchart(chat_id, input_data):


    try:
        user = get_user_by_chat_id(chat_id)
                                                       
        natalchart_svg, natal_data, tracts_planets, tracts_houses, theme = calculate_natalchart(input_data)
                               
                              
        natalchart_png = convert_svg_to_png(original_svg=natalchart_svg, dpi=1200, theme=theme)

        save_natal(chat_id, natalchart_png, natal_data, tracts_planets, tracts_houses)

        report = format_pretty_report(natal_data)

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

                                                                               
        keyboard = [
            [{"text": "🪐 Планеты", "callback_data": "planets"}],
            [{"text": "🏠 Дома", "callback_data": "houses"}]
        ]

                                
        keyboard.append([{"text": "🌙 Лунная фаза", "callback_data": "lunar_phase"}])
        keyboard.append([{"text": "📖 Трактовки (планеты)", "callback_data": "tracts_planets"}])
        keyboard.append([{"text": "📖 Трактовки (дома)", "callback_data": "tracts_houses"}])
               
                                                                                          
        reply_markup = {"inline_keyboard": keyboard}

        asyncio.run(send_photo_to_user_async(chat_id, natalchart_png))
        asyncio.run(send_messages_to_user_async(chat_id, summary_text, reply_markup))
    except Exception as e:
        error_message = "Произошла ошибка при создании натальной карты. Попробуйте позже."
        asyncio.run(send_error_message(chat_id, error_message))
        print(f"Ошибка при обработке задачи: {e}")
        traceback.print_exc()


def generate_transit(chat_id, input_data_person, input_data_transit):


    try:
        user = get_user_by_chat_id(chat_id)
                                                       
                             
        transit_svg, aspects_svg, tractations_message, theme = calculate_transit(input_data_person, input_data_transit)
        transit_png = convert_svg_to_png(original_svg=transit_svg, dpi=1200, theme=theme)
        aspects_png = convert_svg_to_png(original_svg=aspects_svg, dpi=1200, theme=theme)

                                   
        asyncio.run(send_photo_to_user_async(chat_id, transit_png))
        asyncio.run(send_photo_to_user_async(chat_id, aspects_png))
        asyncio.run(send_messages_to_user_async(chat_id, tractations_message))
                                     
                                                                                                                              
    except Exception as e:
                                                        
        error_message = "Произошла ошибка при создании карты транзита. Попробуйте позже."
        asyncio.run(send_error_message(chat_id, error_message))
        print(f"Ошибка при обработке задачи: {e}")
        traceback.print_exc()


def generate_synastry(chat_id, input_data_first, input_data_second):


    try:
        user = get_user_by_chat_id(chat_id)
                                                       
                             
        synastry_svg, aspects_svg, tractations_message, theme = calculate_synastry(input_data_first, input_data_second)
        synastry_png = convert_svg_to_png(original_svg=synastry_svg, dpi=1200, theme=theme)
        aspects_png = convert_svg_to_png(original_svg=aspects_svg, dpi=1200, theme=theme)

                                   
        asyncio.run(send_photo_to_user_async(chat_id, synastry_png))
        asyncio.run(send_photo_to_user_async(chat_id, aspects_png))
        asyncio.run(send_messages_to_user_async(chat_id, tractations_message))
                                     
                                                                                                                              
    except Exception as e:
                                                        
        error_message = "Произошла ошибка при создании карты синастрии. Попробуйте позже."
        asyncio.run(send_error_message(chat_id, error_message))
        print(f"Ошибка при обработке задачи: {e}")
        traceback.print_exc()


@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=10))
async def send_photo_to_user_async(chat_id, photo_bytes):


    url = f"https://api.telegram.org/bot{TOKEN_BOT}/sendPhoto"
                                   
    form_data = aiohttp.FormData()
    form_data.add_field("chat_id", str(chat_id))
    form_data.add_field("photo", photo_bytes, filename="natal_chart.png", content_type="image/png")

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=form_data) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Ошибка {response.status}: {error_text}")


@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=10))
async def send_messages_to_user_async(chat_id, message, reply_markup=None):


    url = f"https://api.telegram.org/bot{TOKEN_BOT}/sendMessage"

    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }

    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            if response.status != 200:
                print(f"Не удалось отправить сообщение. Код {response.status}: {await response.text()}")

                                                                                        
@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=10))
async def send_error_message(chat_id, error_message):


    url = f"https://api.telegram.org/bot{TOKEN_BOT}/sendMessage"
    data = {"chat_id": chat_id, "text": error_message}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            if response.status != 200:
                print(f"Не удалось отправить сообщение об ошибке. Код {response.status}: {await response.text()}")
