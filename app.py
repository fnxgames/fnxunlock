from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

@app.route("/licenca", methods=["POST"])
def verificar_licenca():
    data = request.json
    senha = data.get("senha")

    conn = sqlite3.connect("clientes.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM clientes WHERE senha = ?", (senha,))
    cliente = cur.fetchone()
    conn.close()

    if not cliente:
        return jsonify({"mensagem": "Senha inválida", "status": "bloqueado"})

    if not cliente["ativo"]:
        return jsonify({"mensagem": "Licença desativada", "status": "bloqueado"})

    return jsonify({"status": "ativo", "expira_em": cliente["expira_em"]})

@app.route("/novo_cliente", methods=["POST"])
def novo_cliente():
    data = request.json
    nome = data.get("nome")
    senha = data.get("senha")
    expira_em = data.get("expira_em")
    ativo = data.get("ativo", 0)

    if not senha or not expira_em:
        return jsonify({"erro": "Campos obrigatórios faltando."}), 400

    conn = sqlite3.connect("clientes.db")
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO clientes (nome, senha, expira_em, ativo)
            VALUES (?, ?, ?, ?)
        """, (nome, senha, expira_em, ativo))
        conn.commit()
        return jsonify({"mensagem": "Cliente criado com sucesso."}), 201
    except sqlite3.IntegrityError:
        return jsonify({"erro": "Senha já existe."}), 409
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        conn.close()

@app.route("/clientes", methods=["GET"])
def listar_clientes():
    token = request.args.get("token")
    if token != "2939Melv1n":
        return jsonify({"erro": "Acesso não autorizado"}), 403

    conn = sqlite3.connect("clientes.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM clientes")
    dados = cur.fetchall()
    conn.close()
    return jsonify([dict(d) for d in dados])

@app.route("/alterar_status", methods=["POST"])
def alterar_status():
    data = request.json
    cliente_id = data.get("id")
    ativo = data.get("ativo")

    if cliente_id is None or ativo is None:
        return jsonify({"erro": "Dados incompletos"}), 400

    conn = sqlite3.connect("clientes.db")
    cur = conn.cursor()
    cur.execute("UPDATE clientes SET ativo = ? WHERE id = ?", (ativo, cliente_id))
    conn.commit()
    conn.close()

    return jsonify({"mensagem": "Status atualizado com sucesso"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
