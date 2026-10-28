import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import time
import json

# Configuração da Página
st.set_page_config(
    page_title="Relatório Técnico - Sensor MQ-137",
    layout="wide"
)

# Inicialização do Firebase
@st.cache_resource
def init_firebase():
    if not firebase_admin._apps:
        if "FIREBASE_KEY" in st.secrets:
            key_dict = json.loads(st.secrets["FIREBASE_KEY"])
            cred = credentials.Certificate(key_dict)
        else:
            cred = credentials.Certificate("backend_python/serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
    return firestore.client()

db = init_firebase()

# Cabeçalho Formal
st.title("Relatório Técnico: Monitoramento de Qualidade do Ar")
st.markdown("Registro contínuo dos níveis de concentração de compostos orgânicos voláteis (COVs) e amônia via sensor IoT MQ-137.")
st.divider()

def fetch_data():
    docs = db.collection("leituras_odor").order_by(
        "timestamp", direction=firestore.Query.DESCENDING
    ).limit(20).stream()
    
    dados = []
    for doc in docs:
        dados.append(doc.to_dict())
    return dados

dados_sensor = fetch_data()

if dados_sensor:
    df = pd.DataFrame(dados_sensor)
    df['Hora'] = pd.to_datetime(df['data_hora_legivel']).dt.strftime('%H:%M:%S')
    
    leitura_atual = df.iloc[0]
    intensidade = leitura_atual['intensity_percent']
    hora_atualizacao = leitura_atual['Hora']
    
    if len(df) > 1:
        intensidade_anterior = df.iloc[1]['intensity_percent']
        variacao = intensidade - intensidade_anterior
    else:
        variacao = 0

    # Lógica de Classificação Científica
    if intensidade < 40:
        status = "Nível Aceitável"
        alerta = st.success
    elif intensidade < 70:
        status = "Elevação Detectada"
        alerta = st.warning
    else:
        status = "Saturação Crítica"
        alerta = st.error

    # Seção 1: Resumo Atual
    st.subheader("1. Síntese dos Dados Atuais")
    alerta(f"Diagnóstico de Ambiente: {status} (Intensidade relativa de {intensidade}% registrada às {hora_atualizacao}).")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="Intensidade de Odor", value=f"{intensidade}%", delta=f"{variacao}%", delta_color="inverse")
    col2.metric(label="Tensão Elétrica Lida", value=f"{leitura_atual.get('voltage_v', 0):.2f} V")
    col3.metric(label="Sinal Analógico (ADC)", value=leitura_atual.get('raw_adc', 0))
    col4.metric(label="Status do Hardware", value=leitura_atual.get('sensor_status', 'OK'))

    st.divider()
    
    # Seção 2: Gráfico
    st.subheader("2. Evolução Temporal da Concentração")
    df_grafico = df.iloc[::-1].set_index('Hora')[['intensity_percent']]
    st.line_chart(data=df_grafico, height=350)
    
    st.divider()
    
    # Seção 3: Tabela Aberta e Renomeada
    st.subheader("3. Matriz de Registros Analíticos")
    st.markdown("Amostragem bruta das últimas 20 leituras capturadas no banco de dados Firestore.")
    
    df_display = df[['data_hora_legivel', 'intensity_percent', 'voltage_v', 'raw_adc', 'sensor_status']].copy()
    df_display.columns = ['Data e Hora do Registro', 'Intensidade (%)', 'Tensão (V)', 'ADC Bruto', 'Integridade']
    st.dataframe(df_display, use_container_width=True)
        
else:
    st.info("Aguardando sincronização de dados com o servidor MQTT/Firebase...")

# Rodapé de atualização
st.caption("Protocolo de amostragem configurado para atualização automática a cada 20 segundos.")
time.sleep(20)
st.rerun()