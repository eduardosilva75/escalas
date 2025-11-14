# ferias.py
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QComboBox, QDateEdit, QMessageBox, QHeaderView,
    QGroupBox, QFormLayout, QInputDialog, QLineEdit
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor
from datetime import datetime
from database import DatabaseManager


class FeriasDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.pessoas = {}
        self.ferias_cache = []
        self.initUI()
        self.carregar_pessoas()
        self.carregar_ferias()

    def initUI(self):
        self.setWindowTitle("Gestão de Férias")
        self.setGeometry(100, 100, 900, 600)
        layout = QVBoxLayout()

        # Título
        title = QLabel("Gestão de Férias")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("margin: 10px; color: #2c3e50;")
        layout.addWidget(title)

        # Formulário
        form_group = QGroupBox("Adicionar / Editar Férias")
        form_layout = QFormLayout()

        # Pessoa
        self.combo_pessoa = QComboBox()
        form_layout.addRow("Pessoa:", self.combo_pessoa)

        # Datas
        self.date_inicio = QDateEdit()
        self.date_inicio.setCalendarPopup(True)
        self.date_inicio.setDate(QDate.currentDate())
        form_layout.addRow("Data Início:", self.date_inicio)

        self.date_fim = QDateEdit()
        self.date_fim.setCalendarPopup(True)
        self.date_fim.setDate(QDate.currentDate())
        form_layout.addRow("Data Fim:", self.date_fim)

        # Descrição
        self.input_descricao = QLineEdit()
        self.input_descricao.setPlaceholderText("Ex: Férias de Verão")
        form_layout.addRow("Descrição:", self.input_descricao)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Botões de ação
        btn_layout = QHBoxLayout()
        btn_adicionar = QPushButton("Adicionar Férias")
        btn_adicionar.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 8px;")
        btn_adicionar.clicked.connect(self.adicionar_ferias)

        btn_editar = QPushButton("Editar Selecionada")
        btn_editar.setStyleSheet("background-color: #f39c12; color: white; font-weight: bold; padding: 8px;")
        btn_editar.clicked.connect(self.editar_ferias)

        btn_apagar = QPushButton("Apagar Selecionada")
        btn_apagar.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold; padding: 8px;")
        btn_apagar.clicked.connect(self.apagar_ferias)

        btn_layout.addWidget(btn_adicionar)
        btn_layout.addWidget(btn_editar)
        btn_layout.addWidget(btn_apagar)
        layout.addLayout(btn_layout)

        # Tabela
        layout.addWidget(QLabel("Férias Registadas:"))
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels(["ID", "Pessoa", "Início", "Fim", "Descrição"])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.tabela)

        # Botão fechar
        btn_fechar = QPushButton("Fechar")
        btn_fechar.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        btn_fechar.clicked.connect(self.close)
        layout.addWidget(btn_fechar)

        self.setLayout(layout)

    def carregar_pessoas(self):
        pessoas = self.db.get_pessoas()
        self.pessoas = {}
        self.combo_pessoa.clear()
        for p in pessoas:
            nome = p['nome']
            pid = p['id']
            self.pessoas[nome] = pid
            self.combo_pessoa.addItem(nome)

    def carregar_ferias(self):
        self.ferias_cache = self.db.get_ferias()
        self.tabela.setRowCount(0)
        for ferias in self.ferias_cache:
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            self.tabela.setItem(row, 0, QTableWidgetItem(str(ferias.get('id', ''))))
            self.tabela.setItem(row, 1, QTableWidgetItem(ferias['nome']))
            self.tabela.setItem(row, 2, QTableWidgetItem(ferias['data_inicio']))
            self.tabela.setItem(row, 3, QTableWidgetItem(ferias['data_fim']))
            self.tabela.setItem(row, 4, QTableWidgetItem(ferias.get('descricao', '')))

    def adicionar_ferias(self):
        nome = self.combo_pessoa.currentText()
        if not nome:
            QMessageBox.warning(self, "Erro", "Selecione uma pessoa!")
            return

        inicio = self.date_inicio.date().toString('yyyy-MM-dd')
        fim = self.date_fim.date().toString('yyyy-MM-dd')
        descricao = self.input_descricao.text().strip()

        if self.date_inicio.date() > self.date_fim.date():
            QMessageBox.warning(self, "Erro", "Data de início deve ser antes da data de fim!")
            return

        pessoa_id = self.pessoas[nome]

        # Verificar sobreposição
        for f in self.ferias_cache:
            if f['nome'] == nome:
                fi = datetime.strptime(f['data_inicio'], '%Y-%m-%d').date()
                ff = datetime.strptime(f['data_fim'], '%Y-%m-%d').date()
                ni = datetime.strptime(inicio, '%Y-%m-%d').date()
                nf = datetime.strptime(fim, '%Y-%m-%d').date()
                if not (nf < fi or ni > ff):
                    QMessageBox.warning(self, "Sobreposição", f"Férias já existem entre {f['data_inicio']} e {f['data_fim']}")
                    return

        success = self.db.execute_query("""
            INSERT INTO ferias (pessoa_id, data_inicio, data_fim, descricao)
            VALUES (?, ?, ?, ?)
        """, (pessoa_id, inicio, fim, descricao or None))

        if success:
            QMessageBox.information(self, "Sucesso", "Férias adicionadas!")
            self.input_descricao.clear()
            self.carregar_ferias()
        else:
            QMessageBox.critical(self, "Erro", "Falha ao salvar na base de dados.")

    def editar_ferias(self):
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Erro", "Selecione uma linha para editar!")
            return

        item_id = self.tabela.item(row, 0)
        if not item_id or not item_id.text().strip():
            QMessageBox.warning(self, "Erro", "ID inválido!")
            return

        try:
            ferias_id = int(item_id.text())
        except ValueError:
            QMessageBox.warning(self, "Erro", "ID corrompido!")
            return

        nome = self.tabela.item(row, 1).text()
        inicio = QDate.fromString(self.tabela.item(row, 2).text(), 'yyyy-MM-dd')
        fim = QDate.fromString(self.tabela.item(row, 3).text(), 'yyyy-MM-dd')
        descricao = self.tabela.item(row, 4).text()

        # Preencher formulário
        self.combo_pessoa.setCurrentText(nome)
        self.date_inicio.setDate(inicio)
        self.date_fim.setDate(fim)
        self.input_descricao.setText(descricao)

        if QMessageBox.question(self, "Editar", "Confirmar edição?") != QMessageBox.Yes:
            return

        novo_inicio = self.date_inicio.date().toString('yyyy-MM-dd')
        novo_fim = self.date_fim.date().toString('yyyy-MM-dd')
        nova_desc = self.input_descricao.text().strip()

        if self.date_inicio.date() > self.date_fim.date():
            QMessageBox.warning(self, "Erro", "Data de início deve ser antes do fim!")
            return

        success = self.db.execute_query("""
            UPDATE ferias SET data_inicio = ?, data_fim = ?, descricao = ?
            WHERE id = ?
        """, (novo_inicio, novo_fim, nova_desc or None, ferias_id))

        if success:
            QMessageBox.information(self, "Sucesso", "Férias atualizadas!")
            self.carregar_ferias()
        else:
            QMessageBox.critical(self, "Erro", "Falha ao atualizar.")

    def apagar_ferias(self):
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Erro", "Selecione uma linha para apagar!")
            return

        item_id = self.tabela.item(row, 0)
        if not item_id or not item_id.text().strip():
            QMessageBox.warning(self, "Erro", "ID inválido!")
            return

        try:
            ferias_id = int(item_id.text())
        except ValueError:
            QMessageBox.warning(self, "Erro", "ID corrompido!")
            return

        nome = self.tabela.item(row, 1).text()
        inicio = self.tabela.item(row, 2).text()
        fim = self.tabela.item(row, 3).text()

        if QMessageBox.question(self, "Apagar", f"Apagar férias de {nome} de {inicio} a {fim}?") != QMessageBox.Yes:
            return

        success = self.db.execute_query("DELETE FROM ferias WHERE id = ?", (ferias_id,))
        if success:
            QMessageBox.information(self, "Sucesso", "Férias apagadas!")
            self.carregar_ferias()
        else:
            QMessageBox.critical(self, "Erro", "Falha ao apagar.")

    def closeEvent(self, event):
        self.db.close()
        event.accept()


def mostrar_ferias():
    dialog = FeriasDialog()
    dialog.exec_()


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    dialog = FeriasDialog()
    dialog.show()
    sys.exit(app.exec_())