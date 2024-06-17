# SISTEMA DE SUPORTE À DECISÃO PARA AUXILIAR MÉDICOS NO DIAGNÓSTICO DE DOENÇAS CARDIOVASCULARES (SYSAD-AI)

## Descrição do Projeto

Este projeto tem como objetivo desenvolver um Sistema de Suporte à Decisão para auxiliar médicos no diagnóstico de doenças cardiovasculares. Utilizando técnicas de aprendizado de máquina, especificamente o modelo Random Forest da biblioteca scikit-learn, o sistema pode prever a probabilidade de um paciente ter uma doença cardiovascular com base em seus dados médicos. O sistema é construído com Flask, um microframework web em Python, e utiliza SQLite como banco de dados.

## Funcionalidades

- Cadastro e login de usuários (profissionais de saúde).
- Registro de pacientes com informações detalhadas.
- Entrada de dados médicos do paciente para predição.
- Predição de doenças cardiovasculares usando o modelo Random Forest.
- Visualização das previsões e histórico de diagnósticos.
- Visualização dos pacientes e seu diagnósticos.
- Interface web responsiva com Bootstrap.

## Estrutura do Projeto

```
/SYSAD-AI
|
├── bd/
│   ├── bd_sysad.db
│   └── bd_sysad.sql
│   └── bd_sysad.py
|
├── ml/
│   ├── rf_model.pkl # Modelo "random forest" treinado
│   └── gb_model.pkl  # Modelo "Gradient Boosting" treinado
│   └── heart_disease_data.csv  # Dataset do projecto
│   └── scaler.pkl
│   └── sysad-ai.ipynb
│   └── treinar_modelo.py
|
├── static/
│   ├── css/
│   └── fonts/
│   └── img/
│   └── js/
│
├── templates/
│   ├── base.html
│   ├── cadastroUsuariio.html
│   └── consultaPaciente.html
│   └── consultaPrevisao.html
│   ├── dashboard.html
│   └── index.html
│   ├── login.html
│   └── previsao.html
│
├── app.py
└── README.md
```

## Tecnologias Utilizadas

- **Backend**: Flask(Python)
- **Frontend**: HTML, CSS, Javascript, Bootstrap
- **Banco de Dados**: SQLite
- **Modelos de Machine Learning**: scikit-learn (Random Forest, Gradient Boosting), o random forest é o principal moelo usado
- **Outras Bibliotecas**: pandas, numpy, SQLAlchemy, werkzeug

## Instalação e Execução

### Pré-requisitos

- Python 3.7+
- pip (Python package installer)

### Passos para Instalação

1. **Clone o repositório:**

    ```bash
    git clone https://github.com/Ximana/sysad-ai.git
    cd sysad-ai
    ```

2. **Crie um ambiente virtual:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows, use `venv\Scripts\activate`
    ```

3. **Instale as dependências:**

    ```bash
    pip install -r pandas
    pip install -r numpy
    pip install -r flask
    ```

4. **Prepare o banco de dados:**

    ```bash
    python bd_sysad.py
    ```

5. **Treine o modelo de machine learning:**

    ```bash
    python ml/treinar_modelo.py
    ```

6. **Execute o aplicativo:**

    ```bash
    flask run
    ```

    O aplicativo estará disponível em `http://127.0.0.1:5000`.

## Uso do Sistema

### Cadastro e Login

- Acesse a página inicial e faça o cadastro de um novo usuário (profissional de saúde).
- Após o cadastro, faça login com suas credenciais.

### Registro de Pacientes

- Após o login, você será redirecionado para o dashboard.
- No dashboard, registre novos pacientes com suas informações pessoais e médicas.

### Predição de Doenças Cardiovasculares

- No formulário de registro de previsões, insira os dados do paciente e os dados médicos necessários.
- O sistema realizará a predição e exibirá os resultados.

### Visualização de Previsões

- Acesse a página de histórico para visualizar todas as previsões feitas por você.

## Modelo de Machine Learning

O modelo Random Forest é usado para realizar as predições de doenças cardiovasculares. Este modelo foi escolhido por sua robustez e precisão em tarefas de classificação. O código para treinamento do modelo está no arquivo `treinar_modelo.py`.

No entanto o arquivo `treinar_modelo.py` treina e gera modelo "Gradient Boosting" como segunda opção.

O arquivo `app.py` contém a funcao `predict_GB()` que usa o "Gradient Boosting"

### Treinamento do Modelo

O script `treinar_modelo.py` carrega os dados, treina os modelos "Random Forest" e "Gradient Boosting" e salva o modelos treinados em um arquivo para uso posterior.

## Contribuição

Contribuições são bem-vindas! Por favor, abra uma issue ou envie um pull request para discutir qualquer mudança que você gostaria de fazer.

## Licença

---

Espero que este README forneça uma visão clara e detalhada do projeto. Se houver qualquer dúvida ou sugestão, sinta-se à vontade para entrar em contato.