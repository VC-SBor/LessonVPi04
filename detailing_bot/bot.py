"""
ВК-бот детейлинг-центра DetailPro.
Использует Long Poll API для обработки сообщений.

Принцип работы с «экраном»:
- у пользователя на экране всегда только одно сообщение бота;
- перед отправкой нового сообщения предыдущие удаляются;
- при старте бота удаляется вся история его сообщений.
"""

import json
import random

from vkbottle.bot import Bot, Message
from vkbottle import GroupEventType, GroupTypes

from config import VK_TOKEN, GROUP_ID
from services import get_service_by_id, get_service_info, get_price_list
from keyboards import (
    main_keyboard,
    services_keyboard,
    service_keyboard,
    price_keyboard,
    contact_keyboard,
)

bot = Bot(token=VK_TOKEN)

# ID сообщений бота, которые сейчас «на экране» у каждого пользователя.
# Храним список (а не одно значение), чтобы подчистить всё, если какое-то
# сообщение не удалось удалить с первого раза.
last_message_ids: dict[int, list[int]] = {}

# Тексты сообщений
START_TEXT = (
    "Добро пожаловать в детейлинг-центр DetailPro!\n"
    "Выберите интересующий раздел"
)
UNKNOWN_TEXT = (
    "Извините, я не понял вашу команду.\n"
    "Выберите действие из меню:"
)
SERVICES_TEXT = "Наши услуги:"
MAIN_TEXT = "Выберите интересующий раздел"
CONTACT_TEXT = (
    "Наш менеджер ответит вам в ближайшее время.\n\n"
    "Телефон:\n"
    "+7 900 123-45-67\n\n"
    "Или напишите в сообщения сообщества."
)
SERVICE_NOT_FOUND_TEXT = "Услуга не найдена."

# Текстовые команды, которые ведут в главное меню
GREETINGS = {"начать", "привет", "start", "меню", "главное меню", "help"}


def new_random_id() -> int:
    """Уникальный random_id — ВК использует его для защиты от повторной отправки."""
    return random.randint(0, 2**31 - 1)


def extract_message_id(result) -> int | None:
    """Достать ID сообщения из ответа messages.send.

    В установленной сборке vkbottle метод возвращает словарь
    {"response": <message_id>}, в других версиях — сам ID или объект
    с атрибутом response. Здесь учитываются все варианты.
    """
    if isinstance(result, dict):
        result = result.get("response", result)
    elif hasattr(result, "response"):
        result = result.response
    return result if isinstance(result, int) else None


async def delete_messages(message_ids: list[int]) -> None:
    """Удалить сообщения бота. VK API принимает до 100 ID за раз."""
    for start in range(0, len(message_ids), 100):
        chunk = message_ids[start:start + 100]
        try:
            await bot.api.messages.delete(
                message_ids=chunk,
                delete_for_all=True,
                group_id=GROUP_ID,
            )
        except Exception:
            # ВК может запретить удаление «для всех» (например, сообщение старше суток) —
            # тогда хотя бы удаляем сообщение у сообщества.
            try:
                await bot.api.messages.delete(
                    message_ids=chunk,
                    group_id=GROUP_ID,
                )
            except Exception:
                pass


async def clear_screen(peer_id: int) -> None:
    """Удалить все сообщения бота, которые сейчас видит пользователь."""
    ids = last_message_ids.pop(peer_id, [])
    if ids:
        await delete_messages(ids)


async def send_screen(peer_id: int, text: str, keyboard=None) -> None:
    """Показать новое сообщение бота, полностью очистив предыдущие."""
    await clear_screen(peer_id)

    kwargs = {
        "peer_id": peer_id,
        "message": text,
        "random_id": new_random_id(),
    }
    if keyboard:
        kwargs["keyboard"] = keyboard.get_json()

    result = await bot.api.messages.send(**kwargs)

    msg_id = extract_message_id(result)
    if msg_id is not None:
        last_message_ids.setdefault(peer_id, [])
        last_message_ids[peer_id].append(msg_id)
        # храним только последние 10 сообщений на пользователя
        last_message_ids[peer_id] = last_message_ids[peer_id][-10:]


