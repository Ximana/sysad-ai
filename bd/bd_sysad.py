import sqlite3

DATABASE = 'bd_sysad.db'

def create_tables():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuario (
            id INTEGER,
            email TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL,
            tipo TEXT NOT NULL,
            data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY(id AUTOINCREMENT)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS paciente (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            data_nascimento DATE NOT NULL,
            sexo TEXT NOT NULL,
            endereco TEXT,
            telefone TEXT,
            email TEXT,
            data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profissional (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario INTEGER,
            nome TEXT NOT NULL,
            categoria TEXT NOT NULL,
            especialidade TEXT NOT NULL,
            telefone TEXT,
            data_registo DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_usuario) REFERENCES usuario(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS previsao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_paciente INTEGER,
            id_profissional INTEGER,
            data DATETIME DEFAULT CURRENT_TIMESTAMP,
            dor_toracica TEXT,
            ta TEXT,
            colesterol TEXT,
            glicemia TEXT,
            resultados_eletrocardiograficos TEXT,
            frequencia_cardiaca INTEGER,
            angina TEXT,
            oldpeak TEXT,
            inclinacao_st TEXT,
            num_vasos_principais TEXT,
            talassemia TEXT,
            previsao TEXT,
            FOREIGN KEY (id_paciente) REFERENCES paciente(id),
            FOREIGN KEY (id_profissional) REFERENCES profissional(id)
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_tables()
