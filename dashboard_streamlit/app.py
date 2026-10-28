import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import time
import json
import os

# 1. Configuração da Página
st.set_page_config(
    page_title="Monitoramento de Odores",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Carregar CSS Externo
def carregar_css(nome_arquivo):
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_css = os.path.join(diretorio_atual, nome_arquivo)
    try:
        with open(caminho_css) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"Arquivo {nome_arquivo} não encontrado.")

carregar_css("style.css")

# 3. Inicialização do Firebase
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

# Cabeçalho Limpo
st.title("Monitoramento de Qualidade do Ar")
st.markdown("Sensor de Amônia **MQ-137** | Banheiro 01")
st.write("") 

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
        
    sinal_variacao = "+" if variacao > 0 else ""

    # Lógica de Cores Dinâmicas
    if intensidade < 40:
        cor_hex = "#00FF88" 
        estado_texto = "AMBIENTE PURIFICADO"
        icone = "✨"
    elif intensidade < 70:
        cor_hex = "#FFCC00" 
        estado_texto = "ODOR EM ELEVAÇÃO"
        icone = "⚠️"
    else:
        cor_hex = "#FF3366" 
        estado_texto = "HIGIENIZAÇÃO URGENTE"
        icone = "🚨"

    # 4. Super Card renderizado com as classes do style.css e cores em linha
    html_card = f"""
    <div class="super-card" style="border: 1px solid {cor_hex}50;">
        <span class="card-subtitle">Nível de Saturação Atual</span>
        
        <div class="card-number" style="color: {cor_hex}; text-shadow: 0 0 30px {cor_hex}40;">
            {intensidade}<span class="card-percent" style="color: {cor_hex}AA;">%</span>
        </div>
        
        <div class="card-status-text">
            {icone} {estado_texto}
        </div>
        
        <div class="card-metrics-footer">
            <span>Atualizado às: <b>{hora_atualizacao}</b></span>
            <span>|</span>
            <span>Tendência: <b>{sinal_variacao}{variacao}%</b></span>
        </div>
    </div>
    """
    
    st.markdown(html_card, unsafe_allow_html=True)
    
    # Gráfico 
    st.markdown('<h3 class="chart-title">📉 HISTÓRICO DAS ÚLTIMAS LEITURAS</h3>', unsafe_allow_html=True)
    df_grafico = df.iloc[::-1].set_index('Hora')[['intensity_percent']]
    st.area_chart(data=df_grafico, height=300, color=cor_hex)
    
    st.divider()
    
    with st.expander("Visualizar Matriz de Dados (Dev Mode)"):
        st.dataframe(df[['data_hora_legivel', 'intensity_percent', 'voltage_v', 'raw_adc']], use_container_width=True)
        
else:
    st.info("Aguardando os dados do sensor no Firebase...")

# Recarregamento automático
time.sleep(20)
st.rerun()