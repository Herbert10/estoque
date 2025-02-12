from flask import Flask, render_template, jsonify
import fdb
import os
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

app = Flask(__name__)
if os.getenv("HEROKU") == "true":
    fdb.load_api("firebird_lib/libfbclient.so")

# Conexão com banco Firebird
def get_firebird_connection():
    return fdb.connect(
        host=os.getenv("FIREBIRD_HOST"),
        port=int(os.getenv("FIREBIRD_PORT")),
        database=os.getenv("FIREBIRD_DATABASE"),
        user=os.getenv("FIREBIRD_USER"),
        password=os.getenv("FIREBIRD_PASSWORD"),
    )

# Consulta ao banco
def fetch_data():
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

@app.route("/")
def index():
    db_data = fetch_data()

    # Cards
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

    # Atribuir valores pelos dados do banco
    for group, cards in grouped_cards.items():
        for card in cards:
            card["value"] = db_data.get(card["status"], 0)

    return render_template("index.html", grouped_cards=grouped_cards)

@app.route("/api/data")
def get_data():
    db_data = fetch_data()
    return jsonify(db_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000 )

