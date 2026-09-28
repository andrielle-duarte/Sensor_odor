import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import time
import json

st.set_page_config(
    page_title="Monitorização de Odores",
    layout="wide"
)

@st.cache_resource
def init_firebase():
    if not firebase_admin._apps:
        # 1. Verifica se estamos na nuvem 
        if "FIREBASE_KEY" in st.secrets:
            # Lê o segredo da nuvem e converte de texto para dicionário
            key_dict = json.loads(st.secrets["FIREBASE_KEY"])
            cred = credentials.Certificate(key_dict)
        # 2. Se não estiver na nuvem, tenta usar o ficheiro local
        else:
            cred = credentials.Certificate("backend_python/serviceAccountKey.json")
            
        firebase_admin.initialize_app(cred)
    return firestore.client()

db = init_firebase()

st.title("Painel de Monitorização - Sensor de Odor")
st.markdown("Acompanhamento em tempo real da qualidade do ar nos banheiros.")

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
    leitura_atual = df.iloc[0]
    intensidade = leitura_atual['intensity_percent']
    
    st.subheader("Banheiro 01 - Estado Atual")
    
    # Lógica de Alertas baseada na intensidade
    if intensidade < 40:
        st.success(f"✅ **Ambiente OK** - O nível de odor está aceitável ({intensidade}%).")
        estado_texto = "Normal"
    elif intensidade < 70:
        st.warning(f"⚠️ **Atenção** - O nível de odor está a aumentar ({intensidade}%).")
        estado_texto = "Atenção"
    else:
        st.error(f"🚨 **ALERTA DE LIMPEZA** - Nível de odor elevado detetado ({intensidade}%)! Ação necessária imediata.")
        estado_texto = "Elevado"
    
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Intensidade Relativa do Odor", value=f"{intensidade}%")
    col2.metric(label="Classificação", value=estado_texto)
    col3.metric(label="Última Atualização", value=leitura_atual['data_hora_legivel'])
    
    st.divider()
    
    st.subheader("Histórico Recente de Intensidade (%)")
    df_grafico = df.iloc[::-1].reset_index(drop=True)
    st.line_chart(data=df_grafico, x="data_hora_legivel", y="intensity_percent")
    
    with st.expander("Ver dados brutos recebidos"):
        st.dataframe(df[['data_hora_legivel', 'intensity_percent', 'voltage_v', 'raw_adc']])
        
else:
    st.info("Aguardando os dados do sensor no Firebase...")
# Opcional: Mostrar um pequeno aviso visual de que a página está a ser atualizada
st.caption("Atualiza cada 5 segundos...")

# Aguarda 5 segundos e força a página a recarregar-se sozinha
time.sleep(5)
st.rerun()