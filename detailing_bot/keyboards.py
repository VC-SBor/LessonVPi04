"""
Клавиатуры для бота DetailPro.
Используются Callback-кнопки для навигации по меню.
"""

from vkbottle import Keyboard, Callback

# Главное меню
main_keyboard = Keyboard(inline=True)
main_keyboard.add(Callback("Услуги", {"menu": "services"}))
main_keyboard.add(Callback("Прайс-лист", {"menu": "price"}))
main_keyboard.add(Callback("Связаться с менеджером", {"menu": "contact"}))

# Клавиатура списка услуг
services_keyboard = Keyboard(inline=True)
services_keyboard.add(Callback("Комплексная мойка", {"service": "wash"}))
services_keyboard.add(Callback("Химчистка салона", {"service": "dry_cleaning"}))
services_keyboard.add(Callback("Полировка кузова", {"service": "polishing"}))
services_keyboard.add(Callback("Керамическое покрытие", {"service": "ceramic"}))
services_keyboard.add(Callback("Антидождь", {"service": "anti_rain"}))
services_keyboard.row()
services_keyboard.add(Callback("Главное меню", {"menu": "main"}))

# Клавиатура после просмотра услуги
service_keyboard = Keyboard(inline=True)
service_keyboard.add(Callback("Назад", {"menu": "services"}))
service_keyboard.add(Callback("Главное меню", {"menu": "main"}))

# Клавиатура после прайс-листа
price_keyboard = Keyboard(inline=True)
price_keyboard.add(Callback("Главное меню", {"menu": "main"}))

# Клавиатура после связи с менеджером
contact_keyboard = Keyboard(inline=True)
contact_keyboard.add(Callback("Главное меню", {"menu": "main"}))
