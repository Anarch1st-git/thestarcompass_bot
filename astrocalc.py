import re
import json
from datetime import datetime
from handlers import (
    get_location_info,
    get_nation_from_country
)
from kerykeion import SynastryAspects, AstrologicalSubject, KerykeionChartSVG, Report
from tracts import astrology_tracts
from planets_in_signs import interpretations_planets_in_zodiac
from houses_in_signs import interpretations_houses_in_zodiac
from synastry_aspect_tractations import TRACTATIONS
from transit_aspects_tractations import TRANSIT_TRACTATIONS
import random


def interpret_aspects(aspects, tractations):
    interpretations = []
    for aspect in aspects:
        p1 = aspect['p1_name']
        p2 = aspect['p2_name']
        aspect_type = aspect['aspect']
        orbit = aspect['orbit']

        aspect_key = f"('{p1}', '{p2}')"
        reverse_aspect_key = f"('{p2}', '{p1}')"

        interpretation = tractations.get(aspect_type, {}).get(aspect_key) or \
                         tractations.get(aspect_type, {}).get(reverse_aspect_key)

        if interpretation:
            text = f"{interpretation}\n\n"
            interpretations.append(text)

    return interpretations[:10]


def create_text_interpritations_planets(ratio_planets):
    message = f""
    for key in ratio_planets:
        key_rus = key.split(" ")
        message += f"{interpretations_planets_in_zodiac[key]}\n\n"
    return message


def create_text_interpritations_houses(ratio_houses):
    message = f""
    for key in ratio_houses:
        key_rus = key.split(" ")
        house_rus = translate_house(key_rus[0])
        sign_rus = translate_sign(key_rus[1])
        message += f"{house_rus} в {sign_rus}: {interpretations_houses_in_zodiac[key]}\n\n"
    return message


def translate_planet(planet_name: str) -> str:
    planet_translation = {
        "Sun": "Солнце",
        "Moon": "Луна",
        "Mercury": "Меркурий",
        "Venus": "Венера",
        "Mars": "Марс",
        "Jupiter": "Юпитер",
        "Saturn": "Сатурн",
        "Uranus": "Уран",
        "Neptune": "Нептун",
        "Pluto": "Плутон",
        "Mean_Node": "Средний узел",
        "True_Node": "Истинный узел",
        "Mean_South_Node": "Средний южный узел",
        "True_South_Node": "Истинный южный узел",
        "Chiron": "Хирон",
        "Mean_Lilith": "Средняя Лилит"
    }
    return planet_translation.get(planet_name, planet_name)


def translate_house(house_name: str) -> str:
    houses_translation = {
        "First_House": "Первый дом",
        "Second_House": "Второй дом",
        "Third_House": "Третий дом",
        "Fourth_House": "Четвёртый дом",
        "Fifth_House": "Пятый дом",
        "Sixth_House": "Шестой дом",
        "Seventh_House": "Седьмой дом",
        "Eighth_House": "Восьмой дом",
        "Ninth_House": "Девятый дом",
        "Tenth_House": "Десятый дом",
        "Eleventh_House": "Одинадцатый дом",
        "Twelfth_House": "Двенадцатый дом"
    }
    return houses_translation.get(house_name, house_name)


def translate_sign(sign: str) -> str:
    sign_translation = {
        "Ari": "Овне",
        "Tau": "Тельце",
        "Gem": "Близнецах",
        "Can": "Раке",
        "Leo": "Льве",
        "Vir": "Деве",
        "Lib": "Весах",
        "Sco": "Скорпионе",
        "Sag": "Стрельце",
        "Cap": "Козероге",
        "Aqu": "Водолее",
        "Pis": "Рыбах"
    }
    return sign_translation.get(sign, sign)


def create_ratio_planets(planets: dict) -> list:
    keys_planets = []
    for planet, data in planets.items():
        if planet != "Mean_Node" and planet != "True_Node" and planet != "Mean_South_Node" and planet != "True_South_Node":
            keys_planets.append(f"{planet} {data['sign']}")
    return keys_planets


def create_ratio_houses(houses: dict) -> list:
    keys_houses = []
    for house, data in houses.items():
        keys_houses.append(f"{house} {data['sign']}")
    return keys_houses


planet_translate = {
    "Sun": "Солнце ☀️", "Moon": "Луна 🌙", "Mercury": "Меркурий ☿", "Venus": "Венера ♀",
    "Mars": "Марс ♂", "Jupiter": "Юпитер ♃", "Saturn": "Сатурн ♄", "Uranus": "Уран ♅",
    "Neptune": "Нептун ♆", "Pluto": "Плутон ♇", "Mean_Node": "Средний Северный Узел ☊",
    "True_Node": "Истинный Северный Узел ☊", "Mean_South_Node": "Средний Южный Узел ☋",
    "True_South_Node": "Истинный Южный Узел ☋", "Chiron": "Хирон ⚷", "Mean_Lilith": "Средняя Лилит ⚸"
}

