# Executado automaticamente ao ligar o ESP32. Ele configura a conexão Wi-Fi e só libera o sistema quando a rede estiver conectada.

import network
import time
import config

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print(f"Conectando à rede Wi-Fi '{config.WIFI_SSID}'...")
        wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
        
        timeout = 15
        while not wlan.isconnected() and timeout > 0:
            print(".", end="")
            time.sleep(1)
            timeout -= 1
            
    if wlan.isconnected():
        print("\nWi-Fi conectado com sucesso!")
        print("IP do ESP32:", wlan.ifconfig()[0])
    else:
        print("\nFalha ao conectar no Wi-Fi. Verifique as credenciais.")

connect_wifi()