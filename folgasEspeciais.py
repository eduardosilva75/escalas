# folgas_especiais.py
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QLabel, QComboBox, 
                             QDateEdit, QMessageBox, QHeaderView, QCalendarWidget)
from PyQt5.QtCore import QDate
from database import DatabaseManager

class FolgasEspeciaisDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Gestão de Folgas Especiais")
        self.setGeometry(100, 100, 800, 600)
        
        layout = QVBoxLayout()
        
        # Controles superiores
        controls_layout = QHBoxLayout()
        
        self.pessoa_combo = QComboBox()
        pessoas = self.db.get_pessoas()
        for pessoa in pessoas:
            self.pessoa_combo.addItem(pessoa['nome'])
        controls_layout.addWidget(QLabel("Pessoa:"))
        controls_layout.addWidget(self.pessoa_combo)
        
        self.data_edit = QDateEdit()
        self.data_edit.setDate(QDate.currentDate())
        self.data_edit.setCalendarPopup(True)
        controls_layout.addWidget(QLabel("Data:"))
        controls_layout.addWidget(self.data_edit)
        
        btn_adicionar = QPushButton("➕ Adicionar Folga")
        btn_adicionar.clicked.connect(self.adicionar_folga)
        controls_layout.addWidget(btn_adicionar)
        
        layout.addLayout(controls_layout)
        
        # Tabela de folgas especiais
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(4)
        self.tabela.setHorizontalHeaderLabels(['Pessoa', 'Data', 'Descrição', 'Ações'])
        layout.addWidget(self.tabela)
        
        # Botões
        btn_fechar = QPushButton("Fechar")
        btn_fechar.clicked.connect(self.close)
        layout.addWidget(btn_fechar)
        
        self.setLayout(layout)
        self.carregar_folgas_especiais()
    
    def adicionar_folga(self):
        pessoa = self.pessoa_combo.currentText()
        data = self.data_edit.date().toString('yyyy-MM-dd')
        
        pessoa_result = self.db.execute_query(
            "SELECT id FROM pessoas WHERE nome = ?", (pessoa,), fetch=True
        )
        
        if pessoa_result:
            pessoa_id = pessoa_result[0]['id']
            
            result = self.db.execute_query("""
                INSERT OR REPLACE INTO folgas_especiais (pessoa_id, data, descricao)
                VALUES (?, ?, ?)
            """, (pessoa_id, data, "Folga especial"))
            
            if result:
                QMessageBox.information(self, "Sucesso", f"Folga especial adicionada para {pessoa}!")
                self.carregar_folgas_especiais()
            else:
                QMessageBox.warning(self, "Erro", "Erro ao adicionar folga especial!")
    
    def carregar_folgas_especiais(self):
        folgas = self.db.execute_query("""
            SELECT p.nome, f.data, f.descricao, f.id
            FROM folgas_especiais f
            JOIN pessoas p ON f.pessoa_id = p.id
            ORDER BY f.data DESC
        """, fetch=True)
        
        self.tabela.setRowCount(len(folgas))
        
        for row, folga in enumerate(folgas):
            self.tabela.setItem(row, 0, QTableWidgetItem(folga['nome']))
            self.tabela.setItem(row, 1, QTableWidgetItem(folga['data']))
            self.tabela.setItem(row, 2, QTableWidgetItem(folga['descricao']))
            
            btn_remover = QPushButton("❌ Remover")
            btn_remover.clicked.connect(lambda checked, id=folga['id']: self.remover_folga(id))
            self.tabela.setCellWidget(row, 3, btn_remover)
        
        self.tabela.resizeColumnsToContents()
    
    def remover_folga(self, folga_id):
        result = self.db.execute_query("DELETE FROM folgas_especiais WHERE id = ?", (folga_id,))
        if result:
            QMessageBox.information(self, "Sucesso", "Folga especial removida!")
            self.carregar_folgas_especiais()

def mostrar_folgas_especiais():
    dialog = FolgasEspeciaisDialog()
    dialog.exec_()