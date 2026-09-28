# Lê a entrada analógica da porta GPIO34 (ADC1), converte o valor bruto ($0$ a $4095$) para tensão ($0\text{ V}$ a $3.3\text{ V}$)
# calcula a intensidade relativa em porcentagem, monta o JSON e envia via MQTT com loop de tratamento de exceções.

# Arquivo: firmware_esp32/main.py
import machine
import time
import ujson
import config
from umqttsimple import MQTTClient

# Configuração do pino do sensor MQ-137 (GPIO34 = ADC1_CH6)
adc = machine.ADC(machine.Pin(34))
adc.atten(machine.ADC.ATTN_11DB) # Faixa de leitura até ~3.3V
adc.width(machine.ADC.WIDTH_12BIT) # Resolução de 12 bits (0 a 4095)

def read_sensor():
    # Amostragem (média de 10 leituras para suavizar o ruído)
    sum_adc = 0
    for _ in range(10):
        sum_adc += adc.read()
        time.sleep_ms(10)
    raw_adc = int(sum_adc / 10)
    
    voltage = round((raw_adc / 4095.0) * 3.3, 2)
    intensity_percent = min(100, max(0, int((raw_adc / 3500.0) * 100)))
    
    return raw_adc, voltage, intensity_percent

def main():
    print("Iniciando Firmware do Sensor de Odor...")
    client = MQTTClient(config.MQTT_CLIENT_ID, config.MQTT_BROKER, port=config.MQTT_PORT)
    
    try:
        client.connect()
        print("Conectado ao Broker MQTT com sucesso!")
    except Exception as e:
        print("Erro ao conectar ao Broker MQTT:", e)
        
    while True:
        try:
            raw, volt, intensity = read_sensor()
            
            payload = {
                "device_id": config.MQTT_CLIENT_ID,
                "raw_adc": raw,
                "voltage_v": volt,
                "intensity_percent": intensity,
                "sensor_status": "OK"
            }
            
            json_payload = ujson.dumps(payload)
            client.publish(config.MQTT_TOPIC_DATA, json_payload)
            print("[ESP32] Dados enviados:", json_payload)
            
            time.sleep(5)
            
        except Exception as e:
            print("Erro no ciclo principal / MQTT. Tentando reconectar...", e)
            time.sleep(5)
            try:
                client.connect()
            except:
                pass

if __name__ == "__main__":
    main()