sign_translate = {
    "Ari": "Овен ♈️", "Tau": "Телец ♉️", "Gem": "Близнецы ♊️", "Can": "Рак ♋️",
    "Leo": "Лев ♌️", "Vir": "Дева ♍️", "Lib": "Весы ♎️", "Sco": "Скорпион ♏️",
    "Sag": "Стрелец ♐️", "Cap": "Козерог ♑️", "Aqu": "Водолей ♒️", "Pis": "Рыбы ♓️"
}

house_translate = {
    "First_House": "1-й дом", "Second_House": "2-й дом", "Third_House": "3-й дом",
    "Fourth_House": "4-й дом", "Fifth_House": "5-й дом", "Sixth_House": "6-й дом",
    "Seventh_House": "7-й дом", "Eighth_House": "8-й дом", "Ninth_House": "9-й дом",
    "Tenth_House": "10-й дом", "Eleventh_House": "11-й дом", "Twelfth_House": "12-й дом"
}

lunar_phase_translate = {
    "New Moon": "Новолуние 🌑", "Waxing Crescent": "Растущий месяц 🌒",
    "First Quarter": "Первая четверть 🌓", "Waxing Gibbous": "Растущая Луна 🌔",
    "Full Moon": "Полнолуние 🌕", "Waning Gibbous": "Убывающая Луна 🌖",
    "Last Quarter": "Последняя четверть 🌗", "Waning Crescent": "Старая Луна 🌘"
}

astro_translate = {
    "Fire": "Огонь 🔥",
    "Earth": "Земля 🌍",
    "Air": "Воздух 🌬",
    "Water": "Вода 🌊",
    
    "Cardinal": "Кардинальный ♑️",
    "Fixed": "Фиксированный ♌️",
    "Mutable": "Мутабельный ♊️",
    
    "Retrograde": "Ретроградная ↩️",
    "Direct": "Директная ➡️",
    
    "New Moon": "Новолуние 🌑",
    "Waxing Crescent": "Растущий месяц 🌒",
    "First Quarter": "Первая четверть 🌓",
    "Waxing Gibbous": "Растущая Луна 🌔",
    "Full Moon": "Полнолуние 🌕",
    "Waning Gibbous": "Убывающая Луна 🌖",
    "Last Quarter": "Последняя четверть 🌗",
    "Waning Crescent": "Старая Луна 🌘",
    
    "North Node": "Северный Узел ☊",
    "South Node": "Южный Узел ☋",
    
    "Ascendant": "Асцендент (Восходящий знак) ⬆️",
    "Descendant": "Десцендент ⬇️",
    "Midheaven": "Средина неба (МС) 🔝",
    "IC": "Имум Цели (Надир) 🔽"
}


def get_lunar_phase_description(phase_name):
    phase_translation = {
        "New Moon": "Новолуние",
        "Waxing Crescent": "Растущая Луна",
        "First Quarter": "Первая четверть",
        "Waxing Gibbous": "Растущая Луна",
        "Full Moon": "Полнолуние",
        "Waning Gibbous": "Убывающая Луна",
        "Last Quarter": "Последняя четверть",
        "Waning Crescent": "Убывающая Луна"
    }

    descriptions = {
        "Новолуние": "Начало нового лунного цикла, время закладки намерений и планирования будущего. Энергия обновления способствует новым начинаниям, но пока не стоит спешить с активными действиями. Важно сосредоточиться на целях и намерениях, которые будут развиваться в ближайшие недели.",
        
        "Растущая Луна": "Энергия постепенно набирает силу, поддерживая рост, развитие и движение к поставленным целям. Хорошее время для обучения, начинания новых проектов и вложения сил в долгосрочные перспективы. Все, что посажено в этот период, имеет шанс укрепиться и дать хорошие плоды.",
        
        "Первая четверть": "Критический момент цикла, когда важно принимать решения и действовать, преодолевая первые препятствия. Это период активности, требующий смелости и решительности. Если на пути возникают трудности, стоит их воспринимать как возможность для роста и корректировки курса.",
        
        "Полнолуние": "Пик энергии и эмоций, время раскрытия потенциала и проявления результатов прошлых усилий. Чувства могут обостряться, а события — достигать кульминации. Благоприятный момент для анализа проделанной работы, осознания достигнутого и освобождения от ненужного.",
        
        "Убывающая Луна": "Энергия постепенно идет на спад, подводя к завершению процессов. Хорошее время для подведения итогов, избавления от ненужного и осознания того, что не работает. Подходит для самоанализа, детоксикации и подготовки к новому циклу.",
        
        "Последняя четверть": "Завершающий этап перед началом нового цикла, когда важно довести дела до конца и освободиться от всего лишнего. Это период переосмысления, размышлений и подготовки к следующему шагу. Благоприятное время для внутренней работы, саморефлексии и завершения старых проектов."
    }

    russian_phase = phase_translation.get(phase_name, "Неизвестная фаза")

    return descriptions.get(russian_phase, "Описание недоступно.")


def get_aspects(user_data):
    aspects = []
    planets = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]
    aspect_angles = {"Conjunction": 0, "Opposition": 180, "Trine": 120, "Square": 90, "Sextile": 60}
    
    for i, p1 in enumerate(planets):
        for p2 in planets[i+1:]:
            angle = abs(user_data[p1]["abs_pos"] - user_data[p2]["abs_pos"])
            angle = min(angle, 360 - angle)
            for aspect, degree in aspect_angles.items():
                if abs(angle - degree) <= 6:
                    aspects.append(f"{user_data[p1]['emoji']} {p1.capitalize()} {aspect} {p2.capitalize()} {user_data[p2]['emoji']}")
    
    return "\n".join(aspects) if aspects else "Нет значимых аспектов."


