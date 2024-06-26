from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

import pickle
import pandas as pd
import numpy as np

from datetime import date, datetime

from sklearn.preprocessing import StandardScaler

# Carrega o modelo 
with open('ml/rf_model.pkl', 'rb') as f:
    rf_model = pickle.load(f)

with open('ml/scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

app = Flask(__name__)
app.secret_key = '1234'

DATABASE = 'bd/bd_sysad.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


"""
    Rotas Publicas
"""
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/sobre')
def sobre():
    return render_template('sobre.html')

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
            
            if user['tipo'] == 'admin':
                return redirect(url_for('dashboard'))
            
            return redirect(url_for('index'))
        else:
            flash('Email ou senha errada. Por favor tente novamente.', 'danger')
    
    return render_template('login.html')


@app.route('/detalhePaciente/<int:id_paciente>')
def detalhePaciente(id_paciente):
    
    if 'user_id' in session:
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            SELECT paciente.*, previsao.*
            FROM paciente
            JOIN previsao ON previsao.id_paciente = paciente.id
            WHERE paciente.id = ?
            
        ''', (id_paciente,))
        paciente = cursor.fetchone()
        return render_template('detalhePaciente.html', paciente=paciente)
    
    return redirect(url_for('login'))
    
# Rota para pesquisa de paciente por nome
@app.route('/pesquisar', methods=['GET', 'POST'])
def pesquisar_paciente():
    if request.method == 'POST':
        pesquisa = request.form['pesquisa']
        user_id = session['user_id']
        db = get_db()
        cursor = db.cursor()

        # Obter o número da página a partir do parâmetro da URL
        page = request.args.get('page', 1, type=int)
        per_page = 10  # Número de registros por página
        offset = (page - 1) * per_page

        cursor.execute('''
            SELECT paciente.*, previsao.previsao, previsao.id_profissional
            FROM paciente
            JOIN previsao ON previsao.id_paciente = paciente.id
            WHERE previsao.id_profissional = ? and paciente.nome LIKE ?
            ORDER BY paciente.id DESC
            LIMIT ? OFFSET ?
        ''', (user_id, '%' + pesquisa + '%', per_page, offset))

        pacientes = cursor.fetchall()

        # Obter o total de registros
        cursor.execute('''
            SELECT COUNT(*)
            FROM paciente
            JOIN previsao ON previsao.id_paciente = paciente.id
            WHERE previsao.id_profissional = ?
        ''', (user_id,))
        total_pacientes = cursor.fetchone()[0]

        total_pages = (total_pacientes + per_page - 1) // per_page

        return render_template('consultaPaciente.html', pacientes=pacientes, page=page, total_pages=total_pages)
        
    return render_template('index.html')
    
 
 
@app.route('/logout')
def logout():
    session.clear()
    flash('Sessão Terminada.', 'success')
    return redirect(url_for('login'))
   

@app.route('/previsao', methods=['GET', 'POST'])
def previsao():
    if request.method == 'POST':
        
        # Obter dados do formulário
            #calcular a idade
        idade = int(date.today().year) - int(date.fromisoformat(request.form['nascimento']).year)
        
        age = idade
        sex = int(request.form['sexo'])
        cp = int(request.form['dor'])
        trestbps = int(request.form['ta'])
        chol = int(request.form['colesterol'])
        fbs = int(request.form['glicemia'])
        restecg = int(request.form['result_eletrocardiografico'])
        thalach = int(request.form['freq_cardiaca'])
        exang = int(request.form['angina'])
        oldpeak = request.form['oldpeak']
        slope = int(request.form['inclinacao_st'])
        ca = int(request.form['num_vasos'])
        thal = int(request.form['talassemia'])

        # Criar array com os dados do paciente
        dados_paciente = np.array([[age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal]])

        # Escalonar os dados do paciente
        dados_paciente_scaled = scaler.transform(dados_paciente)

        # Fazer a previsão com o modelo Random Forest
        previsao = rf_model.predict(dados_paciente_scaled)
        prediction_proba = rf_model.predict_proba(dados_paciente_scaled)

        # Resultado da previsão
        resultado_da_previsao = 'Doente' if previsao[0] == 1 else 'Saudável'
        probabilidade = prediction_proba[0][previsao[0]] * 100
        
        previsao_mensagem = f'O paciente está {resultado_da_previsao} com uma probabilidade de {probabilidade:.0f}%'
        # Salvar os dados do paciente e do diagnostico na BD
        gardarPrevisao(request.form, previsao_mensagem)

        flash(previsao_mensagem, 'success')
        return redirect(url_for('previsao'))
        r#eturn f'O paciente está {result} com uma probabilidade de {prob:.2f}%'
    
               
    return render_template('previsao.html')


@app.route('/consultaPrevisao')
def consultaPrevisao():
    if 'user_id' in session:
        user_id = session['user_id']
        db = get_db()
        cursor = db.cursor()

        # Obter o número da página a partir do parâmetro da URL
        page = request.args.get('page', 1, type=int)
        per_page = 10  # Número de registros por página
        offset = (page - 1) * per_page

        cursor.execute('''
            SELECT p.*, pa.nome AS paciente_nome, pa.id AS paciente_id, pa.data_nascimento, pa.sexo, pa.endereco, pa.telefone, pa.email
            FROM previsao p
            JOIN paciente pa ON p.id_paciente = pa.id
            WHERE p.id_profissional = ?
            ORDER BY p.id DESC
            LIMIT ? OFFSET ?
        ''', (user_id, per_page, offset))

        previsoes = cursor.fetchall()

        # Obter o total de registros
        cursor.execute('''
            SELECT COUNT(*)
            FROM previsao p
            JOIN paciente pa ON p.id_paciente = pa.id
            WHERE p.id_profissional = ?
        ''', (user_id,))
        total_previsoes = cursor.fetchone()[0]

        total_pages = (total_previsoes + per_page - 1) // per_page

        return render_template('consultaPrevisao.html', previsoes=previsoes, page=page, total_pages=total_pages)
    return redirect(url_for('login'))

@app.route('/consultaPaciente')
def consultaPaciente():
    
    if 'user_id' in session:
        user_id = session['user_id']
        db = get_db()
        cursor = db.cursor()

        # Obter o número da página a partir do parâmetro da URL
        page = request.args.get('page', 1, type=int)
        per_page = 10  # Número de registros por página
        offset = (page - 1) * per_page

        cursor.execute('''
            SELECT paciente.*, previsao.previsao, previsao.id_profissional
            FROM paciente
            JOIN previsao ON previsao.id_paciente = paciente.id
            WHERE previsao.id_profissional = ?
            ORDER BY paciente.id DESC
            LIMIT ? OFFSET ?
        ''', (user_id, per_page, offset))

        pacientes = cursor.fetchall()

        # Obter o total de registros
        cursor.execute('''
            SELECT COUNT(*)
            FROM paciente
            JOIN previsao ON previsao.id_paciente = paciente.id
            WHERE previsao.id_profissional = ?
        ''', (user_id,))
        total_pacientes = cursor.fetchone()[0]

        total_pages = (total_pacientes + per_page - 1) // per_page

        return render_template('consultaPaciente.html', pacientes=pacientes, page=page, total_pages=total_pages)
    return redirect(url_for('login'))
    
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
    




"""
    Rotas do Dashboard
"""

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        nome_profissional = session['nome']  # Obtém o nome do profissional da sessão
        return render_template('dashboard/dashboard.html', nome_profissional=nome_profissional)
    return redirect(url_for('login'))


@app.route('/listarPrevisoes')
def listarPrevisoes():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    db = get_db()
    cursor = db.cursor()
    previsoes = cursor.execute('''
        SELECT previsao.*, paciente.nome as paciente_nome, profissional.nome as profissional_nome
        FROM previsao
        JOIN paciente ON previsao.id_paciente = paciente.id
        JOIN profissional ON previsao.id_profissional = profissional.id
        LIMIT ? OFFSET ?''', (per_page, offset)).fetchall()

    total_previsoes = cursor.execute('SELECT COUNT(*) FROM previsao').fetchone()[0]
    cursor.close()

    total_pages = (total_previsoes + per_page - 1) // per_page

    return render_template('dashboard/previsaoAdmin.html', previsoes=previsoes, page=page, total_pages=total_pages)


@app.route('/listarProfissional')
def listarProfissional():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    db = get_db()
    cursor = db.cursor()
    profissionais = cursor.execute('''
        SELECT *
        FROM profissional
        LIMIT ? OFFSET ?''', (per_page, offset)).fetchall()

    total_profissionais = cursor.execute('SELECT COUNT(*) FROM previsao').fetchone()[0]
    cursor.close()

    total_pages = (total_profissionais + per_page - 1) // per_page

    return render_template('dashboard/profissionalAdmin.html', profissionais=profissionais, page=page, total_pages=total_pages)
    
     
if __name__ == '__main__':
    app.run(debug=True)
