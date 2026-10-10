"""
Конфигурация бота DetailPro.
Токен и ID группы хранятся в файле .env, не хардкодятся в основном коде.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Токен сообщества ВКонтакте
# Получить можно в настройках сообщества: Работа с API -> Ключи доступа
VK_TOKEN = os.getenv("VK_TOKEN", "your_vk_token_here")

# ID сообщества ВКонтакте (без минуса)
# Узнать можно в настройках сообщества: Основная информация -> Идентификатор сообщества
GROUP_ID = int(os.getenv("GROUP_ID", "123456789"))

# Версия VK API
API_VERSION = "5.131"