def get_dominant_planet(user_data):
    scores = {}
    for planet in ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]:
        score = 0
        if user_data[planet]["sign_num"] in [0, 4, 8]:
            score += 5
        if user_data[planet]["house"] in ["First_House", "Tenth_House"]:
            score += 5
        if user_data[planet]["retrograde"]:
            score -= 3
        scores[planet] = score
    
    dominant_planet = max(scores, key=scores.get)
    return f"🌟 Ваша доминирующая планета: {dominant_planet.capitalize()} ({user_data[dominant_planet]['emoji']})"


def get_lunar_nodes(user_data):
    node = user_data["mean_node"]
    return f"🔮 Северный узел в {node['sign']} ({node['emoji']}) – ваша кармическая задача связана с этим знаком."


def get_chiron_analysis(user_data):
    chiron = user_data["chiron"]
    return f"🩹 Хирон в {chiron['sign']} ({chiron['emoji']}) – раны, связанные с этим знаком и домом {chiron['house']}"


def get_lilith_analysis(user_data):
    lilith = user_data["mean_lilith"]
    return f"🌑 Лилит в {lilith['sign']} ({lilith['emoji']}) – скрытые страхи и теневые аспекты личности."


def calculate_element_percentages(astro_subject_info: dict) -> dict:
    elements = {
        "fire": ["Ari", "Leo", "Sag"],
        "earth": ["Tau", "Vir", "Cap"],
        "air": ["Gem", "Lib", "Aqu"],
        "water": ["Can", "Sco", "Pis"]
    }

    element_count = {"fire": 0, "earth": 0, "air": 0, "water": 0}
    total_planets = 0

    for planet in astro_subject_info["planets_names_list"]:
        planet_data = astro_subject_info.get(planet.lower())
        if planet_data:
            sign = planet_data["sign"]
            for element, signs in elements.items():
                if sign in signs:
                    element_count[element] += 1
                    total_planets += 1

    if total_planets == 0:
        return {key: 0 for key in element_count}

    element_percentages = {
        key: round((value / total_planets) * 100, 2) for key, value in element_count.items()
    }

    return element_percentages


def format_astrology_report(user_data):
    report = {
        "birth_info": {
            "date": f"{user_data['year']}-{user_data['month']:02}-{user_data['day']:02}",
            "time": f"{user_data['hour']:02}:{user_data['minute']:02}",
            "city": user_data["city"],
            "country": user_data["nation"],
            "time_zone": user_data["tz_str"],
        },
        "elements_balance": calculate_element_percentages(user_data),
        "planets": {},
        "houses": {},
        "lunar_phase": {
            "name": user_data["lunar_phase"]["moon_phase_name"],
            "emoji": user_data["lunar_phase"]["moon_emoji"],
            "degrees_between_s_m": user_data["lunar_phase"]["degrees_between_s_m"],
            "moon_phase": user_data["lunar_phase"]["moon_phase"],
            "sun_phase": user_data["lunar_phase"]["sun_phase"],
        }
    }
    
    for planet in user_data["planets_names_list"]:
        planet_data = user_data.get(planet.lower())
        if planet_data:
            report["planets"][planet] = {
                "quality": planet_data["quality"],
                "element": planet_data["element"],
                "sign": planet_data["sign"],
                "house": planet_data["house"],
                "retrograde": planet_data["retrograde"],
                "degree": planet_data["position"]
            }
    
    for house in user_data["houses_names_list"]:
        house_data = user_data.get(house.lower())
        if house_data:
            report["houses"][house] = {
                "quality": house_data["quality"],
                "element": house_data["element"],
                "sign": house_data["sign"],
                "degree": house_data["position"]
            }
    
    return report


# def format_pretty_report(tech_report):
#     birth = tech_report["birth_info"]
#     elements = tech_report["elements_balance"]
#     lunar = tech_report["lunar_phase"]
    
#     report = f"""
#     🌟 <b>Натальная карта</b>
    
#     📅 Дата: {birth['date']}
#     ⏰ Время: {birth['time']}
#     📍 Город: {birth['city']}, {birth['country']}
#     ⏳ Часовой пояс: {birth['time_zone']}
    
#     🔮 <b>Стихийный баланс:</b>
#     🔥 Огонь: {elements['fire']}%
#     🌍 Земля: {elements['earth']}%
#     💨 Воздух: {elements['air']}%
#     🌊 Вода: {elements['water']}%
    
#     🌙 <b>Лунная фаза:</b> {lunar['emoji']} {lunar['name']} {lunar['degrees_between_s_m']} {lunar['moon_phase']} {lunar['sun_phase']}

#     <b>Планеты в знаках и домах:</b>
#     """
    
#     for planet, data in tech_report["planets"].items():
#         retrograde = " (ретроградная)" if data["retrograde"] else ""
#         report += f"\n🔹 {planet}: {data['quality']}, {data['element']}, {data['sign']}, {data['house']}{retrograde} ({data['degree']:.2f}°)"
    
