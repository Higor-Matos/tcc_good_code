# tcc_good_code/app/presentation/routes/process_routes.py

from flasgger import swag_from
from flask import Blueprint, Flask, g

from app.domain.responses.api_response import internal_error_response, success_response
from app.infrastructure.logger import logger
from app.services.user_service import UserService

process_bp = Blueprint("process_bp", __name__)


@process_bp.route("/", methods=["POST"])
@swag_from("../docs/process_routes.yml")
def process_route():
    """
    Processa todos os usuários, gerando e enviando notas se necessário.
    """
    user_service = g.injector.get(UserService)

    logger.info("Iniciando o processamento de todos os usuários.")
    try:
        user_service.process_all_users()
        logger.info("Processamento concluído com sucesso.")
        return success_response(message="Processamento concluído com sucesso.")
    except Exception as e:
        logger.error("Erro durante o processamento dos usuários: %s", e)
        return internal_error_response(
            message="Erro durante o processamento dos usuários."
        )


def register_routes(app: Flask):
    """Registra as rotas de processamento no app Flask."""
    app.register_blueprint(process_bp, url_prefix="/process")
