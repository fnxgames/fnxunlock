# painel_admin_remoto.py
import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QCheckBox, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt
from datetime import datetime

API_URL_CADASTRO = "https://fnxunlock.onrender.com/novo_cliente"
API_URL_LISTA = "https://fnxunlock.onrender.com/clientes"
API_URL_STATUS = "https://fnxunlock.onrender.com/alterar_status"

class AdminWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Painel Remoto de Licenciamento")
        self.setGeometry(100, 100, 1000, 500)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Formulário de cadastro
        form_layout = QHBoxLayout()
        self.nome_input = QLineEdit()
        self.nome_input.setPlaceholderText("Nome")
        self.senha_input = QLineEdit()
        self.senha_input.setPlaceholderText("Senha")
        self.expira_input = QLineEdit()
        self.expira_input.setPlaceholderText("Expira em (AAAA-MM-DD)")
        self.ativo_checkbox = QCheckBox("Ativo")
        self.add_button = QPushButton("Cadastrar Cliente")
        self.add_button.clicked.connect(self.enviar_para_api)

        form_layout.addWidget(self.nome_input)
        form_layout.addWidget(self.senha_input)
        form_layout.addWidget(self.expira_input)
        form_layout.addWidget(self.ativo_checkbox)
        form_layout.addWidget(self.add_button)
        self.layout.addLayout(form_layout)

        # Tabela de clientes
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Nome", "Senha", "Expira em", "Ativo", "Ação"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.table)

        self.carregar_clientes()

    def carregar_clientes(self):
        try:
            resposta = requests.get(API_URL_LISTA)
            dados = resposta.json()
            self.table.setRowCount(len(dados))
            for i, cliente in enumerate(dados):
                self.table.setItem(i, 0, QTableWidgetItem(str(cliente["id"])))
                self.table.setItem(i, 1, QTableWidgetItem(cliente["nome"]))
                self.table.setItem(i, 2, QTableWidgetItem(cliente["senha"]))
                self.table.setItem(i, 3, QTableWidgetItem(cliente["expira_em"]))
                self.table.setItem(i, 4, QTableWidgetItem("Sim" if cliente["ativo"] else "Não"))

                botao = QPushButton("Ativar" if not cliente["ativo"] else "Desativar")
                botao.clicked.connect(lambda _, cid=cliente["id"], novo=not cliente["ativo"]: self.atualizar_status(cid, novo))
                self.table.setCellWidget(i, 5, botao)

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar clientes:\n{e}")

    def enviar_para_api(self):
        nome = self.nome_input.text()
        senha = self.senha_input.text()
        expira_em = self.expira_input.text()
        ativo = 1 if self.ativo_checkbox.isChecked() else 0

        try:
            datetime.strptime(expira_em, "%Y-%m-%d")
        except ValueError:
            QMessageBox.warning(self, "Erro", "Data inválida. Use o formato AAAA-MM-DD.")
            return

        payload = {
            "nome": nome,
            "senha": senha,
            "expira_em": expira_em,
            "ativo": ativo
        }

        try:
            resposta = requests.post(API_URL_CADASTRO, json=payload)
            if resposta.status_code == 201:
                QMessageBox.information(self, "Sucesso", "Cliente cadastrado com sucesso.")
                self.nome_input.clear()
                self.senha_input.clear()
                self.expira_input.clear()
                self.ativo_checkbox.setChecked(False)
                self.carregar_clientes()
            elif resposta.status_code == 409:
                QMessageBox.warning(self, "Erro", "Essa senha já está cadastrada.")
            else:
                QMessageBox.warning(self, "Erro", f"Erro: {resposta.text}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao enviar dados:\n{e}")

    def atualizar_status(self, cliente_id, novo_status):
        try:
            resposta = requests.post(API_URL_STATUS, json={"id": cliente_id, "ativo": int(novo_status)})
            if resposta.status_code == 200:
                self.carregar_clientes()
            else:
                QMessageBox.warning(self, "Erro", f"Erro ao atualizar status: {resposta.text}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha na requisição:\n{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = AdminWindow()
    janela.show()
    sys.exit(app.exec_())

@app.route("/clientes", methods=["GET"])
def listar_clientes():
    conn = sqlite3.connect("clientes.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM clientes")
    dados = cur.fetchall()
    conn.close()
    return jsonify([dict(d) for d in dados])