def parse_payload(event: GroupTypes.MessageEvent) -> dict:
    """Распарсить payload из callback-кнопки."""
    payload = event.object.payload
    if isinstance(payload, str):
        try:
            return json.loads(payload)
        except (json.JSONDecodeError, TypeError):
            return {}
    return payload or {}


@bot.on.message()
async def text_handler(message: Message):
    """Единственный обработчик текстовых сообщений.

    Все текстовые команды обрабатываются здесь, поэтому бот никогда
    не отвечает на одно сообщение дважды.
    """
    text = (message.text or "").strip().lower()

    if text in GREETINGS:
        await send_screen(message.peer_id, START_TEXT, main_keyboard)
        return

    await send_screen(message.peer_id, UNKNOWN_TEXT, main_keyboard)


async def answer_callback(
    event: GroupTypes.MessageEvent,
    peer_id: int,
    snackbar: str,
    text: str,
    keyboard=None,
):
    """Ответить на нажатие callback-кнопки и обновить экран.

    Сначала показываем snackbar — это мгновенно убирает «крутилку» на кнопке,
    которую ВК держит, пока бот не ответит на событие. Только потом удаляем
    старое сообщение и отправляем новое.
    """
    try:
        await event.show_snackbar(snackbar)
    except Exception:
        pass

    await send_screen(peer_id, text, keyboard)


@bot.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=GroupTypes.MessageEvent)
async def callback_handler(event: GroupTypes.MessageEvent):
    """Обработчик нажатий на callback-кнопки."""
    payload = parse_payload(event)
    peer_id = event.object.peer_id

    if not peer_id:
        return

    menu = payload.get("menu")

    if menu == "services":
        await answer_callback(event, peer_id, "Услуги", SERVICES_TEXT, services_keyboard)

    elif menu == "price":
        await answer_callback(event, peer_id, "Прайс-лист", get_price_list(), price_keyboard)

    elif menu == "contact":
        await answer_callback(event, peer_id, "Связь с менеджером", CONTACT_TEXT, contact_keyboard)

    elif menu == "main":
        await answer_callback(event, peer_id, "Главное меню", MAIN_TEXT, main_keyboard)

    elif "service" in payload:
        service_id = payload.get("service", "")
        service = get_service_by_id(service_id)

        if service:
            await answer_callback(
                event, peer_id, service["name"], get_service_info(service), service_keyboard
            )
        else:
            await answer_callback(
                event, peer_id, "Услуга не найдена", SERVICE_NOT_FOUND_TEXT, main_keyboard
            )


async def cleanup_peer(peer_id: int) -> int:
    """Удалить все сообщения бота в одном диалоге. Возвращает число удалённых."""
    removed = 0
    offset = 0

    # 25 страниц по 200 сообщений — потолок, чтобы не крутиться вечно
    for _ in range(25):
        try:
            history = await bot.api.messages.get_history(
                peer_id=peer_id, count=200, offset=offset
            )
        except Exception:
            break

        own_ids = [m.id for m in history.items if m.from_id == -GROUP_ID]
        if own_ids:
            await delete_messages(own_ids)
            removed += len(own_ids)

        offset += 200
        if not history.items or offset >= history.count:
            break

    return removed


async def cleanup_history() -> None:
    """Удалить все сообщения бота во всех диалогах (очистка при старте)."""
    print("Очищаю историю сообщений бота...")
    removed = 0
    offset = 0

    try:
        while True:
            try:
                conversations = await bot.api.messages.get_conversations(
                    count=200, offset=offset
                )
            except Exception as exc:
                print(f"Не удалось получить диалоги: {exc}")
                break

            for item in conversations.items:
                peer_id = item.conversation.peer.id
                try:
                    removed += await cleanup_peer(peer_id)
                except Exception as exc:
                    print(f"Не удалось очистить диалог {peer_id}: {exc}")

            offset += 200
            if not conversations.items or offset >= conversations.count:
                break
    except Exception as exc:
        # Очистка не должна мешать боту запуститься
        print(f"Очистка истории прервана: {exc}")

    print(f"Очистка завершена, удалено сообщений: {removed}")


if __name__ == "__main__":
    print("Бот DetailPro запускается...")
    # Корутина выполнится до старта поллинга: удалим всю историю прошлой работы
    bot.on_startup.append(cleanup_history())
    bot.run()
