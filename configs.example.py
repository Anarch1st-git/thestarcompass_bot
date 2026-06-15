import os
from dotenv import load_dotenv

load_dotenv()

TOKEN_BOT = os.getenv("TOKEN_BOT", "")
ERROR_MESSAGE_NOT_USER = "Пользователь не найден. Нажмите /start и попробуйте снова."
