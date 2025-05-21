from flask import Flask, request, jsonify
from datetime import datetime
import sqlite3

app = Flask(__name__)

def conectar_db():
    conn = sqlite3.connect("clientes.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/licenca", methods=["POST"])
def verificar_licenca():
    dados = request.get_json()
    senha = dados.get("senha")

    if not senha:
        return jsonify({"status": "erro", "mensagem": "Senha não fornecida"}), 400

    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM clientes WHERE senha = ?", (senha,))
    cliente = cur.fetchone()
    conn.close()

    if not cliente:
        return jsonify({"status": "bloqueado", "mensagem": "Senha inválida"}), 403

    if not cliente["ativo"]:
        return jsonify({"status": "bloqueado", "mensagem": "Licença bloqueada"}), 403

    validade = datetime.strptime(cliente["expira_em"], "%Y-%m-%d")
    if datetime.now() > validade:
        return jsonify({"status": "bloqueado", "mensagem": f"Licença expirada em {cliente['expira_em']}"}), 403

    return jsonify({"status": "ativo", "expira_em": cliente["expira_em"]})

@app.route("/initdb")
def initdb():
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            senha TEXT UNIQUE,
            expira_em TEXT,
            ativo INTEGER
        )
    """)
    conn.commit()
    conn.close()
    return "Banco de dados inicializado."

if __name__ == "__main__":
    app.run(debug=True)
