# diasFixos.py
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QComboBox, QDateEdit, QMessageBox, QHeaderView,
    QGroupBox, QFormLayout, QLineEdit, QInputDialog
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor
from datetime import datetime
from database import DatabaseManager


class DiasFixosDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.pessoas = {}
        self.horarios_cache = []
        self.initUI()
        self.carregar_pessoas()
        self.carregar_horarios()

    def initUI(self):
        self.setWindowTitle("Gestão de Horários Fixos")
        self.setGeometry(100, 100, 950, 650)
        layout = QVBoxLayout()

        # Título
        title = QLabel("Gestão de Horários Fixos")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("margin: 10px; color: #2c3e50;")
        layout.addWidget(title)

        # Formulário
        form_group = QGroupBox("Adicionar / Editar Horário Fixo")
        form_layout = QFormLayout()

        # Pessoa
        self.combo_pessoa = QComboBox()
        form_layout.addRow("Pessoa:", self.combo_pessoa)

        # Data
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate(2025, 9, 29))
        form_layout.addRow("Data:", self.date_edit)

        # Horário
        self.input_horario = QLineEdit()
        self.input_horario.setPlaceholderText("Ex: 09:00 - 18:00")
        form_layout.addRow("Horário:", self.input_horario)

        # Descrição (opcional)
        self.input_descricao = QLineEdit()
        self.input_descricao.setPlaceholderText("Opcional: motivo do horário fixo")
        form_layout.addRow("Descrição:", self.input_descricao)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Botões de ação
        btn_layout = QHBoxLayout()
        btn_adicionar = QPushButton("Adicionar Horário")
        btn_adicionar.setStyleSheet("""
            QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 8px; border-radius: 4px; }
            QPushButton:hover { background-color: #45a049; }
        """)
        btn_adicionar.clicked.connect(self.adicionar_horario)

        btn_editar = QPushButton("Editar Selecionado")
        btn_editar.setStyleSheet("""
            QPushButton { background-color: #FF9800; color: white; font-weight: bold; padding: 8px; border-radius: 4px; }
            QPushButton:hover { background-color: #e68900; }
        """)
        btn_editar.clicked.connect(self.editar_horario)

        btn_apagar = QPushButton("Apagar Selecionado")
        btn_apagar.setStyleSheet("""
            QPushButton { background-color: #f44336; color: white; font-weight: bold; padding: 8px; border-radius: 4px; }
            QPushButton:hover { background-color: #d32f2f; }
        """)
        btn_apagar.clicked.connect(self.apagar_horario)

        btn_layout.addWidget(btn_adicionar)
        btn_layout.addWidget(btn_editar)
        btn_layout.addWidget(btn_apagar)
        layout.addLayout(btn_layout)

        # Tabela
        layout.addWidget(QLabel("Horários Fixos Registados:"))
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels(["ID", "Pessoa", "Data", "Horário", "Descrição"])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.tabela)

        # Botão fechar
        btn_fechar = QPushButton("Fechar")
        btn_fechar.setStyleSheet("""
            QPushButton { background-color: #f44336; color: white; font-weight: bold; padding: 8px; border-radius: 4px; }
            QPushButton:hover { background-color: #d32f2f; }
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

    def carregar_horarios(self):
        self.horarios_cache = self.db.execute_query("""
            SELECT h.id, p.nome, h.data, h.horario, h.descricao
            FROM horarios_fixos h
            JOIN pessoas p ON h.pessoa_id = p.id
            ORDER BY h.data, p.nome
        """, fetch=True)
        self.tabela.setRowCount(0)
        for h in self.horarios_cache:
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            self.tabela.setItem(row, 0, QTableWidgetItem(str(h.get('id', ''))))
            self.tabela.setItem(row, 1, QTableWidgetItem(h['nome']))
            self.tabela.setItem(row, 2, QTableWidgetItem(h['data']))
            self.tabela.setItem(row, 3, QTableWidgetItem(h['horario']))
            self.tabela.setItem(row, 4, QTableWidgetItem(h.get('descricao', '')))

    def validar_horario(self, texto):
        import re
        pattern = r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9] - ([0-1]?[0-9]|2[0-3]):[0-5][0-9]$'
        return bool(re.match(pattern, texto.strip()))

    def adicionar_horario(self):
        nome = self.combo_pessoa.currentText()
        if not nome:
            QMessageBox.warning(self, "Erro", "Selecione uma pessoa!")
            return

        data = self.date_edit.date().toString('yyyy-MM-dd')
        horario = self.input_horario.text().strip()
        descricao = self.input_descricao.text().strip()

        if not self.validar_horario(horario):
            QMessageBox.warning(self, "Formato Inválido", "Horário deve ser: HH:MM - HH:MM\nEx: 09:00 - 18:00")
            return

        pessoa_id = self.pessoas[nome]

        # Verificar duplicata
        for h in self.horarios_cache:
            if h['nome'] == nome and h['data'] == data:
                QMessageBox.warning(self, "Duplicata", f"Já existe horário fixo para {nome} em {data}!")
                return

        success = self.db.execute_query("""
            INSERT INTO horarios_fixos (pessoa_id, data, horario, descricao)
            VALUES (?, ?, ?, ?)
        """, (pessoa_id, data, horario, descricao or None))

        if success:
            QMessageBox.information(self, "Sucesso", "Horário fixo adicionado!")
            self.input_horario.clear()
            self.input_descricao.clear()
            self.carregar_horarios()
        else:
            QMessageBox.critical(self, "Erro", "Falha ao salvar na base de dados.")

    def editar_horario(self):
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Erro", "Selecione uma linha para editar!")
            return

        item_id = self.tabela.item(row, 0)
        if not item_id or not item_id.text().strip():
            QMessageBox.warning(self, "Erro", "ID inválido!")
            return

        try:
            horario_id = int(item_id.text())
        except ValueError:
            QMessageBox.warning(self, "Erro", "ID corrompido!")
            return

        nome = self.tabela.item(row, 1).text()
        data_atual = self.tabela.item(row, 2).text()

        # Preencher formulário
        self.combo_pessoa.setCurrentText(nome)
        self.date_edit.setDate(QDate.fromString(data_atual, 'yyyy-MM-dd'))
        self.input_horario.setText(self.tabela.item(row, 3).text())
        self.input_descricao.setText(self.tabela.item(row, 4).text())

        if QMessageBox.question(self, "Editar", "Confirmar edição?") != QMessageBox.Yes:
            return

        nova_data = self.date_edit.date().toString('yyyy-MM-dd')
        novo_horario = self.input_horario.text().strip()
        nova_desc = self.input_descricao.text().strip()

        if not self.validar_horario(novo_horario):
            QMessageBox.warning(self, "Formato Inválido", "Horário: HH:MM - HH:MM")
            return

        # Verificar duplicata (exceto ele mesmo)
        for h in self.horarios_cache:
            if h['nome'] == nome and h['data'] == nova_data and h['id'] != horario_id:
                QMessageBox.warning(self, "Duplicata", f"Já existe horário em {nova_data} para {nome}!")
                return

        success = self.db.execute_query("""
            UPDATE horarios_fixos SET data = ?, horario = ?, descricao = ?
            WHERE id = ?
        """, (nova_data, novo_horario, nova_desc or None, horario_id))

        if success:
            QMessageBox.information(self, "Sucesso", "Horário atualizado!")
            self.carregar_horarios()
        else:
            QMessageBox.critical(self, "Erro", "Falha ao atualizar.")

    def apagar_horario(self):
        row = self.tabela.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Erro", "Selecione uma linha para apagar!")
            return

        item_id = self.tabela.item(row, 0)
        if not item_id or not item_id.text().strip():
            QMessageBox.warning(self, "Erro", "ID inválido!")
            return

        try:
            horario_id = int(item_id.text())
        except ValueError:
            QMessageBox.warning(self, "Erro", "ID corrompido!")
            return

        nome = self.tabela.item(row, 1).text()
        data = self.tabela.item(row, 2).text()
        horario = self.tabela.item(row, 3).text()

        if QMessageBox.question(self, "Apagar", f"Apagar horário de {nome} em {data} ({horario})?") != QMessageBox.Yes:
            return

        success = self.db.execute_query("DELETE FROM horarios_fixos WHERE id = ?", (horario_id,))
        if success:
            QMessageBox.information(self, "Sucesso", "Horário apagado!")
            self.carregar_horarios()
        else:
            QMessageBox.critical(self, "Erro", "Falha ao apagar.")

    def closeEvent(self, event):
        self.db.close()
        event.accept()


def mostrar_dias_fixos():
    dialog = DiasFixosDialog()
    dialog.exec_()


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    dialog = DiasFixosDialog()
    dialog.show()
    sys.exit(app.exec_())