# database.py
import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        import os
        import sys
        import shutil

        self.connection = None
        self.db_file = "escala_trabalho.db"
        self.dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sábado', 'Domingo']

        # === CÓPIA AUTOMÁTICA DA BD NO EXECUTÁVEL ===
        if getattr(sys, 'frozen', False):  # Roda como executável (PyInstaller)
            bundle_dir = sys._MEIPASS
            bundled_db = os.path.join(bundle_dir, 'escala_trabalho.db')
            if os.path.exists(bundled_db) and not os.path.exists(self.db_file):
                shutil.copy(bundled_db, self.db_file)
        # ===========================================

        self.connect()
    
    def connect(self):
        try:
            self.connection = sqlite3.connect(self.db_file)
            self.connection.row_factory = sqlite3.Row
            self.create_tables()
            return True
        except Exception as e:
            print(f"Erro ao conectar à base de dados: {e}")
            return False
    
    def create_tables(self):
        tables = [
            """CREATE TABLE IF NOT EXISTS pessoas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                horas_diarias INTEGER DEFAULT 8,
                cor_hex TEXT DEFAULT '#FFFFFF',
                ativo BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            
            """CREATE TABLE IF NOT EXISTS ferias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pessoa_id INTEGER NOT NULL,
                data_inicio DATE NOT NULL,
                data_fim DATE NOT NULL,
                descricao TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pessoa_id) REFERENCES pessoas(id) ON DELETE CASCADE
            )""",
            
            """CREATE TABLE IF NOT EXISTS horarios_fixos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pessoa_id INTEGER NOT NULL,
                data DATE NOT NULL,
                horario TEXT NOT NULL,
                descricao TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pessoa_id) REFERENCES pessoas(id) ON DELETE CASCADE,
                UNIQUE(pessoa_id, data)
            )""",
            
            """CREATE TABLE IF NOT EXISTS folgas_ciclo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pessoa_id INTEGER NOT NULL,
                semana_referencia INTEGER NOT NULL,
                dia_semana INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pessoa_id) REFERENCES pessoas(id) ON DELETE CASCADE,
                UNIQUE(pessoa_id, semana_referencia, dia_semana)
            )""",
            
            """CREATE TABLE IF NOT EXISTS dias_loja_fechada (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data DATE NOT NULL UNIQUE,
                descricao TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            
            """CREATE TABLE IF NOT EXISTS escalas_geradas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_inicio DATE NOT NULL,
                num_semanas INTEGER NOT NULL,
                data_geracao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                descricao TEXT,
                UNIQUE(data_inicio, num_semanas)
            )""",
            
            """CREATE TABLE IF NOT EXISTS escala_detalhes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                escala_id INTEGER NOT NULL,
                pessoa_id INTEGER NOT NULL,
                data DATE NOT NULL,
                horario TEXT NOT NULL,
                dia_semana INTEGER NOT NULL,
                semana_numero INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (escala_id) REFERENCES escalas_geradas(id) ON DELETE CASCADE,
                FOREIGN KEY (pessoa_id) REFERENCES pessoas(id) ON DELETE CASCADE,
                UNIQUE(escala_id, pessoa_id, data)
            )"""
        ]
        
        cursor = self.connection.cursor()
        for table in tables:
            try:
                cursor.execute(table)
            except Exception as e:
                print(f"Erro ao criar tabela: {e}")
        self.connection.commit()
        
        # Inserir dados iniciais
        self.initialize_data()
    
    def initialize_data(self):
        # Verificar se já existem dados
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM pessoas")
        if cursor.fetchone()[0] == 0:
            # Inserir pessoas
            pessoas = [
                ('Susana A.', 8, '#E8F5E8'),
                ('António C.', 8, '#FFF3CD'),
                ('Antónia F.', 8, '#D4EDDA'),
                ('Magda G.', 8, '#CCE5FF'),
                ('Eduardo S.', 8, '#F0E6FF')
            ]
            
            cursor.executemany(
                "INSERT OR IGNORE INTO pessoas (nome, horas_diarias, cor_hex) VALUES (?, ?, ?)",
                pessoas
            )
            
            # Inserir dias em que a loja está fechada
            dias_fechada = [
                ('2025-12-25', 'Natal'),
                ('2026-01-01', 'Ano Novo')
            ]
            
            cursor.executemany(
                "INSERT OR IGNORE INTO dias_loja_fechada (data, descricao) VALUES (?, ?)",
                dias_fechada
            )
            
            self.connection.commit()
    
    def execute_query(self, query, params=None, fetch=False):
        try:
            if self.connection is None:
                self.connect()
            
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            
            if fetch:
                result = [dict(row) for row in cursor.fetchall()]
                return result
            else:
                self.connection.commit()
                return True
                
        except Exception as e:
            print(f"Erro na query: {e}")
            return None
    
    def get_pessoas(self):
        return self.execute_query("SELECT * FROM pessoas WHERE ativo = 1", fetch=True)
    
    def get_ferias(self):
        return self.execute_query("""
            SELECT f.id, p.nome, f.data_inicio, f.data_fim, f.descricao
            FROM ferias f
            JOIN pessoas p ON f.pessoa_id = p.id
            WHERE p.ativo = 1
            ORDER BY f.data_inicio
        """, fetch=True)
    
    def get_horarios_fixos(self):
        return self.execute_query("""
            SELECT p.nome, hf.data, hf.horario 
            FROM horarios_fixos hf 
            JOIN pessoas p ON hf.pessoa_id = p.id 
            WHERE p.ativo = 1
        """, fetch=True)
    
    def get_folgas_ciclo(self, pessoa_id):
        """Obtém as folgas do ciclo para uma pessoa (nova estrutura)"""
        return self.execute_query("""
            SELECT semana_id, dia_semana 
            FROM folgas_ciclo 
            WHERE pessoa_id = ? 
            ORDER BY semana_id, dia_semana
        """, (pessoa_id,), fetch=True)
    
    def get_dias_loja_fechada(self):
        return self.execute_query("SELECT data FROM dias_loja_fechada", fetch=True)
    
    def save_escala(self, data_inicio, num_semanas, schedule_data):
        try:
            # Salvar escala principal
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO escalas_geradas (data_inicio, num_semanas, descricao) 
                VALUES (?, ?, ?)
            """, (data_inicio, num_semanas, f"Escala gerada em {datetime.now()}"))
            
            escala_id = cursor.lastrowid
            
            # Salvar detalhes da escala
            for registro in schedule_data:
                for pessoa_nome, horario in registro.items():
                    if pessoa_nome not in ['Semana', 'Data', 'Dia', 'Data_obj']:
                        # Obter ID da pessoa
                        pessoa_result = self.execute_query(
                            "SELECT id FROM pessoas WHERE nome = ?", 
                            (pessoa_nome,), 
                            fetch=True
                        )
                        
                        if pessoa_result:
                            pessoa_id = pessoa_result[0]['id']
                            
                            cursor.execute("""
                                INSERT OR REPLACE INTO escala_detalhes 
                                (escala_id, pessoa_id, data, horario, dia_semana, semana_numero) 
                                VALUES (?, ?, ?, ?, ?, ?)
                            """, (
                                escala_id, 
                                pessoa_id, 
                                registro['Data_obj'].strftime('%Y-%m-%d'),
                                str(horario),
                                self.dias_semana.index(registro['Dia']),
                                registro['Semana']
                            ))
            
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Erro ao salvar escala: {e}")
            return False
    
    def close(self):
        if self.connection:
            self.connection.close()