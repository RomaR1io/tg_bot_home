import paho.mqtt.client as mqtt

# Глобальные переменные для данных
current_temperature = None
current_humidity = None
mqtt_client = None
def on_connect(client, userdata, flags, rc):
    print("✅ Подключено к MQTT-брокеру")
    client.subscribe([("sensor/temperature", 0), ("sensor/humidity", 0)])

def on_message(client, userdata, msg):
    global current_temperature, current_humidity
    try:
        value = float(msg.payload.decode())
        if msg.topic == "sensor/temperature":
            current_temperature = value
        elif msg.topic == "sensor/humidity":
            current_humidity = value
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def publish(topic: str, message: str):
    """Отправка сообщения в MQTT-топик"""
    if mqtt_client:
        mqtt_client.publish(topic, message)
        print(f"📤 Отправлено в {topic}: {message}")
    else:
        print("❌ MQTT-клиент не инициализирован")
def start_mqtt():
    global mqtt_client
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect("5.189.40.94", 1883, 60)
    mqtt_client.loop_start()  # Неблокирующий режим