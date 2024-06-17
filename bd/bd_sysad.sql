

CREATE TABLE usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL,
    tipo TEXT NOT NULL,
    data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE paciente (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    data_nascimento DATE NOT NULL,
    sexo TEXT NOT NULL,
    endereco TEXT,
    telefone TEXT,
    email TEXT UNIQUE NOT NULL,
    data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE profissional (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER,
    nome TEXT NOT NULL,
    categoria TEXT NOT NULL,
    especialidade TEXT NOT NULL,
    telefone TEXT,
    data_registo DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id)
);

CREATE TABLE previsao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_paciente INTEGER,
    id_profissional INTEGER,
    data DATETIME DEFAULT CURRENT_TIMESTAMP,
    dor_toracica TEXT,
    ta TEXT,
    colesterol INTEGER,
    glicemia INTEGER,
    resultados_eletrocardiograficos TEXT,
    frequencia_cardiaca INTEGER,
    angina TEXT,
    oldpeak REAL,
    inclinacao_st TEXT,
    num_vasos_principais INTEGER,
    talassemia TEXT,
    previsao TEXT,
    FOREIGN KEY (id_paciente) REFERENCES paciente(id),
    FOREIGN KEY (id_profissional) REFERENCES profissional(id)
);
