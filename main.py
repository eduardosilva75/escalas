#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QLabel, QFrame, QHBoxLayout, 
                             QScrollArea, QGridLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Gestão de Escalas")
        self.setGeometry(100, 100, 900, 650)  # Reduzido para caber em portátil 15.6"
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal com scroll
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Área de scroll
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Widget interno da área de scroll
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(15)
        scroll_layout.setContentsMargins(10, 10, 10, 10)
        
        # Título
        title = QLabel("Sistema de Gestão de Escalas")
        title.setFont(QFont("Arial", 20, QFont.Bold))  # Reduzido
        title.setAlignment(Qt.AlignCenter)
        scroll_layout.addWidget(title)
        
        # Subtítulo
        subtitle = QLabel("Selecione o módulo desejado")
        subtitle.setFont(QFont("Arial", 11))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #666; margin-bottom: 10px;")
        scroll_layout.addWidget(subtitle)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #CCC; margin: 5px 0;")
        scroll_layout.addWidget(separator)
        
        # Grid de botões (2 colunas)
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(15)
        
        # Lista de botões com (texto, cor, função, ícone)
        botoes = [
            ("📅 Gerador de Escalas", "#4CAF50", self.abrir_gerador_escalas),
            ("🌴 Gestão de Folgas", "#2196F3", self.abrir_folgas),
            ("✈️ Gestão de Férias", "#FF9800", self.abrir_ferias),
            ("🏖️ Mapa de Férias", "#9C27B0", self.abrir_mapa_ferias),
            ("📋 Dias Fixos", "#607D8B", self.abrir_dias_fixos),
            ("⚙️ Configurações", "#795548", self.abrir_configuracoes),
            ("🆘 Gerador de Apoios", "#E67E22", self.abrir_gerador_apoios),  # NOVO BOTÃO
        ]
        
        # Posicionar botões no grid (2 colunas)
        for i, (texto, cor, funcao) in enumerate(botoes):
            row = i // 2  # Linha no grid
            col = i % 2   # Coluna no grid
            
            btn = QPushButton(texto)
            btn.setFont(QFont("Arial", 12))  # Fonte reduzida
            btn.setMinimumHeight(70)  # Altura reduzida
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {cor};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 8px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {self.darken_color(cor)};
                }}
                QPushButton:pressed {{
                    background-color: {self.darker_color(cor)};
                }}
                QPushButton:disabled {{
                    background-color: #A9A9A9;
                    color: #666;
                }}
            """)
            
            # Desativar Configurações se necessário
            if texto == "⚙️ Configurações":
                btn.setEnabled(False)
            
            btn.clicked.connect(funcao)
            grid_layout.addWidget(btn, row, col)
        
        scroll_layout.addWidget(grid_widget)
        
        # Espaçador
        scroll_layout.addStretch()
        
        # Separador antes do botão fechar
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setFrameShadow(QFrame.Sunken)
        separator2.setStyleSheet("background-color: #CCC; margin: 10px 0;")
        scroll_layout.addWidget(separator2)
        
        # Botão Fechar Aplicação
        btn_fechar_layout = QHBoxLayout()
        btn_fechar = QPushButton("🚪 Fechar Aplicação")
        btn_fechar.setFont(QFont("Arial", 11))
        btn_fechar.setMinimumHeight(45)
        btn_fechar.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px;
                font-weight: bold;
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
        scroll_layout.addLayout(btn_fechar_layout)
        
        # Rodapé
        footer = QLabel("© 2025 Sistema de Gestão de Escalas - SQLite")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: #999; font-size: 9px; margin-top: 5px;")
        scroll_layout.addWidget(footer)
        
        # Configurar scroll
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
        
        # Estilo geral da janela
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QScrollArea {
                background-color: #f5f5f5;
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: #E0E0E0;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #BDBDBD;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #9E9E9E;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
    
    def darken_color(self, hex_color):
        """Escurece uma cor hexadecimal para o efeito hover"""
        # Remove o # se existir
        hex_color = hex_color.lstrip('#')
        
        # Converte para RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # Escurece
        r = max(0, r - 20)
        g = max(0, g - 20)
        b = max(0, b - 20)
        
        # Retorna formato hexadecimal
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def darker_color(self, hex_color):
        """Escurece ainda mais para o efeito pressed"""
        # Remove o # se existir
        hex_color = hex_color.lstrip('#')
        
        # Converte para RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # Escurece mais
        r = max(0, r - 40)
        g = max(0, g - 40)
        b = max(0, b - 40)
        
        # Retorna formato hexadecimal
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def abrir_gerador_escalas(self):
        try:
            from gerador import mostrar_gerador
            mostrar_gerador()
        except Exception as e:
            print(f"Erro ao abrir Gerador: {e}")
            self.mostrar_erro("Gerador de Escalas", e)

    def abrir_folgas(self):
        """Abre a gestão de folgas"""
        try:
            from folgas import mostrar_folgas
            mostrar_folgas()
        except Exception as e:
            print(f"Erro ao abrir Gestão de Folgas: {e}")
            self.mostrar_erro("Gestão de Folgas", e)

    def abrir_ferias(self):
        """Abre a gestão de férias"""
        try:
            from ferias import mostrar_ferias
            mostrar_ferias()
        except Exception as e:
            print(f"Erro ao abrir Gestão de Férias: {e}")
            self.mostrar_erro("Gestão de Férias", e)

    def abrir_mapa_ferias(self):
        """Abre o mapa de férias"""
        try:
            from mapaFerias import mostrar_mapa_ferias
            mostrar_mapa_ferias()
        except Exception as e:
            print(f"Erro ao abrir Mapa de Férias: {e}")
            self.mostrar_erro("Mapa de Férias", e)

    def abrir_dias_fixos(self):
        """Abre a gestão de dias fixos"""
        try:
            from diasFixos import mostrar_dias_fixos
            mostrar_dias_fixos()
        except Exception as e:
            print(f"Erro ao abrir Dias Fixos: {e}")
            self.mostrar_erro("Dias Fixos", e)

    def abrir_configuracoes(self):
        """Abre as configurações"""
        try:
            from configuracoes import mostrar_configuracoes
            mostrar_configuracoes()
        except Exception as e:
            print(f"Erro ao abrir Configurações: {e}")
            self.mostrar_erro("Configurações", e)
    
    def abrir_gerador_apoios(self):
        """Abre o gerador de apoios"""
        try:
            from geradorApoios import mostrar_gerador_apoios
            mostrar_gerador_apoios()
        except ImportError:
            # Se o módulo ainda não existe, mostra mensagem informativa
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(
                self, 
                "Gerador de Apoios", 
                "O módulo Gerador de Apoios será implementado em breve.\n\n"
                "Prepare o ficheiro geradorApoios.py com a função mostrar_gerador_apoios()."
            )
        except Exception as e:
            print(f"Erro ao abrir Gerador de Apoios: {e}")
            self.mostrar_erro("Gerador de Apoios", e)

    def mostrar_erro(self, modulo, erro):
        """Mostra mensagem de erro amigável"""
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.warning(
            self, 
            f"Erro - {modulo}", 
            f"Não foi possível abrir o módulo {modulo}:\n\n{erro}\n\n"
            "Verifique se o ficheiro existe e não tem erros."
        )

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
