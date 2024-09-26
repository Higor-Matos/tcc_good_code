# tcc_good_code/app/presentation/routes/user_routes.py

from flasgger import swag_from
from flask import Blueprint
from injector import inject

from app.domain.responses.api_response import internal_error_response, success_response
from app.infrastructure.logger import logger
from app.repository.user_repository import UserRepository

user_bp = Blueprint("user_bp", __name__)


@user_bp.route("/", methods=["GET"])
@inject
@swag_from("../docs/user_routes.yml")
def get_users(user_repository: UserRepository):
    """
    Retorna todos os usuários cadastrados no banco de dados.
    """
    logger.info("Requisição recebida para listar todos os usuários.")
    try:
        users = user_repository.get_all_users()
        logger.info("Usuários recuperados com sucesso. Total: %d", len(users))
        return success_response(data=users)
    except Exception as e:
        logger.error("Erro ao recuperar usuários: %s", e)
        return internal_error_response(message="Erro ao recuperar usuários")
