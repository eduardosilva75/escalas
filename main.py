#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QLabel, QFrame, QHBoxLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Gestão de Escalas")
        self.setGeometry(100, 100, 800, 700)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Título
        title = QLabel("Sistema de Gestão de Escalas")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Subtítulo
        subtitle = QLabel("Selecione o módulo desejado")
        subtitle.setFont(QFont("Arial", 12))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #666; margin-bottom: 20px;")
        layout.addWidget(subtitle)
        
        # Frame para os botões
        buttons_frame = QFrame()
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(15)
        
        # Botão Gerador de Escalas
        btn_gerador = QPushButton("📅 Gerador de Escalas")
        btn_gerador.setFont(QFont("Arial", 14))
        btn_gerador.setMinimumHeight(80)
        btn_gerador.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        btn_gerador.clicked.connect(self.abrir_gerador_escalas)
        buttons_layout.addWidget(btn_gerador)
        
        # Botão Gestão de Folgas
        btn_folgas = QPushButton("🌴 Gestão de Folgas")
        btn_folgas.setFont(QFont("Arial", 14))
        btn_folgas.setMinimumHeight(80)
        btn_folgas.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
            QPushButton:pressed {
                background-color: #0960a8;
            }
        """)
        btn_folgas.clicked.connect(self.abrir_folgas)
        buttons_layout.addWidget(btn_folgas)
        
        # Botão Gestão de Férias
        btn_ferias = QPushButton("✈️ Gestão de Férias")
        btn_ferias.setFont(QFont("Arial", 14))
        btn_ferias.setMinimumHeight(80)
        btn_ferias.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #e68900;
            }
            QPushButton:pressed {
                background-color: #cc7a00;
            }
        """)
        btn_ferias.clicked.connect(self.abrir_ferias)
        buttons_layout.addWidget(btn_ferias)
        
        # Botão Gestão de Horários
        btn_horarios = QPushButton("⏰ Gestão de Horários")
        btn_horarios.setFont(QFont("Arial", 14))
        btn_horarios.setMinimumHeight(80)
        btn_horarios.setEnabled(False)  # DESATIVADO
        btn_horarios.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
            QPushButton:pressed {
                background-color: #6A1B9A;
            }
        """)
        btn_horarios.clicked.connect(self.abrir_horarios)
        buttons_layout.addWidget(btn_horarios)
        
        # Botão Dias Fixos
        btn_dias_fixos = QPushButton("📋 Dias Fixos")
        btn_dias_fixos.setFont(QFont("Arial", 14))
        btn_dias_fixos.setMinimumHeight(80)
        btn_dias_fixos.setStyleSheet("""
            QPushButton {
                background-color: #607D8B;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #546E7A;
            }
            QPushButton:pressed {
                background-color: #455A64;
            }
        """)
        btn_dias_fixos.clicked.connect(self.abrir_dias_fixos)
        buttons_layout.addWidget(btn_dias_fixos)
        
        # Botão Configurações
        btn_config = QPushButton("⚙️ Configurações")
        btn_config.setFont(QFont("Arial", 14))
        btn_config.setMinimumHeight(80)
        btn_config.setEnabled(False)  # DESATIVADO
        btn_config.setStyleSheet("""
            QPushButton {
                background-color: #795548;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #6D4C41;
            }
            QPushButton:pressed {
                background-color: #5D4037;
            }
        """)
        btn_config.clicked.connect(self.abrir_configuracoes)
        buttons_layout.addWidget(btn_config)
        
        buttons_frame.setLayout(buttons_layout)
        layout.addWidget(buttons_frame)
        
        # Espaçador
        layout.addStretch()
        
        # Botão Fechar Aplicação
        btn_fechar_layout = QHBoxLayout()
        btn_fechar = QPushButton("🚪 Fechar Aplicação")
        btn_fechar.setFont(QFont("Arial", 12))
        btn_fechar.setMinimumHeight(50)
        btn_fechar.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
        """)
        btn_fechar.clicked.connect(self.fechar_aplicacao)
        btn_fechar_layout.addStretch()
        btn_fechar_layout.addWidget(btn_fechar)
        btn_fechar_layout.addStretch()
        layout.addLayout(btn_fechar_layout)
        
        # Rodapé
        footer = QLabel("© 2025 Sistema de Gestão de Escalas - SQLite")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: #999; font-size: 10px;")
        layout.addWidget(footer)
        
        central_widget.setLayout(layout)
        
        # Estilo geral da janela
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
        """)
    
    def abrir_gerador_escalas(self):
        try:
            from gerador import mostrar_gerador
            mostrar_gerador()
        except Exception as e:
            print(f"Erro ao abrir Gerador: {e}")
    
    def abrir_folgas(self):
        """Abre a gestão de folgas"""
        try:
            from folgas import mostrar_folgas
            mostrar_folgas()
        except Exception as e:
            print(f"Erro ao abrir Gestão de Folgas: {e}")
    
    def abrir_ferias(self):
        """Abre a gestão de férias"""
        try:
            from ferias import mostrar_ferias
            mostrar_ferias()
        except Exception as e:
            print(f"Erro ao abrir Gestão de Férias: {e}")
    
    def abrir_horarios(self):
        """Abre a gestão de horários"""
        try:
            from horarios import mostrar_horarios
            mostrar_horarios()
        except Exception as e:
            print(f"Erro ao abrir Gestão de Horários: {e}")
    
    def abrir_dias_fixos(self):
        """Abre a gestão de dias fixos"""
        try:
            from diasFixos import mostrar_dias_fixos
            mostrar_dias_fixos()
        except Exception as e:
            print(f"Erro ao abrir Dias Fixos: {e}")
    
    def abrir_configuracoes(self):
        """Abre as configurações"""
        try:
            from configuracoes import mostrar_configuracoes
            mostrar_configuracoes()
        except Exception as e:
            print(f"Erro ao abrir Configurações: {e}")
    
    def fechar_aplicacao(self):
        """Fecha a aplicação completamente"""
        self.close()
        QApplication.quit()

def main():
    app = QApplication(sys.argv)
    
    # Estilo moderno
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()