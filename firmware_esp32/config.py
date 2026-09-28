# Armazena SSID, senha e tópicos do MQTT para fácil manutenção.
# Configurações da Rede Wi-Fi
WIFI_SSID = "nome da rede" #nome da nossa rede do ESP32
WIFI_PASSWORD = "a nossa senha" #senha da nossa rede do ESP32

# Configurações do Broker MQTT (Utilizaremos o HiveMQ público para testes)
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC_DATA = "projeto/sensor_odor/banheiro_01/dados"
MQTT_TOPIC_STATUS = "projeto/sensor_odor/banheiro_01/status"
MQTT_CLIENT_ID = "esp32_sensor_odor_01"