# tcc_good_code/app/presentation/routes/user_routes.py

from flask import Blueprint, g

from app.domain.responses.api_response import internal_error_response, success_response
from app.infrastructure.logger import logger
from app.repository.user_repository import UserRepository

user_bp = Blueprint("user_bp", __name__)


@user_bp.route("/", methods=["GET"])
def get_users():
    """
    Retorna todos os usuários cadastrados no banco de dados.
    """
    user_repository = g.injector.get(
        UserRepository
    )  # Obtendo o UserRepository pelo Injector

    logger.info("Requisição recebida para listar todos os usuários.")
    try:
        users = user_repository.get_all_users()
        logger.info("Usuários recuperados com sucesso. Total: %d", len(users))
        return success_response(data=users)
    except Exception as e:
        logger.error("Erro ao recuperar usuários: %s", e)
        return internal_error_response(message="Erro ao recuperar usuários")


def register_routes(app):
    app.register_blueprint(user_bp, url_prefix="/users")
