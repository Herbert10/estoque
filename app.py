from flask import Flask, render_template, jsonify
import fdb
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)

# Conexão com banco Firebird
def get_firebird_connection():
    try:
        conn = fdb.connect(
            host=os.getenv("FIREBIRD_HOST", "127.0.0.1"),
            port=int(os.getenv("FIREBIRD_PORT", 3050)),
            database=os.getenv("FIREBIRD_DATABASE", "/caminho/para/seu_banco.fdb"),
            user=os.getenv("FIREBIRD_USER", "SYSDBA"),
            password=os.getenv("FIREBIRD_PASSWORD", "masterkey"),
            charset="UTF8"
        )
        return conn
    except Exception as e:
        print(f"Erro na conexão com Firebird: {e}")
        return None

# Função para buscar dados do banco
def fetch_data():
    conn = get_firebird_connection()
    if conn is None:
        return {"erro": "Não foi possível conectar ao banco Firebird"}

    try:
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
        print(f"Erro ao buscar dados: {e}")
        return {"erro": "Falha ao buscar dados no banco"}

# Rota principal - renderiza o template
@app.route("/")
def index():
    db_data = fetch_data()

    # Cards pré-definidos
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

    # Atribuir valores vindos do banco
    if "erro" not in db_data:
        for group, cards in grouped_cards.items():
            for card in cards:
                card["value"] = db_data.get(card["status"], 0)

    return render_template("index.html", grouped_cards=grouped_cards)

# Rota API para retorno dos dados em JSON
@app.route("/api/data")
def get_data():
    return jsonify(fetch_data())

# Inicializa a aplicação
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
