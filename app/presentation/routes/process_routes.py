# tcc_good_code/app/presentation/routes/process_routes.py

from threading import Thread

from flasgger import swag_from
from flask import Blueprint, current_app

from app.domain.responses.api_response import internal_error_response, success_response
from app.infrastructure.logger import logger
from app.services.user_service import UserService

process_bp = Blueprint("process_bp", __name__)


def process_users(app):
    """
    Função que realiza o processamento dos usuários em segundo plano.
    """
    with app.app_context():

        injector = current_app.injector
        user_service = injector.get(UserService)
        try:
            user_service.process_all_users()
            logger.info("Processamento concluído com sucesso.")
        except Exception as e:
            logger.error("Erro durante o processamento dos usuários: %s", e)


@process_bp.route("/", methods=["POST"])
@swag_from("../docs/process_routes.yml")
def process_route():
    """
    Inicia o processamento de todos os usuários em segundo plano.
    """
    try:

        app = current_app._get_current_object()
        thread = Thread(target=process_users, args=(app,))
        thread.start()
        logger.info("Processamento iniciado em background.")
        return success_response(message="Processamento iniciado em background.")
    except Exception as e:
        logger.error("Erro ao iniciar o processamento em background: %s", e)
        return internal_error_response(
            message="Erro ao iniciar o processamento dos usuários."
        )


def register_routes(app):
    """Registra as rotas de processamento no app Flask."""
    app.register_blueprint(process_bp, url_prefix="/process")
