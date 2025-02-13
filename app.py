from flask import Flask, render_template, jsonify
import os
import requests
import fdb
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

app = Flask(__name__)

# Detecta se está rodando no Render (sem Firebird instalado)
USE_FIREBIRD_API = os.getenv("USE_FIREBIRD_API", "false").lower() == "true"

# URL da API Firebird (se rodando no Render)
FIREBIRD_API_URL = os.getenv("FIREBIRD_API_URL", "http://alfadash.ddns.net:5001/api/firebird-data")


# 🔹 1️⃣ Função para buscar os dados do Firebird (quando rodando localmente)
def get_firebird_connection():
    return fdb.connect(
        host=os.getenv("FIREBIRD_HOST", "127.0.0.1"),
        port=int(os.getenv("FIREBIRD_PORT", 3050)),
        database=os.getenv("FIREBIRD_DATABASE", "/caminho/para/seu_banco.fdb"),
        user=os.getenv("FIREBIRD_USER", "SYSDBA"),
        password=os.getenv("FIREBIRD_PASSWORD", "masterkey"),
    )


# 🔹 2️⃣ Função para buscar dados, conectando ao Firebird local ou à API Firebird remota
def fetch_data():
    if USE_FIREBIRD_API:
        try:
            response = requests.get(FIREBIRD_API_URL, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"erro": f"Falha ao conectar à API Firebird: {str(e)}"}
    else:
        try:
            conn = get_firebird_connection()
            cursor = conn.cursor()

            query = """
                SELECT PV.STATUS_WORKFLOW, COUNT(PV.PEDIDOV) AS QUANTIDADE
                FROM PEDIDO_VENDA PV
                WHERE PV.EFETUADO = 'F'
                GROUP BY PV.STATUS_WORKFLOW;
            """
            cursor.execute(query)
            result = cursor.fetchall()
            conn.close()
            return {str(row[0]): row[1] for row in result}
        except Exception as e:
            return {"erro": f"Erro na conexão com Firebird: {str(e)}"}


@app.route("/")
def index():
    db_data = fetch_data()

    grouped_cards = {
        "Personalizado": [
            {"label": "Aguardando impressão personalizado", "status": "47", "filial": "2", "tipo_pedido": "13"}
        ],
        "Fluxo de Pedidos": [
            {"label": "Aguardando impressão prioritário", "status": "47", "filial": "2"},
            {"label": "Aguardando impressão", "status": "45", "filial": "2"},
            {"label": "Aguardando atribuição de separador prioritário", "status": "148", "filial": "2"},
            {"label": "Aguardando atribuição de separador", "status": "149", "filial": "2"},
            {"label": "Aguardando separação prioritário", "status": "30", "filial": "2"},
            {"label": "Aguardando separação", "status": "4", "filial": "2"},
            {"label": "Aguardando conferência prioritário", "status": "32", "filial": "2"},
            {"label": "Aguardando conferência", "status": "6", "filial": "2"},
        ],
        "Enviar para Zanzibar": [
            {"label": "Aguardando impressão agrupamento prioritário", "status": "156", "filial": "14"},
            {"label": "Aguardando impressão agrupamento", "status": "153", "filial": "14"},
            {"label": "Aguardando separação agrupamento prioritário", "status": "155", "filial": "14"},
            {"label": "Aguardando separação agrupamento", "status": "152", "filial": "14"},
        ],
        "Aguardando chegar da Zanzibar": [
            {"label": "Aguardando retorno agrupamento prioritário", "status": "157", "filial": "2"},
            {"label": "Aguardando retorno agrupamento", "status": "146", "filial": "2"},
        ],
    }

    # Atribuir valores vindos dos dados recebidos
    if "erro" not in db_data:
        for group, cards in grouped_cards.items():
            for card in cards:
                status_str = str(card["status"])
                card["value"] = db_data.get(status_str, 0)

    return render_template("index.html", grouped_cards=grouped_cards)


@app.route("/api/data")
def get_data():
    return jsonify(fetch_data())


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
