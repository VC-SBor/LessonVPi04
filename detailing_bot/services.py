"""
Каталог услуг детейлинг-центра DetailPro.
Данные хранятся отдельно от кода для удобного редактирования.
"""

# Каталог услуг
SERVICES = [
    {
        "id": "wash",
        "name": "Комплексная мойка",
        "price": 1500,
        "description": "Полная мойка кузова, дисков, стёкол, дверных проёмов и сушка автомобиля."
    },
    {
        "id": "dry_cleaning",
        "name": "Химчистка салона",
        "price": 7000,
        "description": "Глубокая очистка сидений, потолка, пола, дверных карт и пластиковых элементов. Удаление сложных загрязнений и устранение запахов."
    },
    {
        "id": "polishing",
        "name": "Полировка кузова",
        "price": 12000,
        "description": "Восстановительная полировка лакокрасочного покрытия: удаление мелких царапин, голограмм и окислов, возврат блеска и глубины цвета кузова."
    },
    {
        "id": "ceramic",
        "name": "Керамическое покрытие",
        "price": 25000,
        "description": "Нанесение защитного керамического слоя на кузов: защита от реагентов, грязи и мелких царапин, гидрофобный эффект и стойкий глянец на срок до 1–2 лет."
    },
    {
        "id": "anti_rain",
        "name": "Антидождь",
        "price": 3000,
        "description": "Защитное покрытие стёкол для улучшения видимости во время дождя: капли скатываются с поверхности даже без работы дворников."
    }
]


def get_service_by_id(service_id: str) -> dict | None:
    """Получить услугу по ID."""
    for service in SERVICES:
        if service["id"] == service_id:
            return service
    return None


def format_price(price: int) -> str:
    """Форматировать цену с разделителями тысяч."""
    return f"{price:,}".replace(",", " ")


def get_service_info(service: dict) -> str:
    """Форматировать информацию об услуге для вывода."""
    return (
        f"{service['name']}\n\n"
        f"{service['description']}\n\n"
        f"Стоимость: {format_price(service['price'])} руб."
    )


def get_price_list() -> str:
    """Форматировать прайс-лист для вывода."""
    lines = ["Прайс-лист", ""]
    for service in SERVICES:
        lines.append(f"{service['name']} — {format_price(service['price'])} руб.")
    return "\n".join(lines)
