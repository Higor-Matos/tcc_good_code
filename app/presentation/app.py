# tcc_good_code/app/presentation/app.py

import os

from flasgger import Swagger
from flask import Flask, g
from injector import Injector
from sqlalchemy.orm import scoped_session, sessionmaker

from app.infrastructure.database import init_db
from app.infrastructure.injector_module import InjectorModule
from app.infrastructure.load_envs import load_envs
from app.infrastructure.logger import setup_logger
from app.presentation.routes.process_routes import process_bp
from app.presentation.routes.user_routes import user_bp

load_envs()
logger = setup_logger()

app = Flask(__name__)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/swagger/",
}

swagger_template = {
    "info": {
        "title": "API de Exemplo",
        "description": "Documentação da API de Exemplo utilizando Flasgger",
        "version": "1.0.0",
    }
}

Swagger(app, config=swagger_config, template=swagger_template)

init_db()
logger.info("Banco de dados inicializado.")

injector = Injector([InjectorModule()])
logger.info("Injeção de dependências configurada.")

app.register_blueprint(user_bp, url_prefix="/users")
app.register_blueprint(process_bp, url_prefix="/process")
logger.info("Rotas registradas.")


@app.before_request
def before_request() -> None:
    """Inicia uma nova sessão de banco de dados antes de cada requisição."""
    session_factory = injector.get(sessionmaker)
    db_session = scoped_session(session_factory)
    setattr(g, "db_session", db_session)
    logger.info("Sessão de banco de dados iniciada para a requisição.")


@app.teardown_request
def teardown_request(exception=None) -> None:
    """Fecha a sessão de banco de dados após cada requisição."""
    session = getattr(g, "db_session", None)
    if session:
        session.remove()
        logger.info("Sessão de banco de dados encerrada para a requisição.")
    else:
        logger.warning("Nenhuma sessão encontrada para encerrar.")


if __name__ == "__main__":
    app_name = os.getenv("APP_NAME", "Flask App")
    app_port = int(os.getenv("APP_PORT", "5000"))
    logger.info("Iniciando servidor %s na porta %d.", app_name, app_port)
    app.run(port=app_port, use_reloader=False)
