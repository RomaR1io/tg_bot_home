import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from mqtt import publish
from functools import wraps
import os
import subprocess
# Инициализация бота
logging.basicConfig(level=logging.INFO)
bot = Bot(token="7564675362:AAHrVXjlLHJUI9_AzH9VG3oHqoV3kc5Z7kY")
dp = Dispatcher()
ALLOWED_USERS = {566737402}

def auth(func):
    """Декоратор для ограничения доступа"""
    @wraps(func)
    async def wrapper(message: types.Message | types.CallbackQuery, *args, **kwargs):
        user_id = message.from_user.id
        if user_id not in ALLOWED_USERS:
            if isinstance(message, types.Message):
                await message.answer("⛔ Доступ запрещен!")
            elif isinstance(message, types.CallbackQuery):
                await message.answer("Доступ запрещен!", show_alert=True)
            return
        return await func(message, *args, **kwargs)
    return wrapper


def is_pc_on(ip_address: str) -> bool:
    try:
        # Пинг компьютера
        subprocess.check_output(["ping", "-n", "1", ip_address], timeout=2)

        # Проверка ARP-таблицы (только Windows)
        arp_output = subprocess.check_output(["arp", "-a", ip_address]).decode()
        return "00-00-00-00-00-00" not in arp_output  # Если MAC не нулевой
    except:
        return False



# Хэндлеры
@dp.message(Command("start"))
@auth
async def cmd_start(msg: types.Message):
    kb = [
        [types.KeyboardButton(text="Управление ПК"),
         types.KeyboardButton(text="Управление в комнате")]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )
    await msg.answer(
        "Доброго времени суток, вас приветствует личный помощник по дому",
        reply_markup=keyboard
    )

@dp.message(F.text.lower() == "управление пк")
@auth
async def menu_pc(message: types.Message):
    if is_pc_on("192.168.0.46"):
        status="Включен"
    else: status="Выключен"
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="Включить ПК",))
    await message.answer(f"Статус ПК {status} \nМеню управления ПК!")


@dp.message(F.text.lower() == "управление в комнате")
@auth
async def menu_room(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="🌡️ Температура", callback_data="room_temp"),
        types.InlineKeyboardButton(text="💧 Влажность", callback_data="room_hum")
    )
    builder.row(
        types.InlineKeyboardButton(text="💡 Включить свет у Алисы", callback_data="light_on_a"),
        types.InlineKeyboardButton(text="🔌 Выключить свет у Алисы", callback_data="light_off_a")
    )
    builder.row(
        types.InlineKeyboardButton(text="💡 Включить свет в комнате", callback_data="light_on_me"),
        types.InlineKeyboardButton(text="🔌 Выключить свет в комнате", callback_data="light_off_me")
    )
    await message.answer(
        "Меню управления в комнате:",
        reply_markup=builder.as_markup()
    )

@dp.callback_query(F.data == "room_temp")
@auth
async def send_temp(callback: types.CallbackQuery):
    from mqtt import current_temperature
    await callback.message.answer(f"Текущая температура: {current_temperature}°C")
    await callback.answer()

@dp.callback_query(F.data == "room_hum")
@auth
async def send_hum(callback: types.CallbackQuery):
    from mqtt import current_humidity
    await callback.message.answer(f"Текущая влажность: {current_humidity}%")
    await callback.answer()

@dp.callback_query(F.data == "light_on_a")
@auth
async def turn_light_on(callback: types.CallbackQuery):
    publish("room/light", "ON_a")  # Отправляем команду в MQTT
    await callback.message.answer("✅ Свет включен")
    await callback.answer()

@dp.callback_query(F.data == "light_off_a")
@auth
async def turn_light_off(callback: types.CallbackQuery):
    publish("room/light", "OFF_a")  # Отправляем команду в MQTT
    await callback.message.answer("🔌 Свет выключен")
    await callback.answer()

@dp.callback_query(F.data == "light_on_me")
@auth
async def turn_light_on(callback: types.CallbackQuery):
    publish("room/light", "ON_me")  # Отправляем команду в MQTT
    await callback.message.answer("✅ Свет включен")
    await callback.answer()

@dp.callback_query(F.data == "light_off_me")
@auth
async def turn_light_off(callback: types.CallbackQuery):
    publish("room/light", "OFF_me")  # Отправляем команду в MQTT
    await callback.message.answer("🔌 Свет выключен")
    await callback.answer()