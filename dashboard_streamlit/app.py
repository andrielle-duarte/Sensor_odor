import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import time
import json
import os

# 1. Configuração da Página
st.set_page_config(
    page_title="Monitoramento de Odores",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Função para carregar o CSS externo
def carregar_css(nome_arquivo):
    # Pega o caminho absoluto da pasta atual
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_css = os.path.join(diretorio_atual, nome_arquivo)
    
    try:
        with open(caminho_css) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"Arquivo {nome_arquivo} não encontrado. O layout padrão será exibido.")

# Chama o arquivo CSS (certifique-se de ter criado o arquivo style.css na mesma pasta)
carregar_css("style.css")

# 3. Inicialização do Firebase
@st.cache_resource
def init_firebase():
    if not firebase_admin._apps:
        # Verifica se estamos na nuvem 
        if "FIREBASE_KEY" in st.secrets:
            # Lê o segredo da nuvem e converte de texto para dicionário
            key_dict = json.loads(st.secrets["FIREBASE_KEY"])
            cred = credentials.Certificate(key_dict)
        # Se não estiver na nuvem, tenta usar o arquivo local
        else:
            cred = credentials.Certificate("backend_python/serviceAccountKey.json")
            
        firebase_admin.initialize_app(cred)
    return firestore.client()

db = init_firebase()

# Cabeçalho do Dashboard
st.title("🎛️ Centro de Comando - Qualidade do Ar")
st.markdown("Monitoramento IoT em tempo real de concentração de amônia (Banheiro 01).")
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
    
    # Extrair apenas a hora para o eixo do gráfico ficar mais limpo
    df['Hora'] = pd.to_datetime(df['data_hora_legivel']).dt.strftime('%H:%M:%S')
    
    # Leitura atual (a mais recente)
    leitura_atual = df.iloc[0]
    intensidade = leitura_atual['intensity_percent']
    hora_atualizacao = leitura_atual['Hora']
    
    # Calcular a variação (Delta) em relação à leitura anterior
    if len(df) > 1:
        intensidade_anterior = df.iloc[1]['intensity_percent']
        variacao = intensidade - intensidade_anterior
    else:
        variacao = 0

    # Layout de Dashboard em 2 Colunas (Esquerda: Alertas, Direita: Gráfico)
    coluna_esquerda, coluna_direita = st.columns([1, 2.5]) 
    
    with coluna_esquerda:
        st.subheader("📡 Status em Tempo Real")
        
        # Lógica de Alertas baseada na intensidade
        if intensidade < 40:
            st.success(f"✅ **QUALIDADE IDEAL**\n\nO nível de odor está aceitável ({intensidade}%).")
            estado_texto = "Normal"
        elif intensidade < 70:
            st.warning(f"⚠️ **ATENÇÃO REQUERIDA**\n\nO nível de odor está a aumentar ({intensidade}%).")
            estado_texto = "Em Elevação"
        else:
            st.error(f"🚨 **HIGIENIZAÇÃO URGENTE**\n\nNível crítico detectado ({intensidade}%).")
            estado_texto = "Crítico"
        
        # Métricas em formato de Cards
        st.metric(label="Odor Relativo", value=f"{intensidade}%", delta=f"{variacao}% (Variação)", delta_color="inverse")
        st.metric(label="Classificação", value=estado_texto)
        st.metric(label="Última Sincronização", value=hora_atualizacao)
        
        # Barra de preenchimento
        st.progress(intensidade / 100, text="Capacidade Crítica (100%)")
        
    with coluna_direita:
        st.subheader("📈 Histórico de Saturação")
        # Inverte a ordem para o gráfico ficar cronológico (do mais antigo para o mais novo) e define a 'Hora' como eixo X
        df_grafico = df.iloc[::-1].set_index('Hora')[['intensity_percent']]
        st.area_chart(data=df_grafico, height=350)
    
    st.divider()
    
    with st.expander("🛠️ Modo Desenvolvedor: Inspecionar Dados Brutos"):
        st.dataframe(df[['data_hora_legivel', 'intensity_percent', 'voltage_v', 'raw_adc']], use_container_width=True)
        
else:
    st.info("Aguardando os dados do sensor no Firebase...")

# Aviso visual discreto
st.caption("Atualiza automaticamente a cada 20 segundos...")

# Aguarda 20 segundos e força a página a recarregar-se sozinha
time.sleep(20)
st.rerun()