#     report += "\n\n<b>Дома гороскопа:</b>"
#     for house, data in tech_report["houses"].items():
#         report += f"\n🏠 {house}: {data['quality']} {data['element']} {data['sign']} ({data['degree']:.2f}°)"
    
#     return report.strip()
def format_pretty_report(tech_report):
    birth = tech_report["birth_info"]
    elements = tech_report["elements_balance"]
    lunar = tech_report["lunar_phase"]
    
    report_dict = {
        "natal_chart": {
            "date": birth["date"],
            "time": birth["time"],
            "city": birth["city"],
            "country": birth["country"],
            "time_zone": birth["time_zone"]
        },
        "elements_balance": {
            "fire": f"{elements['fire']}%",
            "earth": f"{elements['earth']}%",
            "air": f"{elements['air']}%",
            "water": f"{elements['water']}%"
        },
        "lunar_phase": {
            "emoji": lunar["emoji"],
            "name": lunar["name"],
            "degrees_between_s_m": lunar["degrees_between_s_m"],
            "moon_phase": lunar["moon_phase"],
            "sun_phase": lunar["sun_phase"]
        },
        "planets": [],
        "houses": []
    }
    
    for planet, data in tech_report["planets"].items():
        report_dict["planets"].append({
            "title": f"{planet_translate.get(planet, planet)} в {sign_translate.get(data['sign'], data['sign'])}",
            "name": planet,
            "quality": astro_translate.get(data["quality"], data["quality"]),
            "element": astro_translate.get(data["element"], data["element"]),
            "sign": sign_translate.get(data["sign"], data["sign"]),
            "house": house_translate.get(data["house"], data["house"]),
            "retrograde": astro_translate.get("Retrograde", "Ретроградная") if data["retrograde"] else astro_translate.get("Direct", "Директная"),
            "degree": f"{data['degree']:.2f}°"
        })
    
    for house, data in tech_report["houses"].items():
        report_dict["houses"].append({
            "title": f"{house_translate.get(house, house)} в {sign_translate.get(data['sign'], data['sign'])}",
            "house": house,
            "quality": astro_translate.get(data["quality"], data["quality"]),
            "element": astro_translate.get(data["element"], data["element"]),
            "sign": sign_translate.get(data["sign"], data["sign"]),
            "degree": f"{data['degree']:.2f}°"
        })
    
    return report_dict


def extract_planet_positions(report):
    """
    Извлекает данные о планетах и их положениях из полного отчёта.
    """
    planets_data = report.get("planets", {})

    extracted_data = {
        "planets": {
            planet: {
                "sign": details["sign"],
                "house": details["house"]
            }
            for planet, details in planets_data.items()
        }
    }

    return extracted_data


def format_key(planet, sign, house):
    """
    Формирует ключ для словаря интерпретаций.
    """
    return f"{planet.lower()}_in_{sign.lower()}_{house}_house"


def get_interpretation(planet, sign, house):
    """
    Получает трактовку из словаря интерпретаций.
    """
    key = format_key(planet, sign, house)
    return astrology_tracts.get(key, "Трактовка отсутствует.")


def collect_interpretations(data):
    """
    Собирает трактовки из отчёта.
    """
    interpretations_list = []

    for planet, details in data.get("planets", {}).items():
        sign = details["sign"].lower()
        house = details["house"].replace("_House", "").lower()
        interpretation = get_interpretation(planet, sign, house)
        interpretations_list.append({
            "title": f"{planet}: {sign.capitalize()}, {house.capitalize()} дом",
            "interpretation": interpretation
        })

    return interpretations_list


def calculate_natalchart(input_data): #, subscription_status
    theme = "black-gold"
    interpritations = []

    # Получение данных с значениями по умолчанию
    input_day = int(input_data.get("day", 1))
    input_month = int(input_data.get("month", 1))
    input_year = int(input_data.get("year", 2000))
    input_time = input_data.get("time", "12:00")
    input_city = input_data.get("city", "Москва")
    input_country = input_data.get("country", "Россия")

    # Получение географических данных
    try:
        lat, lng, tz = get_location_info(input_country, input_city)
        nation = get_nation_from_country(input_country)
    except Exception:
        lat, lng, tz, nation = "55.75", "37.61", "Europe/Moscow", "RU"

    # Разбор времени
    hour, minute = 0, 0
    if input_time:
        try:
            parsed_time = datetime.strptime(input_time, "%H:%M")
            hour, minute = parsed_time.hour, parsed_time.minute
        except ValueError:
            pass

    # Создание натальной карты
    birth_chart = AstrologicalSubject(
        name="Natal",
        year=input_year,
        month=input_month,
        day=input_day,
        hour=hour,
        minute=minute,
        city=input_city,
        nation=nation,
        lng=lng,
        lat=lat,
        online=False,
        tz_str=tz,
        zodiac_type="Tropic",
        houses_system_identifier="P",
        perspective_type="apparent_geocentric"
    )

    # Генерация SVG натальной карты
    birth_chart_svg = KerykeionChartSVG(
        first_obj=birth_chart,
        chart_type="Natal",
        theme=theme,
        chart_language="RU"
    )

    natalchart_svg = birth_chart_svg.makeWheelOnlySVG()

    ao = json.loads(birth_chart.json())
    tech_report = format_astrology_report(ao)

    tracts_report = Report(birth_chart).get_full_report()
    ratio_planets = create_ratio_planets(tracts_report['planets'])
    ratio_houses = create_ratio_houses(tracts_report['houses'])

    info_planets = []
    info_houses = []
    # if not subscription_status:
    #     info_planets.append(ratio_planets[0])
    #     info_planets.append(ratio_planets[1])
    #     info_houses.append(ratio_houses[0])
    #     #interpritations.append(all_info)
    #     interpritations.append(create_text_interpritations_planets(info_planets))
    #     interpritations.append(create_text_interpritations_houses(info_houses))
    # else:
    extend_info_planets = ratio_planets
    extend_info_houses = ratio_houses
    #interpritations.append(all_info)
    interpritations.append(create_text_interpritations_planets(extend_info_planets))
    interpritations.append(create_text_interpritations_houses(extend_info_houses))

    return natalchart_svg, tech_report, interpritations[0], interpritations[1], theme


