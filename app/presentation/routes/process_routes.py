# tcc_good_code/app/presentation/routes/process_routes.py

from flasgger import swag_from
from flask import Blueprint
from injector import inject

from app.domain.responses.api_response import internal_error_response, success_response
from app.infrastructure.logger import logger
from app.services.user_service import UserService

process_bp = Blueprint("process_bp", __name__)


@process_bp.route("/", methods=["POST"])
@inject
@swag_from("../docs/process_routes.yml")
def process_route(user_service: UserService):
    """
    Processa todos os usuários, gerando e enviando notas se necessário.
    """
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
