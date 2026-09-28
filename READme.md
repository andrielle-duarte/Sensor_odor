# 📡 Monitoramento Inteligente de Odores (MQ-137)

## Guia de Execução Local

Os passos para configurar e executar o projeto localmente, incluindo Backend, Dashboard e Simulador.

### 1. Pré-requisitos

- Python 3.9 ou superior
- VS Code
- Git

### 2. Clonar o repositório

```bash
git clone https://github.com/andrielle-duarte/Sensor_odor.git
cd Sensor_odor
```

Abra a pasta no VS Code.

### 3. Configurar o Firebase

1. Acesse o [Firebase Console](https://console.firebase.google.com/) e crie um projeto.
2. Ative o **Firestore Database** em modo de teste.
3. Em **Configurações do projeto → Contas de serviço**, gere uma chave privada.
4. Renomeie o arquivo baixado para `serviceAccountKey.json` e coloque-o na pasta `backend_python/`.

> Não compartilhe nem envie esse arquivo ao GitHub, pois contém credenciais privadas. Usar .gitignore.

### 4. Configurar o ambiente Python

Crie e ative o ambiente virtual:

```bash
python -m venv .venv
```

**Windows:**

```powershell
.\.venv\Scripts\activate
```

**Linux/Mac:**

```bash
source .venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

### 5. Executar o projeto

Abra três terminais no VS Code, com o ambiente virtual ativado em cada um.

**Terminal 1 — Backend**

```bash
python backend_python/main.py
```

**Terminal 2 — Dashboard**

```bash
streamlit run dashboard_streamlit/app.py
```

**Terminal 3 — Simulador**

```bash
python backend_python/simulator.py
```

### 6. Verificar o funcionamento

Acesse o dashboard em http://localhost:8501.

Com os três componentes em execução, o sistema deverá:

- Receber dados via MQTT.
- Armazenar informações no Firebase.
- Atualizar os gráficos e indicadores do dashboard.
- Exibir alertas conforme os níveis de odor detectados.

**Repositório:** [Sensor_odor](https://github.com/andrielle-duarte/Sensor_odor)