# def format_aspects_report(aspects_list, tractations):
#     report_dict = {"synastry": {}, "houses": {}}
    
#     for aspect in aspects_list:
#         p1 = aspect["p1_name"]
#         p2 = aspect["p2_name"]
#         aspect_type = aspect["aspect"]
#         orbit = round(aspect["orbit"], 2)
        
#         key = f"{p1} - {p2}"
        
#         # Ищем трактовку в словаре
#         aspect_key = str((p1, p2))
#         description = tractations.get(aspect_type, {}).get(aspect_key, "Трактовка отсутствует")
        
#         aspect_data = {
#             "aspect": aspect_type,
#             "orbit": orbit,
#             "description": description
#         }
        
#         # Определяем, куда записать аспект (планеты или дома)
#         if "House" in p1 or "House" in p2:
#             report_dict["houses"][key] = aspect_data
#         else:
#             report_dict["synastry"][key] = aspect_data
    
#     return json.dumps(report_dict, ensure_ascii=False, indent=2)



def calculate_transit(input_data_object, input_data_transit): #, subscription_status
    theme = "black-gold"

    # Получение данных с значениями по умолчанию
    input_object_day = int(input_data_object.get("day", 1))
    input_object_month = int(input_data_object.get("month", 1))
    input_object_year = int(input_data_object.get("year", 2000))
    input_object_time = input_data_object.get("time", "12:00")
    input_object_city = input_data_object.get("city", "Москва")
    input_object_country = input_data_object.get("country", "Россия")

    input_transit_day = int(input_data_transit.get("day", 1))
    input_transit_month = int(input_data_transit.get("month", 1))
    input_transit_year = int(input_data_transit.get("year", 2030))
    input_transit_time = input_data_transit.get("time", "12:00")
    input_transit_city = input_data_transit.get("city", "Москва")
    input_transit_country = input_data_transit.get("country", "Россия")

    # Получение географических данных
    try:
        object_lat, object_lng, object_tz = get_location_info(input_object_country, input_object_city)
        object_nation = get_nation_from_country(input_object_country)
    except Exception:
        object_lat, object_lng, object_tz, object_nation = "55.75", "37.61", "Europe/Moscow", "RU"
    
    try:
        transit_lat, transit_lng, transit_tz = get_location_info(input_transit_country, input_transit_city)
        transit_nation = get_nation_from_country(input_transit_country)
    except Exception:
        transit_lat, transit_lng, transit_tz, transit_nation = "55.75", "37.61", "Europe/Moscow", "RU"

    # Разбор времени
    object_hour, object_minute = 0, 0
    if input_object_time:
        try:
            parsed_time = datetime.strptime(input_object_time, "%H:%M")
            object_hour, object_minute = parsed_time.hour, parsed_time.minute
        except ValueError:
            pass
    
    transit_hour, transit_minute = 0, 0
    if input_transit_time:
        try:
            parsed_time = datetime.strptime(input_transit_time, "%H:%M")
            transit_hour, transit_minute = parsed_time.hour, parsed_time.minute
        except ValueError:
            pass

    object_subject = AstrologicalSubject(
        name="transit",
        year=input_object_year,
        month=input_object_month,
        day=input_object_day,
        hour=object_hour,
        minute=object_minute,
        city=input_object_city,
        nation=object_nation,
        lng=object_lng,
        lat=object_lat,
        online=False,
        tz_str=object_tz,
        zodiac_type="Tropic",
        houses_system_identifier="P",
        perspective_type="apparent_geocentric"
    )
    
    # Текущее время для транзитов
    transit_subject = AstrologicalSubject(
        name="transit",
        year=input_transit_year,
        month=input_transit_month,
        day=input_transit_day,
        hour=transit_hour,
        minute=transit_minute,
        city=input_transit_city,
        nation=transit_nation,
        lng=transit_lng,
        lat=transit_lat,
        online=False,
        tz_str=transit_tz,
        zodiac_type="Tropic",
        houses_system_identifier="P",
        perspective_type="apparent_geocentric"
    )

    #synastry_aspects = SynastryAspects(object_subject, transit_subject)

    # aspect_list = []
    # for aspect in synastry_aspects.all_aspects:
    #         aspect_list.append(aspect.dict())

    #print(format_aspects_report(aspect_list, TRACTATIONS))

    tractations_message = None

    #if subscription_status:
    aspect_list = []
    name = SynastryAspects(object_subject, transit_subject)
    
    for aspect in name.all_aspects:
        aspect_list.append(aspect.dict())
    
    result = interpret_aspects(aspect_list, TRANSIT_TRACTATIONS)
    
    tractations_message = ""
    for line in result:
        tractations_message += line
    # else:
    #     # Если подписки нет — выбираем только 3 трактовки
    #     aspect_list = []
    #     name = SynastryAspects(object_subject, transit_subject)
        
    #     for aspect in name.all_aspects:
    #         aspect_list.append(aspect.dict())

    #     result = interpret_aspects(aspect_list, TRANSIT_TRACTATIONS)
        
    #     # Берём только 3 случайные трактовки
    #     limited_result = random.sample(result, min(3, len(result)))

    #     tractations_message = ""
    #     for line in limited_result:
    #         tractations_message += line
    
    object_chart_svg = KerykeionChartSVG(
        first_obj=object_subject,
        chart_type="Transit",
        second_obj=transit_subject,
        theme="black-gold",
        chart_language="RU"
    )
    
    transit_svg = object_chart_svg.makeWheelOnlySVG()
    aspects_svg = object_chart_svg.makeAspectGridOnlySVG()

    return transit_svg, aspects_svg, tractations_message, theme


