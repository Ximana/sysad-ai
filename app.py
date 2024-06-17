from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

import pickle
import pandas as pd
import numpy as np

from datetime import date, datetime

# Carrega o modelo 
with open('ml/rf_model.pkl', 'rb') as f:
    rf_model = pickle.load(f)

with open('ml/scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Substitua por uma chave secreta forte

DATABASE = 'bd/bd_sysad.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/cadastroUsuariio', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        categoria = request.form['categoria']
        especialidade = request.form['especialidade']
        telefone = request.form['telefone']
        hashed_password = generate_password_hash(senha)
        
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute('INSERT INTO usuario (email, senha, tipo) VALUES (?, ?, ?)', (email, hashed_password, 'profissional'))
            user_id = cursor.lastrowid
            cursor.execute('INSERT INTO profissional (id_usuario, nome, categoria, especialidade, telefone) VALUES (?, ?, ?, ?, ?)', (user_id, nome, categoria, especialidade, telefone))
            db.commit()
            flash('Usuario cadastrado com sucesso, pode fazer o login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('O omail inserido já está associada a uma conta. por favor insira outro email.', 'danger')
    
    return render_template('cadastroUsuariio.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM usuario WHERE email = ?', (email,))
        user = cursor.fetchone()
        
        if user and check_password_hash(user['senha'], senha):
            # Busca informações adicionais do profissional
            cursor.execute('SELECT * FROM profissional WHERE id_usuario = ?', (user['id'],))
            profissional = cursor.fetchone()

            session['user_id'] = user['id']
            session['email'] = user['email']
            session['nome'] = profissional['nome']  # Armazena o nome na sessão
            flash('Login com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Email ou senha errada. Por favor tente novamente.', 'danger')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        nome_profissional = session['nome']  # Obtém o nome do profissional da sessão
        return render_template('dashboard.html', nome_profissional=nome_profissional)
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Sessão Terminada.', 'success')
    return redirect(url_for('login'))

@app.route('/previsao', methods=['GET', 'POST'])
def previsao():
    if request.method == 'POST':
        
        # Obter o resultado d diagnostico
        previsao =  predict(request.form) # faz o diagnostico do paciente com os dados do fomrulario
        
        previsao = "Possibilidade de uma doença cardiovascular" if previsao == "1" else "Sem possibilidade de uma doença cardiovascular"
                
        # Salvar os dados do paciente e do diagnostico na BD
        gardarPrevisao(request.form, previsao)
        
        flash('Resultado da previsao: '+ previsao +'.', 'success')
        return redirect(url_for('previsao'))
               
    return render_template('previsao.html')

@app.route('/consultaPrevisao')
def consultaPrevisao():
    
    if 'user_id' in session:
        user_id = session['user_id']
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            SELECT p.*, pa.nome AS paciente_nome, pa.data_nascimento, pa.sexo, pa.endereco, pa.telefone, pa.email
            FROM previsao p
            JOIN paciente pa ON p.id_paciente = pa.id
            WHERE p.id_profissional = ?
            ORDER BY p.id
            DESC 
        ''', (user_id,))
        previsoes = cursor.fetchall()
        return render_template('consultaPrevisao.html', previsoes=previsoes)
    return redirect(url_for('login'))

@app.route('/consultaPaciente')
def consultaPaciente():
    
    if 'user_id' in session:
        user_id = session['user_id']
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            SELECT paciente.*, previsao.previsao, previsao.id_profissional
            FROM paciente
            JOIN previsao ON previsao.id_paciente = paciente.id
            WHERE previsao.id_profissional = ?
            ORDER BY paciente.id
            DESC 
        ''', (user_id,))
        pacientes = cursor.fetchall()
        return render_template('consultaPaciente.html', pacientes=pacientes)
    return redirect(url_for('login'))


def predict(paciente):
    
    try:        
        idade = date.today().year - date.fromisoformat(paciente['nascimento']).year
        novo_paciente = {
            'age': idade,
            'sex': paciente['sexo'],
            'cp': paciente['dor'],
            'trestbps': paciente['ta'],
            'chol': paciente['colesterol'],
            'fbs': paciente['glicemia'],
            'restecg': paciente['result_eletrocardiografico'],
            'thalach': paciente['freq_cardiaca'],
            'exang': paciente['angina'],
            'oldpeak': paciente['oldpeak'],
            'slope': paciente['inclinacao_st'],
            'ca': paciente['num_vasos'],
            'thal': paciente['talassemia'],
        }
            
        #data = request.form.to_dict()
        df_novo_paciente = pd.DataFrame([novo_paciente])
        
        # Converter os dados para os tipos corretos
        #df = df.astype(float)
        
        # Pré-processar os dados
        df_scaled_novo_paciente = scaler.transform(df_novo_paciente)
        
        # Previsão com Random Forest
        rf_prediction = rf_model.predict(df_scaled_novo_paciente)
        
        return str(rf_prediction[0]) # Previsão Random Forest
    
    except Exception as e:
        return f'Erro: {str(e)}', 400
   
    
def gardarPrevisao(form, previsao):
    
    # Receber e converter os valores do formulário
    formulario = {
        "nome": request.form['nome'],
        "nascimento": request.form['nascimento'],
        "endereco": request.form['endereco'],
        "telefone": request.form['telefone'],
        "email": request.form['email'],
        "ta": request.form['ta'],
        "colesterol": request.form['colesterol'],
        "freq_cardiaca": request.form['freq_cardiaca'],
        "oldpeak": request.form['oldpeak'],
        "num_vasos": request.form['num_vasos'],
        "previsao": previsao,
    }

    # Verificar e converter campos de formulário
    formulario['sexo'] = "Masculino" if request.form['sexo'] == "1" else "Feminino"

    dor_opcoes = {
        "0": "Assintomático",
        "1": "Angina atípica",
        "2": "Dor não anginosa",
        "3": "Angina típica"
    }
    formulario['dor'] = dor_opcoes.get(request.form['dor'], "Desconhecido")

    formulario['glicemia'] = 'Sim' if request.form['glicemia'] == "1" else 'Não'
    formulario['angina'] = 'Sim' if request.form['angina'] == "1" else 'Não'

    inclinacao_st_opcoes = {
        "0": "Descendente",
        "1": "Plano",
        "2": "Ascendente"
    }
    formulario['inclinacao_st'] = inclinacao_st_opcoes.get(request.form['inclinacao_st'], "Desconhecido")

    talassemia_opcoes = {
        "1": "Defeito fixo",
        "2": "Normal",
        "3": "Defeito reversível"
    }
    formulario['talassemia'] = talassemia_opcoes.get(request.form['talassemia'], "Desconhecido")

    result_eletrocardiografico_opcoes = {
        "0": "Mostrando hipertrofia ventricular esquerda provável ou definitiva pelos critérios de Estes",
        "1": "Normal",
        "2": "Com anormalidade nas ondas ST-T"
    }
    formulario['result_eletrocardiografico'] = result_eletrocardiografico_opcoes.get(request.form['result_eletrocardiografico'], "Desconhecido")

     # Salvar a previsão na BD
    try:
        db = get_db()
        cursor = db.cursor()

        # Inserir dados do paciente
        cursor.execute("""
            INSERT INTO paciente (nome, data_nascimento, sexo, endereco, telefone, email)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (formulario['nome'], formulario['nascimento'], formulario['sexo'], formulario['endereco'], formulario['telefone'], formulario['email']))

        # Obter o ID do paciente recém-inserido
        id_paciente = cursor.lastrowid

        # Inserir dados da previsão
        cursor.execute("""
            INSERT INTO previsao (id_paciente, id_profissional, dor_toracica, ta, colesterol, glicemia, resultados_eletrocardiograficos, frequencia_cardiaca, angina, oldpeak, inclinacao_st, num_vasos_principais, talassemia, previsao)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (id_paciente, session['user_id'], formulario['dor'], formulario['ta'], formulario['colesterol'], formulario['glicemia'], formulario['result_eletrocardiografico'], formulario['freq_cardiaca'], formulario['angina'], formulario['oldpeak'], formulario['inclinacao_st'], formulario['num_vasos'], formulario['talassemia'], formulario['previsao']))

        db.commit()
        #flash('Previsão salva com sucesso!', 'success')
        return True
    
    except sqlite3.IntegrityError as e:
        flash(f'Erro ao salvar os dados: {e}', 'danger')
        return redirect(url_for('previsao'))
    
 
# Predizer com o Gradient Boosting
def predict_GB(paciente):
    
    try:        
        idade = date.today().year - date.fromisoformat(paciente['nascimento']).year
        novo_paciente = {
            'age': idade,
            'sex': paciente['sexo'],
            'cp': paciente['dor'],
            'trestbps': paciente['ta'],
            'chol': paciente['colesterol'],
            'fbs': paciente['glicemia'],
            'restecg': paciente['result_eletrocardiografico'],
            'thalach': paciente['freq_cardiaca'],
            'exang': paciente['angina'],
            'oldpeak': paciente['oldpeak'],
            'slope': paciente['inclinacao_st'],
            'ca': paciente['num_vasos'],
            'thal': paciente['talassemia'],
        }
            
        #data = request.form.to_dict()
        df_novo_paciente = pd.DataFrame([novo_paciente])
        
        # Converter os dados para os tipos corretos
        #df = df.astype(float)
        
        # Pré-processar os dados
        df_scaled_novo_paciente = scaler.transform(df_novo_paciente)
        
        # Previsão com Random Forest
        gb_prediction = gb_model.predict(df_scaled_novo_paciente)
        
        return str(gb_prediction[0]) # Previsão Gradient Boosting
    
    except Exception as e:
        return f'Erro: {str(e)}', 400
    
    
if __name__ == '__main__':
    app.run(debug=True)
