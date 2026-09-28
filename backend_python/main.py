# Arquivo: backend_python/main.py
import json
import paho.mqtt.client as mqtt
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import datetime

# --- CONFIGURAÇÕES ---
BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "projeto/sensor_odor/banheiro_01/dados"
CLIENT_ID = "backend_python_consumidor_01"

# --- INICIALIZAÇÃO DO FIREBASE ---
try:
    # O caminho pressupõe que você rodará o script a partir da raiz do projeto
    cred = credentials.Certificate("backend_python/serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Firebase conectado com sucesso!")
except Exception as e:
    print(f"Erro ao inicializar o Firebase. Verifique o arquivo JSON. Erro: {e}")
    exit()

# --- FUNÇÕES DO MQTT ---
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Conectado ao Broker MQTT: {BROKER}")
    client.subscribe(TOPIC)
    print(f"Inscrito e aguardando dados no tópico: {TOPIC}...\n")

def on_message(client, userdata, msg):
    try:
        # 1. Recebe e decodifica a mensagem JSON do MQTT
        payload = msg.payload.decode("utf-8")
        dados = json.loads(payload)
        
        # 2. Adiciona a data e hora em que o dado chegou ao servidor
        data_atual = datetime.datetime.now()
        dados["timestamp"] = data_atual
        dados["data_hora_legivel"] = data_atual.strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"[MENSAGEM RECEBIDA] Odor Relativo: {dados.get('intensity_percent')}% | ADC: {dados.get('raw_adc')}")
        
        # 3. Salva os dados na coleção 'leituras_odor' do Firestore
        # O Firestore é um banco NoSQL, então ele aceita o dicionário Python diretamente[cite: 1]
        db.collection("leituras_odor").add(dados)
        print("Dado persistido no Firebase Firestore com sucesso!\n")
        
    except json.JSONDecodeError:
        print("Erro: Mensagem recebida não é um JSON válido.")
    except Exception as e:
        print(f"Erro ao processar ou salvar a mensagem: {e}")

# --- INICIALIZAÇÃO DO CLIENTE MQTT ---
client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    client_id=CLIENT_ID,
    protocol=mqtt.MQTTv5
)
client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect(BROKER, PORT, 60)
    # Mantém o script rodando infinitamente escutando novas mensagens
    client.loop_forever()
except KeyboardInterrupt:
    print("\nBackend encerrado pelo usuário.")
    client.disconnect()