def calculate_synastry(input_data_first_object, input_data_second_object): #, subscription_status
    theme = "black-gold"
    # Получение данных с значениями по умолчанию
    input_object_first_day = int(input_data_first_object.get("day", 1))
    input_object_first_month = int(input_data_first_object.get("month", 1))
    input_object_first_year = int(input_data_first_object.get("year", 2000))
    input_object_first_time = input_data_first_object.get("time", "12:00")
    input_object_first_city = input_data_first_object.get("city", "Москва")
    input_object_first_country = input_data_first_object.get("country", "Россия")

    input_object_second_day = int(input_data_second_object.get("day", 1))
    input_object_second_month = int(input_data_second_object.get("month", 1))
    input_object_second_year = int(input_data_second_object.get("year", 2030))
    input_object_second_time = input_data_second_object.get("time", "12:00")
    input_object_second_city = input_data_second_object.get("city", "Москва")
    input_object_second_country = input_data_second_object.get("country", "Россия")

    # Получение географических данных
    try:
        object_first_lat, object_first_lng, object_first_tz = get_location_info(input_object_first_country, input_object_first_city)
        object_first_nation = get_nation_from_country(input_object_first_country)
    except Exception:
        object_first_lat, object_first_lng, object_first_tz, object_first_nation = "55.75", "37.61", "Europe/Moscow", "RU"
    
    try:
        object_second_lat, object_second_lng, object_second_tz = get_location_info(input_object_second_country, input_object_second_city)
        object_second_nation = get_nation_from_country(input_object_second_country)
    except Exception:
        object_second_lat, object_second_lng, object_second_tz, object_second_nation = "55.75", "37.61", "Europe/Moscow", "RU"

    # Разбор времени
    object_first_hour, object_first_minute = 0, 0
    if input_object_first_time:
        try:
            parsed_time = datetime.strptime(input_object_first_time, "%H:%M")
            object_first_hour, object_first_minute = parsed_time.hour, parsed_time.minute
        except ValueError:
            pass
    
    object_second_hour, object_second_minute = 0, 0
    if input_object_second_time:
        try:
            parsed_time = datetime.strptime(input_object_second_time, "%H:%M")
            object_second_hour, object_second_minute = parsed_time.hour, parsed_time.minute
        except ValueError:
            pass

    object_chart_first = AstrologicalSubject(
        name="synastry",
        year=input_object_first_year,
        month=input_object_first_month,
        day=input_object_first_day,
        hour=object_first_hour,
        minute=object_first_minute,
        city=input_object_first_city,
        nation=object_first_nation,
        lng=object_first_lng,
        lat=object_first_lat,
        online=False,
        tz_str=object_first_tz,
        zodiac_type="Tropic",
        houses_system_identifier="P",
        perspective_type="apparent_geocentric"
    )
    
    object_chart_second = AstrologicalSubject(
        name="synastry",
        year=input_object_second_year,
        month=input_object_second_month,
        day=input_object_second_day,
        hour=object_second_hour,
        minute=object_second_minute,
        city=input_object_second_city,
        nation=object_second_nation,
        lng=object_second_lng,
        lat=object_second_lat,
        online=False,
        tz_str=object_second_tz,
        zodiac_type="Tropic",
        houses_system_identifier="P",
        perspective_type="apparent_geocentric"
    )

    tractations_message = None

    #if subscription_status:
    aspect_list = []
    name = SynastryAspects(object_chart_first, object_chart_second)
    
    for aspect in name.all_aspects:
        aspect_list.append(aspect.dict())
    
    result = interpret_aspects(aspect_list, TRACTATIONS)
    
    tractations_message = ""
    for line in result:
        tractations_message += line
    # else:
    #     # Если подписки нет — выбираем только 3 трактовки
    #     aspect_list = []
    #     name = SynastryAspects(object_chart_first, object_chart_second)
        
    #     for aspect in name.all_aspects:
    #         aspect_list.append(aspect.dict())

    #     result = interpret_aspects(aspect_list, TRACTATIONS)
        
    #     # Берём только 3 случайные трактовки
    #     limited_result = random.sample(result, min(3, len(result)))

    #     tractations_message = ""
    #     for line in limited_result:
    #         tractations_message += line
    
    object_chart_svg = KerykeionChartSVG(
        first_obj=object_chart_first,
        chart_type="Synastry",
        second_obj=object_chart_second,
        theme="black-gold",
        chart_language="RU"
    )
    
    synastry_svg = object_chart_svg.makeWheelOnlySVG()
    aspects_svg = object_chart_svg.makeAspectGridOnlySVG()

    return synastry_svg, aspects_svg, tractations_message, theme

