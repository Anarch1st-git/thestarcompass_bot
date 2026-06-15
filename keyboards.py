from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from datetime import datetime
import calendar


def profile_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Подписаться", callback_data="btn_inl_subscribe")]
    ])


def payment_link_keyboard(link):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Оплатить", url=link)]
    ])


def m_generation_keyboard():
    buttons = [
        [InlineKeyboardButton("Натальная карта", callback_data="start_input_natalchart")],
        [InlineKeyboardButton("Транзит", callback_data="start_input_transit")],
        [InlineKeyboardButton("Синастрия", callback_data="start_input_synastry")]
    ]

    return buttons


CURRENT_YEAR = datetime.now().year
START_YEAR = 1900
YEARS_PER_PAGE = 20
BUTTONS_PER_ROW = 5


def get_years_keyboard(page: int = 0, max_year: int = CURRENT_YEAR):
    start = START_YEAR + page * YEARS_PER_PAGE
    end = min(start + YEARS_PER_PAGE, max_year + 1)
    
                           
    buttons = [InlineKeyboardButton(str(year), callback_data=f"select_year|{year}") for year in range(start, end)]
    
                                                        
    keyboard = [buttons[i:i + BUTTONS_PER_ROW] for i in range(0, len(buttons), BUTTONS_PER_ROW)]
    
                          
    nav_buttons = []
    if start > START_YEAR:
        nav_buttons.append(InlineKeyboardButton("⬅ Назад", callback_data=f"change_year_page|{page-1}"))
    if end < max_year:
        nav_buttons.append(InlineKeyboardButton("Вперёд ➡", callback_data=f"change_year_page|{page+1}"))
    
                                                 
    if nav_buttons:
        keyboard.append(nav_buttons)

    return keyboard
                                        
                                                
def get_months_keyboard():
    months = [
        InlineKeyboardButton(month, callback_data=f"month|{i+1}")
        for i, month in enumerate([
            "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
            "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
        ])
    ]
    
                                              
    keyboard = [months[i:i + 3] for i in range(0, len(months), 3)]
    
    return keyboard


def get_days_keyboard(year: int, month: int):
    days_in_month = calendar.monthrange(year, month)[1]
    
                           
    days = [InlineKeyboardButton(str(day), callback_data=f"day|{day}") for day in range(1, days_in_month + 1)]
    
                                          
    keyboard = [days[i:i + 7] for i in range(0, len(days), 7)]
    
    return keyboard
