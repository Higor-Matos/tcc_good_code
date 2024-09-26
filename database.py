# tcc_good_code/database.py


"""
Módulo responsável por gerenciar a conexão com o banco de dados.
"""

import sqlite3

from flask import g

DATABASE = "database.db"


def get_db():
    """
    Retorna a conexão com o banco de dados, criando-a se não existir.
    """
    if not hasattr(g, "database"):
        g.database = sqlite3.connect(DATABASE)
    return g.database


def close_connection(_):
    """
    Fecha a conexão com o banco de dados se existir.

    Args:
        _: Argumento de exceção necessário para o hook `teardown_appcontext`,
           mas não utilizado.
    """
    db = g.pop("database", None)
    if db is not None:
        db.close()
