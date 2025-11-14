from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QLabel, QComboBox, QDateEdit, QSpinBox, QMessageBox, QHeaderView, QGroupBox, QFormLayout, QCheckBox, QInputDialog)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor
from datetime import datetime, timedelta, date
from database import DatabaseManager

# === FUNÇÕES AUXILIARES PARA SEMANAS ===
def get_semana_id_from_date(data):
    """Converte uma data para o formato AAAASS (ex: 202540)"""
    ano = data.year
    numero_semana = data.isocalendar()[1]  # ISO week number
    return f"{ano}{numero_semana:02d}"

def get_semana_id_formatado(semana_id):
    """Formata AAAASS para AAAA-WSS (ex: 202540 → 2025-W40)"""
    return f"{semana_id[:4]}-W{semana_id[4:]}"

def get_date_from_semana_id(semana_id):
    """Converte AAAASS para a data do primeiro dia da semana (segunda-feira)"""
    ano = int(semana_id[:4])
    numero_semana = int(semana_id[4:])
    # Primeira segunda-feira do ano
    primeira_segunda = datetime(ano, 1, 4)  # 4 de Janeiro é sempre na semana 1
    while primeira_segunda.weekday() != 0:  # 0 = segunda-feira
        primeira_segunda -= timedelta(days=1)
    # Adicionar semanas
    data_semana = primeira_segunda + timedelta(weeks=numero_semana-1)
    return data_semana

class FolgasDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.ciclos_base = {
            'António C.': [[5,6], [3,4], [2,3], [1,2], [1,2], [1,6]],
            'Antónia F.': [[2,3], [1,2], [1,2], [1,6], [5,6], [3,4]],
            'Magda G.': [[1,2], [1,6], [5,6], [3,4], [2,3], [1,2]],
            'Eduardo S.': [[0,6], [5,6], [3,4], [2,3]],
            'Susana A.': [[5,6]]
        }
        self.pessoa_ids = {}
        self.current_edit_mode = 'pattern'
        self.current_semana_id = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Gestão de Folgas e Ciclos")
        self.setGeometry(100, 100, 1000, 700)
        layout = QVBoxLayout()

        # Título
        title = QLabel("Gestão de Folgas e Ciclos de Trabalho")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("margin: 10px; color: #2c3e50;")
        layout.addWidget(title)

        # Grupo de configuração de ciclos
        config_group = QGroupBox("Configuração de Ciclos")
        config_layout = QFormLayout()

        # Seleção de pessoa
        self.pessoa_combo = QComboBox()
        self.pessoa_combo.addItems(['António C.', 'Antónia F.', 'Magda G.', 'Eduardo S.', 'Susana A.'])
        self.pessoa_combo.currentTextChanged.connect(self.carregar_ciclo_pessoa)
        config_layout.addRow("Pessoa:", self.pessoa_combo)

        # Data de referência
        self.data_ref_edit = QDateEdit()
        self.data_ref_edit.setDate(QDate(2025, 9, 29))
        self.data_ref_edit.setCalendarPopup(True)
        self.data_ref_edit.dateChanged.connect(self.atualizar_visualizacao_apos_data_mudanca)
        config_layout.addRow("Data Base:", self.data_ref_edit)

        # Semana do ciclo
        self.semana_spin = QSpinBox()
        self.semana_spin.setRange(1, 6)
        self.semana_spin.valueChanged.connect(self.carregar_dias_semana)
        config_layout.addRow("Semana do Ciclo:", self.semana_spin)

        config_group.setLayout(config_layout)
        layout.addWidget(config_group)

        # Grupo de dias de folga
        dias_group = QGroupBox("Dias de Folga na Semana")
        dias_layout = QVBoxLayout()

        # Checkboxes para dias da semana
        dias_semana_layout = QHBoxLayout()
        self.checkboxes = {}
        dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        for i, dia in enumerate(dias_semana):
            checkbox = QCheckBox(dia)
            checkbox.dia_numero = i
            self.checkboxes[i] = checkbox
            dias_semana_layout.addWidget(checkbox)
        dias_layout.addLayout(dias_semana_layout)

        # Botões para a semana
        botoes_semana_layout = QHBoxLayout()
        btn_fim_semana = QPushButton("Fim de Semana (Sáb+Dom)")
        btn_fim_semana.clicked.connect(self.marcar_fim_semana)
        botoes_semana_layout.addWidget(btn_fim_semana)

        btn_dias_uteis = QPushButton("Dias Úteis (Seg-Sex)")
        btn_dias_uteis.clicked.connect(self.marcar_dias_uteis)
        botoes_semana_layout.addWidget(btn_dias_uteis)

        btn_limpar = QPushButton("Limpar Seleção")
        btn_limpar.clicked.connect(self.limpar_selecao)
        botoes_semana_layout.addWidget(btn_limpar)

        dias_layout.addLayout(botoes_semana_layout)
        dias_group.setLayout(dias_layout)
        layout.addWidget(dias_group)

        # Botões de ação
        botoes_layout = QHBoxLayout()

        btn_salvar_semana = QPushButton("💾 Salvar Semana Específica")
        btn_salvar_semana.setStyleSheet("QPushButton { background-color: #27ae60; color: white; font-weight: bold; padding: 8px; }")
        btn_salvar_semana.clicked.connect(self.salvar_semana)
        botoes_layout.addWidget(btn_salvar_semana)

        btn_salvar_base = QPushButton("💾 Salvar no Ciclo Base")
        btn_salvar_base.setStyleSheet("QPushButton { background-color: #27ae60; color: white; font-weight: bold; padding: 8px; }")
        btn_salvar_base.clicked.connect(self.salvar_ciclo_base)
        botoes_layout.addWidget(btn_salvar_base)

        btn_adicionar_ciclo = QPushButton("Adicionar Ciclo a Partir de...")
        btn_adicionar_ciclo.setStyleSheet("QPushButton { background-color: #3498db; color: white; font-weight: bold; padding: 8px; }")
        btn_adicionar_ciclo.clicked.connect(self.adicionar_ciclo_a_partir_de)
        botoes_layout.addWidget(btn_adicionar_ciclo)
        '''
        btn_gerar_ciclo.setStyleSheet("QPushButton { background-color: #3498db; color: white; font-weight: bold; padding: 8px; }")
        btn_gerar_ciclo.clicked.connect(self.gerar_ciclo_completo)
        botoes_layout.addWidget(btn_gerar_ciclo)
        '''
        btn_carregar_bd = QPushButton("📂 Carregar da BD")
        btn_carregar_bd.setStyleSheet("QPushButton { background-color: #f39c12; color: white; font-weight: bold; padding: 8px; }")
        btn_carregar_bd.clicked.connect(self.carregar_da_base_dados)
        botoes_layout.addWidget(btn_carregar_bd)

        btn_editar_semana = QPushButton("📅 Editar Semana Específica")
        btn_editar_semana.setStyleSheet("QPushButton { background-color: #9b59b6; color: white; font-weight: bold; padding: 8px; }")
        btn_editar_semana.clicked.connect(self.editar_semana_especifica)
        botoes_layout.addWidget(btn_editar_semana)

        layout.addLayout(botoes_layout)

        # Tabela de visualização do ciclo
        layout.addWidget(QLabel("Visualização do Ciclo:"))
        self.tabela_ciclo = QTableWidget()
        self.tabela_ciclo.setColumnCount(8)
        self.tabela_ciclo.setHorizontalHeaderLabels(['Semana'] + dias_semana)
        layout.addWidget(self.tabela_ciclo)

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

        # Carregar dados iniciais
        self.carregar_ciclo_pessoa()

    def atualizar_visualizacao_apos_data_mudanca(self):
        pessoa = self.pessoa_combo.currentText()
        ciclo = self.ciclos_base.get(pessoa, [])
        self.atualizar_visualizacao_ciclo(ciclo)

    def carregar_ciclo_pessoa(self):
        """Carrega o ciclo da pessoa selecionada"""
        pessoa = self.pessoa_combo.currentText()
        ciclo = self.ciclos_base.get(pessoa, [])

        # Atualizar limite do spinbox baseado no ciclo
        if pessoa == 'Eduardo S.':
            self.semana_spin.setRange(1, 4)
        elif pessoa == 'Susana A.':
            self.semana_spin.setRange(1, 1)
        else:
            self.semana_spin.setRange(1, 6)

        # Atualizar visualização
        self.atualizar_visualizacao_ciclo(ciclo)

    def carregar_dias_semana(self):
        """Carrega os dias da semana selecionada"""
        self.current_edit_mode = 'pattern'
        self.current_semana_id = None
        pessoa = self.pessoa_combo.currentText()
        semana = self.semana_spin.value() - 1  # Converter para índice 0-based
        ciclo = self.ciclos_base.get(pessoa, [])
        if semana < len(ciclo):
            dias_folga = ciclo[semana]
            # Limpar seleção atual
            self.limpar_selecao()
            # Marcar dias de folga
            for dia in dias_folga:
                if dia in self.checkboxes:
                    self.checkboxes[dia].setChecked(True)

    def limpar_selecao(self):
        """Limpa todas as seleções de dias"""
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(False)

    def marcar_fim_semana(self):
        """Marca sábado e domingo como folga"""
        self.limpar_selecao()
        self.checkboxes[5].setChecked(True)  # Sábado
        self.checkboxes[6].setChecked(True)  # Domingo

    def marcar_dias_uteis(self):
        """Marca dias úteis como folga"""
        self.limpar_selecao()
        for i in range(5):  # Segunda a Sexta
            self.checkboxes[i].setChecked(True)

    def get_dias_selecionados(self):
        """Retorna lista de dias selecionados"""
        return [dia for dia, checkbox in self.checkboxes.items() if checkbox.isChecked()]

    def salvar_ciclo_base(self):
        """Salva a configuração da semana atual no ciclo base"""
        pessoa = self.pessoa_combo.currentText()
        semana = self.semana_spin.value() - 1
        dias_folga = self.get_dias_selecionados()
        if not dias_folga:
            QMessageBox.warning(self, "Aviso", "Selecione pelo menos um dia de folga!")
            return
        if pessoa not in self.ciclos_base or semana >= len(self.ciclos_base[pessoa]):
            QMessageBox.warning(self, "Erro", "Semana inválida no ciclo base!")
            return
        self.ciclos_base[pessoa][semana] = sorted(dias_folga)
        self.atualizar_visualizacao_ciclo(self.ciclos_base[pessoa])
        QMessageBox.information(self, "Sucesso", f"Semana {semana + 1} do ciclo base atualizada para {pessoa}!")

    def salvar_semana(self):
        """Salva a configuração da semana atual para uma semana específica pelo semana_id"""
        pessoa = self.pessoa_combo.currentText()
        dias_folga = self.get_dias_selecionados()
        if not dias_folga:
            QMessageBox.warning(self, "Aviso", "Selecione pelo menos um dia de folga!")
            return

        if self.current_edit_mode == 'specific' and self.current_semana_id:
            semana_id = self.current_semana_id
        else:
            # Perguntar qual semana (semana_id) deseja atualizar
            semana_id, ok = QInputDialog.getText(
                self, "Salvar Semana Específica",
                "Digite o identificador da semana (AAAASS):\nEx: 202540, 202601"
            )
            if not ok or not semana_id:
                return

        # Validar formato
        if not semana_id.isdigit() or len(semana_id) != 6:
            QMessageBox.warning(self, "Formato Inválido", "O identificador deve ter 6 dígitos (AAAASS)\nEx: 202540, 202601")
            return

        # Obter ID da pessoa
        if pessoa not in self.pessoa_ids:
            pessoa_result = self.db.execute_query(
                "SELECT id FROM pessoas WHERE nome = ?", (pessoa,), fetch=True
            )
            if not pessoa_result:
                QMessageBox.warning(self, "Erro", f"Pessoa {pessoa} não encontrada na base de dados!")
                return
            self.pessoa_ids[pessoa] = pessoa_result[0]['id']
        pessoa_id = self.pessoa_ids[pessoa]

        # Remover folgas existentes para esta semana
        self.db.execute_query("""
            DELETE FROM folgas_ciclo WHERE pessoa_id = ? AND semana_id = ?
        """, (pessoa_id, semana_id))

        # Inserir novas folgas
        for dia in dias_folga:
            self.db.execute_query("""
                INSERT INTO folgas_ciclo (pessoa_id, semana_id, dia_semana) VALUES (?, ?, ?)
            """, (pessoa_id, semana_id, dia))

        semana_formatada = get_semana_id_formatado(semana_id)
        QMessageBox.information(
            self, "Sucesso", f"Semana {semana_formatada} atualizada para {pessoa}!"
        )

        # Recarregar visualização
        self.carregar_da_base_dados()
        self.current_edit_mode = 'pattern'
        self.current_semana_id = None

    def gerar_ciclo_completo(self):
        """Gera e salva o ciclo completo na base de dados com identificadores de semana"""
        pessoa = self.pessoa_combo.currentText()
        if pessoa not in self.ciclos_base:
            QMessageBox.warning(self, "Erro", "Pessoa não encontrada!")
            return

        # Perguntar quantas semanas gerar
        num_semanas, ok = QInputDialog.getInt(
            self, "Gerar Ciclo",
            "Quantas semanas deseja gerar?\n(O ciclo repetirá automaticamente)",
            value=52,  # Valor padrão: 1 ano
            min=1, max=520  # Máximo: 10 anos
        )
        if not ok:
            return

        # Obter ID da pessoa
        pessoa_result = self.db.execute_query(
            "SELECT id FROM pessoas WHERE nome = ?", (pessoa,), fetch=True
        )
        if not pessoa_result:
            QMessageBox.warning(self, "Erro", f"Pessoa {pessoa} não encontrada na base de dados!")
            return
        pessoa_id = pessoa_result[0]['id']

        ciclo = self.ciclos_base[pessoa]
        tamanho_ciclo = len(ciclo)

        # Data de referência
        data_referencia = self.data_ref_edit.date().toPyDate()

        # Limpar folgas existentes para esta pessoa
        self.db.execute_query("DELETE FROM folgas_ciclo WHERE pessoa_id = ?", (pessoa_id,))

        # Inserir ciclo repetitivo
        for semana_offset in range(num_semanas):
            # Calcular qual semana do ciclo (0, 1, 2, 3... e reinicia)
            posicao_no_ciclo = semana_offset % tamanho_ciclo
            dias_folga = ciclo[posicao_no_ciclo]

            # Calcular semana_id para esta semana
            data_semana = data_referencia + timedelta(weeks=semana_offset)
            semana_id = get_semana_id_from_date(data_semana)

            # Inserir dias de folga
            for dia in dias_folga:
                self.db.execute_query("""
                    INSERT INTO folgas_ciclo (pessoa_id, semana_id, dia_semana) VALUES (?, ?, ?)
                """, (pessoa_id, semana_id, dia))

        QMessageBox.information(
            self, "Sucesso",
            f"Ciclo de {tamanho_ciclo} semanas gerado para {pessoa}!\n"
            f"Total de semanas na base de dados: {num_semanas}\n"
            f"O ciclo repete {num_semanas // tamanho_ciclo} vezes completas."
        )

        # Carregar da base de dados para confirmar
        self.carregar_da_base_dados()

    def adicionar_ciclo_a_partir_de(self):
        """Adiciona um novo ciclo a partir de uma data escolhida, sem apagar os existentes"""
        pessoa = self.pessoa_combo.currentText()
        if pessoa not in self.ciclos_base:
            QMessageBox.warning(self, "Erro", "Pessoa não encontrada!")
            return

        # 1. Obter ID da pessoa
        if pessoa not in self.pessoa_ids:
            pessoa_result = self.db.execute_query(
                "SELECT id FROM pessoas WHERE nome = ?", (pessoa,), fetch=True
            )
            if not pessoa_result:
                QMessageBox.warning(self, "Erro", f"Pessoa {pessoa} não encontrada na base de dados!")
                return
            self.pessoa_ids[pessoa] = pessoa_result[0]['id']
        pessoa_id = self.pessoa_ids[pessoa]

        # 2. Perguntar: usar última semana ou escolher data?
        opcoes = ["Usar última semana salva", "Escolher data manualmente"]
        opcao, ok = QInputDialog.getItem(
            self, "Adicionar Ciclo", "Como definir a data inicial?", opcoes, 0, False
        )
        if not ok:
            return

        # 3. Determinar data inicial
        if opcao == opcoes[0]:
            # Última semana salva
            ultima = self.db.execute_query("""
                SELECT MAX(semana_id) FROM folgas_ciclo WHERE pessoa_id = ?
            """, (pessoa_id,), fetch=True)
            if not ultima or not ultima[0]['MAX(semana_id)']:
                QMessageBox.information(self, "Info", "Nenhum ciclo encontrado. Usando data base atual.")
                data_inicial = self.data_ref_edit.date().toPyDate()
            else:
                ultima_semana_id = ultima[0]['MAX(semana_id)']
                ultima_data = get_date_from_semana_id(ultima_semana_id)
                data_inicial = ultima_data + timedelta(weeks=1)
        else:
            # Escolher data com calendário
            dialog = QDialog(self)
            dialog.setWindowTitle("Selecionar Data Inicial")
            dialog.setModal(True)
            layout = QVBoxLayout()

            label = QLabel("Selecione a data de início (será ajustada para segunda-feira):")
            layout.addWidget(label)

            date_edit = QDateEdit()
            date_edit.setCalendarPopup(True)
            date_edit.setDate(self.data_ref_edit.date())
            layout.addWidget(date_edit)

            buttons = QHBoxLayout()
            btn_ok = QPushButton("OK")
            btn_cancel = QPushButton("Cancelar")
            buttons.addWidget(btn_ok)
            buttons.addWidget(btn_cancel)
            layout.addLayout(buttons)

            dialog.setLayout(layout)

            result = {'ok': False, 'date': None}

            def on_ok():
                selected_date = date_edit.date().toPyDate()
                if selected_date.weekday() != 0:
                    selected_date -= timedelta(days=selected_date.weekday())
                result['ok'] = True
                result['date'] = selected_date
                dialog.accept()

            def on_cancel():
                dialog.reject()

            btn_ok.clicked.connect(on_ok)
            btn_cancel.clicked.connect(on_cancel)

            dialog.exec_()

            if not result['ok']:
                return
            data_inicial = result['date']

        # 4. Perguntar quantas semanas
        num_semanas, ok = QInputDialog.getInt(
            self, "Adicionar Ciclo",
            f"Adicionar quantas semanas a partir de {data_inicial.strftime('%d/%m/%Y')}?",
            value=12, min=1, max=520
        )
        if not ok:
            return

        # 5. Gerar e inserir (sem apagar)
        ciclo = self.ciclos_base[pessoa]
        tamanho_ciclo = len(ciclo)

        for semana_offset in range(num_semanas):
            posicao_no_ciclo = semana_offset % tamanho_ciclo
            dias_folga = ciclo[posicao_no_ciclo]
            data_semana = data_inicial + timedelta(weeks=semana_offset)
            semana_id = get_semana_id_from_date(data_semana)

            for dia in dias_folga:
                self.db.execute_query("""
                    INSERT OR IGNORE INTO folgas_ciclo (pessoa_id, semana_id, dia_semana)
                    VALUES (?, ?, ?)
                """, (pessoa_id, semana_id, dia))

        QMessageBox.information(
            self, "Sucesso",
            f"Adicionadas {num_semanas} semanas a partir de {data_inicial.strftime('%d/%m/%Y')}!\n"
            f"Ciclo existente mantido."
        )

        # Atualizar visualização
        self.carregar_da_base_dados()

    def carregar_da_base_dados(self):
        """Carrega os ciclos da base de dados com identificadores de semana"""
        pessoa = self.pessoa_combo.currentText()

        # Obter ID da pessoa
        if pessoa not in self.pessoa_ids:
            pessoa_result = self.db.execute_query(
                "SELECT id FROM pessoas WHERE nome = ?", (pessoa,), fetch=True
            )
            if not pessoa_result:
                QMessageBox.warning(self, "Erro", f"Pessoa {pessoa} não encontrada na base de dados!")
                return
            self.pessoa_ids[pessoa] = pessoa_result[0]['id']
        pessoa_id = self.pessoa_ids[pessoa]

        # Carregar folgas da base de dados
        folgas_db = self.db.execute_query("""
            SELECT semana_id, dia_semana FROM folgas_ciclo
            WHERE pessoa_id = ?
            ORDER BY semana_id, dia_semana
        """, (pessoa_id,), fetch=True)

        if not folgas_db:
            QMessageBox.information(self, "Info", f"Nenhum ciclo encontrado para {pessoa} na base de dados!")
            return

        # Reconstruir ciclo a partir da base de dados
        ciclo_reconstruido = {}
        for folga in folgas_db:
            semana_id = folga['semana_id']
            dia = folga['dia_semana']
            if semana_id not in ciclo_reconstruido:
                ciclo_reconstruido[semana_id] = []
            ciclo_reconstruido[semana_id].append(dia)

        # Converter para lista ordenada por semana_id
        ciclo_ordenado = []
        for semana_id in sorted(ciclo_reconstruido.keys()):
            ciclo_ordenado.append(sorted(ciclo_reconstruido[semana_id]))

        # Atualizar visualização com o ciclo reconstruído (não sobrescreve ciclos_base)
        self.atualizar_visualizacao_ciclo(ciclo_ordenado)

        num_semanas = len(ciclo_reconstruido)
        QMessageBox.information(
            self, "Sucesso",
            f"Ciclo carregado da base de dados para {pessoa}!\n"
            f"Total de semanas: {num_semanas}"
        )

    def atualizar_visualizacao_ciclo(self, ciclo):
        """Atualiza a tabela de visualização do ciclo com formato AAAA-WSS"""
        dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']

        # Mostrar o ciclo (padrão ou carregado)
        self.tabela_ciclo.setRowCount(len(ciclo))

        # Data de referência
        data_referencia = self.data_ref_edit.date().toPyDate()

        for semana_idx, dias_folga in enumerate(ciclo):
            # Calcular semana_id para esta posição
            data_semana = data_referencia + timedelta(weeks=semana_idx)
            semana_id = get_semana_id_from_date(data_semana)
            semana_formatada = get_semana_id_formatado(semana_id)

            # Número da semana
            item_semana = QTableWidgetItem(semana_formatada)
            item_semana.setBackground(QColor(240, 240, 240))
            item_semana.setTextAlignment(Qt.AlignCenter)
            self.tabela_ciclo.setItem(semana_idx, 0, item_semana)

            # Dias da semana
            for dia_idx in range(7):
                item_dia = QTableWidgetItem()
                if dia_idx in dias_folga:
                    item_dia.setText("FOLGA")
                    item_dia.setBackground(QColor(173, 216, 230))  # Azul claro
                    item_dia.setForeground(QColor(0, 0, 139))  # Azul escuro
                else:
                    item_dia.setText("TRABALHO")
                    item_dia.setBackground(QColor(144, 238, 144))  # Verde claro
                    item_dia.setForeground(QColor(0, 100, 0))  # Verde escuro
                item_dia.setTextAlignment(Qt.AlignCenter)
                self.tabela_ciclo.setItem(semana_idx, dia_idx + 1, item_dia)

        self.tabela_ciclo.resizeColumnsToContents()
        self.tabela_ciclo.resizeRowsToContents()
        self.tabela_ciclo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def closeEvent(self, event):
        self.db.close()
        event.accept()

    def editar_semana_especifica(self):
        """Permite editar uma semana específica pelo identificador AAAASS"""
        pessoa = self.pessoa_combo.currentText()

        # Diálogo para escolher semana
        semana_id, ok = QInputDialog.getText(self, "Editar Semana Específica", "Digite o identificador da semana (AAAASS):\nEx: 202540, 202601")
        if ok and semana_id:
            # Validar formato (6 dígitos numéricos)
            if not semana_id.isdigit() or len(semana_id) != 6:
                QMessageBox.warning(self, "Formato Inválido", "O identificador deve ter 6 dígitos (AAAASS)\nEx: 202540, 202601")
                return
            self.current_edit_mode = 'specific'
            self.current_semana_id = semana_id
            # Carregar folgas existentes para esta semana
            self.carregar_semana_por_id(pessoa, semana_id)

    def carregar_semana_por_id(self, pessoa, semana_id):
        """Carrega os dias de folga para uma semana específica"""
        # Obter ID da pessoa se não existir
        if pessoa not in self.pessoa_ids:
            pessoa_result = self.db.execute_query(
                "SELECT id FROM pessoas WHERE nome = ?", (pessoa,), fetch=True
            )
            if not pessoa_result:
                QMessageBox.warning(self, "Erro", f"Pessoa {pessoa} não encontrada na base de dados!")
                return
            self.pessoa_ids[pessoa] = pessoa_result[0]['id']

        # Buscar folgas para esta semana específica
        folgas_db = self.db.execute_query("""
            SELECT dia_semana FROM folgas_ciclo
            WHERE pessoa_id = ? AND semana_id = ?
        """, (self.pessoa_ids[pessoa], semana_id), fetch=True)

        # Limpar seleção atual
        self.limpar_selecao()

        # Marcar dias de folga encontrados
        dias_folga = []
        for folga in folgas_db:
            dia = folga['dia_semana']
            dias_folga.append(dia)
            if dia in self.checkboxes:
                self.checkboxes[dia].setChecked(True)

        semana_formatada = get_semana_id_formatado(semana_id)
        if dias_folga:
            QMessageBox.information(self, "Semana Carregada", f"Editando semana {semana_formatada} para {pessoa}\nDias de folga: {len(dias_folga)}")
        else:
            QMessageBox.information(self, "Semana Vazia", f"Semana {semana_formatada} não tem folgas definidas para {pessoa}")

def mostrar_folgas():
    dialog = FolgasDialog()
    dialog.exec_()

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    dialog = FolgasDialog()
    dialog.show()
    sys.exit(app.exec_())