#user_data = json.loads('''{"name":"none","year":1990,"month":5,"day":5,"hour":13,"minute":13,"city":"Москва","nation":"RU","lng":37.6173,"lat":55.7558,"tz_str":"Europe/Moscow","zodiac_type":"Tropic","houses_system_identifier":"P","houses_system_name":"Placidus","perspective_type":"apparent_geocentric","iso_formatted_local_datetime":"1990-05-05T13:13:00+04:00","iso_formatted_utc_datetime":"1990-05-05T09:13:00+00:00","julian_day":2448016.8840277777,"utc_time":9.216666666666667,"local_time":13.216666666666667,"sun":{"name":"Sun","quality":"Fixed","element":"Earth","sign":"Tau","sign_num":1,"position":14.621116274367033,"abs_pos":44.62111627436703,"emoji":"♉️","point_type":"Planet","house":"Tenth_House","retrograde":false},"moon":{"name":"Moon","quality":"Mutable","element":"Earth","sign":"Vir","sign_num":5,"position":25.803786370514786,"abs_pos":175.80378637051479,"emoji":"♍️","point_type":"Planet","house":"Second_House","retrograde":false},"mercury":{"name":"Mercury","quality":"Fixed","element":"Earth","sign":"Tau","sign_num":1,"position":12.390407107321522,"abs_pos":42.39040710732152,"emoji":"♉️","point_type":"Planet","house":"Tenth_House","retrograde":true},"venus":{"name":"Venus","quality":"Cardinal","element":"Fire","sign":"Ari","sign_num":0,"position":1.3697642022458085,"abs_pos":1.3697642022458085,"emoji":"♈️","point_type":"Planet","house":"Eighth_House","retrograde":false},"mars":{"name":"Mars","quality":"Mutable","element":"Water","sign":"Pis","sign_num":11,"position":10.803839184093306,"abs_pos":340.8038391840933,"emoji":"♓️","point_type":"Planet","house":"Seventh_House","retrograde":false},"jupiter":{"name":"Jupiter","quality":"Cardinal","element":"Water","sign":"Can","sign_num":3,"position":7.695887549667546,"abs_pos":97.69588754966755,"emoji":"♋️","point_type":"Planet","house":"Eleventh_House","retrograde":false},"saturn":{"name":"Saturn","quality":"Cardinal","element":"Earth","sign":"Cap","sign_num":9,"position":25.338812798545973,"abs_pos":295.338812798546,"emoji":"♑️","point_type":"Planet","house":"Fifth_House","retrograde":true},"uranus":{"name":"Uranus","quality":"Cardinal","element":"Earth","sign":"Cap","sign_num":9,"position":9.39746364172288,"abs_pos":279.3974636417229,"emoji":"♑️","point_type":"Planet","house":"Fifth_House","retrograde":true},"neptune":{"name":"Neptune","quality":"Cardinal","element":"Earth","sign":"Cap","sign_num":9,"position":14.478375841957757,"abs_pos":284.47837584195776,"emoji":"♑️","point_type":"Planet","house":"Fifth_House","retrograde":true},"pluto":{"name":"Pluto","quality":"Fixed","element":"Water","sign":"Sco","sign_num":7,"position":16.450636273896833,"abs_pos":226.45063627389683,"emoji":"♏️","point_type":"Planet","house":"Fourth_House","retrograde":true},"chiron":{"name":"Chiron","quality":"Cardinal","element":"Water","sign":"Can","sign_num":3,"position":12.45368582948025,"abs_pos":102.45368582948025,"emoji":"♋️","point_type":"Planet","house":"Eleventh_House","retrograde":false},"mean_lilith":{"name":"Mean_Lilith","quality":"Fixed","element":"Water","sign":"Sco","sign_num":7,"position":20.345451154540314,"abs_pos":230.3454511545403,"emoji":"♏️","point_type":"Planet","house":"Fourth_House","retrograde":false},"first_house":{"name":"First_House","quality":"Fixed","element":"Fire","sign":"Leo","sign_num":4,"position":26.123632980191587,"abs_pos":146.1236329801916,"emoji":"♌️","point_type":"House"},"second_house":{"name":"Second_House","quality":"Mutable","element":"Earth","sign":"Vir","sign_num":5,"position":13.85530148501826,"abs_pos":163.85530148501826,"emoji":"♍️","point_type":"House"},"third_house":{"name":"Third_House","quality":"Cardinal","element":"Air","sign":"Lib","sign_num":6,"position":7.9533036736487475,"abs_pos":187.95330367364875,"emoji":"♎️","point_type":"House"},"fourth_house":{"name":"Fourth_House","quality":"Fixed","element":"Water","sign":"Sco","sign_num":7,"position":11.283266767464767,"abs_pos":221.28326676746477,"emoji":"♏️","point_type":"House"},"fifth_house":{"name":"Fifth_House","quality":"Mutable","element":"Fire","sign":"Sag","sign_num":8,"position":22.54631571181028,"abs_pos":262.5463157118103,"emoji":"♐️","point_type":"House"},"sixth_house":{"name":"Sixth_House","quality":"Cardinal","element":"Earth","sign":"Cap","sign_num":9,"position":28.801835442286347,"abs_pos":298.80183544228635,"emoji":"♑️","point_type":"House"},"seventh_house":{"name":"Seventh_House","quality":"Fixed","element":"Air","sign":"Aqu","sign_num":10,"position":26.123632980191587,"abs_pos":326.1236329801916,"emoji":"♒️","point_type":"House"},"eighth_house":{"name":"Eighth_House","quality":"Mutable","element":"Water","sign":"Pis","sign_num":11,"position":13.85530148501823,"abs_pos":343.85530148501823,"emoji":"♓️","point_type":"House"},"ninth_house":{"name":"Ninth_House","quality":"Cardinal","element":"Fire","sign":"Ari","sign_num":0,"position":7.9533036736487475,"abs_pos":7.9533036736487475,"emoji":"♈️","point_type":"House"},"tenth_house":{"name":"Tenth_House","quality":"Fixed","element":"Earth","sign":"Tau","sign_num":1,"position":11.28326676746476,"abs_pos":41.28326676746476,"emoji":"♉️","point_type":"House"},"eleventh_house":{"name":"Eleventh_House","quality":"Mutable","element":"Air","sign":"Gem","sign_num":2,"position":22.54631571181028,"abs_pos":82.54631571181028,"emoji":"♊️","point_type":"House"},"twelfth_house":{"name":"Twelfth_House","quality":"Cardinal","element":"Water","sign":"Can","sign_num":3,"position":28.80183544228632,"abs_pos":118.80183544228632,"emoji":"♋️","point_type":"House"},"mean_node":{"name":"Mean_Node","quality":"Fixed","element":"Air","sign":"Aqu","sign_num":10,"position":11.874805210014301,"abs_pos":311.8748052100143,"emoji":"♒️","point_type":"Planet","house":"Sixth_House","retrograde":true},"true_node":{"name":"True_Node","quality":"Fixed","element":"Air","sign":"Aqu","sign_num":10,"position":11.900959712803228,"abs_pos":311.9009597128032,"emoji":"♒️","point_type":"Planet","house":"Sixth_House","retrograde":true},"mean_south_node":{"name":"Mean_South_Node","quality":"Fixed","element":"Fire","sign":"Leo","sign_num":4,"position":11.874805210014301,"abs_pos":131.8748052100143,"emoji":"♌️","point_type":"Planet","house":"Twelfth_House","retrograde":true},"true_south_node":{"name":"True_South_Node","quality":"Fixed","element":"Fire","sign":"Leo","sign_num":4,"position":11.900959712803228,"abs_pos":131.90095971280323,"emoji":"♌️","point_type":"Planet","house":"Twelfth_House","retrograde":true},"lunar_phase":{"degrees_between_s_m":131.18267009614775,"moon_phase":11,"sun_phase":10,"moon_emoji":"🌔","moon_phase_name":"Waxing Gibbous"},"planets_names_list":["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Uranus","Neptune","Pluto","Mean_Node","True_Node","Mean_South_Node","True_South_Node","Chiron","Mean_Lilith"],"houses_names_list":["First_House","Second_House","Third_House","Fourth_House","Fifth_House","Sixth_House","Seventh_House","Eighth_House","Ninth_House","Tenth_House","Eleventh_House","Twelfth_House"]}''')

# input_data_object = {
#     "day": 1,
#     "month": 1,
#     "year": 2000,
#     "time": "12:00",
#     "city": "Москва",
#     "country": "Россия"
# }

# input_data_object = {
#     "day": 2,
#     "month": 2,
#     "year": 2026,
#     "time": "14:23",
#     "city": "Москва",
#     "country": "Россия"
# }

# calculate_transit(input_data_object, input_data_object)
#print(get_aspects(user_data))
#print(get_dominant_planet(user_data))
#print(get_lunar_nodes(user_data))
#print(get_chiron_analysis(user_data))
#print(get_lilith_analysis(user_data))
#message = format_astrology_report(user_data)
#print(message)
# result = collect_interpretations(extract_planet_positions(message))

# for item in result:
#     print(f"{item['title']}: {item['interpretation']}")

# display_message = format_pretty_report(message)
# print(display_message)