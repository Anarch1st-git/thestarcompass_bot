from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from datetime import datetime
import calendar


# Главное меню "Ваш профиль"
def profile_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Подписаться", callback_data="btn_inl_subscribe")]
    ])


# Клавиатура с ссылкой на оплату
def payment_link_keyboard(link):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Оплатить", url=link)]
    ])


# Главное меню "Генерация"
def m_generation_keyboard():
    buttons = [
        [InlineKeyboardButton("Натальная карта", callback_data="start_input_natalchart")],
        [InlineKeyboardButton("Транзит", callback_data="start_input_transit")],
        [InlineKeyboardButton("Синастрия", callback_data="start_input_synastry")]
    ]

    return buttons


# Получаем текущий год
CURRENT_YEAR = datetime.now().year
START_YEAR = 1900
YEARS_PER_PAGE = 20  # Количество лет на странице
BUTTONS_PER_ROW = 5


# Функция для генерации inline-клавиатуры выбора года с пагинацией
def get_years_keyboard(page: int = 0, max_year: int = CURRENT_YEAR):
    start = START_YEAR + page * YEARS_PER_PAGE
    end = min(start + YEARS_PER_PAGE, max_year + 1)  # Используем max_year вместо CURRENT_YEAR
    
    # Создаем список кнопок
    buttons = [InlineKeyboardButton(str(year), callback_data=f"select_year|{year}") for year in range(start, end)]
    
    # Разбиваем кнопки на строки по BUTTONS_PER_ROW штук
    keyboard = [buttons[i:i + BUTTONS_PER_ROW] for i in range(0, len(buttons), BUTTONS_PER_ROW)]
    
    # Навигационные кнопки
    nav_buttons = []
    if start > START_YEAR:
        nav_buttons.append(InlineKeyboardButton("⬅ Назад", callback_data=f"change_year_page|{page-1}"))
    if end < max_year:
        nav_buttons.append(InlineKeyboardButton("Вперёд ➡", callback_data=f"change_year_page|{page+1}"))
    
    # Добавляем навигационные кнопки в клавиатуру
    if nav_buttons:
        keyboard.append(nav_buttons)

    return keyboard
# def get_years_keyboard(page: int = 0):
#     start = START_YEAR + page * YEARS_PER_PAGE
#     end = min(start + YEARS_PER_PAGE, CURRENT_YEAR + 1)
    
#     # Создаем список кнопок
#     buttons = [InlineKeyboardButton(str(year), callback_data=f"select_year|{year}") for year in range(start, end)]
    
#     # Разбиваем кнопки на строки по BUTTONS_PER_ROW штук
#     keyboard = [buttons[i:i + BUTTONS_PER_ROW] for i in range(0, len(buttons), BUTTONS_PER_ROW)]
    
#     # Навигационные кнопки
#     nav_buttons = []
#     if start > START_YEAR:
#         nav_buttons.append(InlineKeyboardButton("⬅ Назад", callback_data=f"change_year_page|{page-1}"))
#     if end < CURRENT_YEAR:
#         nav_buttons.append(InlineKeyboardButton("Вперёд ➡", callback_data=f"change_year_page|{page+1}"))
    
#     # Добавляем навигационные кнопки в клавиатуру
#     if nav_buttons:
#         keyboard.append(nav_buttons)

#     return keyboard


# Функция для генерации inline-клавиатуры выбора месяца
def get_months_keyboard():
    months = [
        InlineKeyboardButton(month, callback_data=f"month|{i+1}")
        for i, month in enumerate([
            "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
            "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
        ])
    ]
    
    # Разбиваем кнопки на строки по 3 в каждой
    keyboard = [months[i:i + 3] for i in range(0, len(months), 3)]
    
    return keyboard


# Функция для генерации inline-клавиатуры выбора дня
def get_days_keyboard(year: int, month: int):
    days_in_month = calendar.monthrange(year, month)[1]
    
    # Создаём список кнопок
    days = [InlineKeyboardButton(str(day), callback_data=f"day|{day}") for day in range(1, days_in_month + 1)]
    
    # Разбиваем кнопки на строки по 9 штук
    keyboard = [days[i:i + 7] for i in range(0, len(days), 7)]
    
    return keyboard