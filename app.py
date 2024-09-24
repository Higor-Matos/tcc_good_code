# app.py

"""
Módulo principal do Flask que define as rotas e inicializa a aplicação.
"""

import os  # Import padrão do Python

from flask import Flask, jsonify, request  # Import de biblioteca de terceiros

from database import close_connection
from user_service import (  # Imports de funções locais
    add_new_user,
    get_all_users,
    process_all_users,
)

app = Flask(__name__)
app.teardown_appcontext(close_connection)


@app.route('/users', methods=['GET'])
def get_users():
    """
    Retorna todos os usuários cadastrados no banco de dados.
    """
    users = get_all_users()
    return jsonify(users)


@app.route('/add_user', methods=['POST'])
def add_user():
    """
    Adiciona um novo usuário com base nos dados fornecidos na requisição.
    """
    user_data = request.form.to_dict()
    if add_new_user(user_data):
        return 'Usuário adicionado com sucesso', 201
    return 'Erro ao adicionar usuário', 400


@app.route('/process', methods=['POST'])
def process_route():
    """
    Processa todos os usuários, gerando e enviando notas se necessário.
    """
    process_all_users()
    return 'Processamento concluído', 200


@app.route('/gerar_notas', methods=['GET'])
def gerar_notas():
    """
    Gera notas para todos os usuários e envia-as por e-mail.
    """
    process_all_users()
    return 'Notas geradas e enviadas com sucesso para todos os usuários', 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(port=port, use_reloader=False)
