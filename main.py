import asyncio
from threading import Thread
from bot import dp, bot
from mqtt import  start_mqtt

async def run_bot():
    await dp.start_polling(bot)

if __name__ == "__main__":
    # Запуск MQTT в отдельном потоке
    mqtt_thread = Thread(target=start_mqtt, daemon=True)
    mqtt_thread.start()

    # Запуск бота в основном потоке
    asyncio.run(run_bot())