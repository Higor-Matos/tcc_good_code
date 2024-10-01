# tcc_good_code/app/presentation/routes/user_routes.py

from concurrent.futures import ThreadPoolExecutor, as_completed

from flasgger import swag_from
from flask import Blueprint, g, request

from app.domain.responses.api_response import (
    bad_request_response,
    internal_error_response,
    success_response,
)
from app.domain.schemas.user_schema import UserSchema
from app.domain.utils import validate_user
from app.infrastructure.logger import logger
from app.repository.user_repository import UserRepository

user_bp = Blueprint("user_bp", __name__)


@user_bp.route("/add_user", methods=["POST"])
@swag_from("../docs/add_user.yml")
def add_user():
    """
    Adiciona um novo usuário no banco de dados.
    """
    user_repository = g.injector.get(UserRepository)
    try:

        user_data = request.get_json()

        user_schema = UserSchema(**user_data)

        new_user = user_repository.add_user(user_schema)

        if new_user:
            logger.info("Usuário adicionado com sucesso: %s", new_user.email)
            return success_response(data={"id": new_user.id, "email": new_user.email})
        return internal_error_response(message="Erro ao adicionar o usuário.")
    except Exception as e:
        logger.error("Erro ao processar o request de adição de usuário: %s", e)
        return bad_request_response(
            message=f"Erro ao processar os dados do usuário: {str(e)}"
        )


@user_bp.route("/", methods=["GET"])
@swag_from("../docs/user_routes.yml")
def get_users():
    """
    Retorna todos os usuários cadastrados no banco de dados.
    """
    user_repository = g.injector.get(UserRepository)
    logger.info("Requisição recebida para listar todos os usuários.")
    try:
        users = user_repository.get_all_users()
        valid_users = []

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(validate_user, user): user for user in users}
            for future in as_completed(futures):
                result = future.result()
                if result:
                    valid_users.append(result)

        logger.info(
            "Usuários válidos recuperados com sucesso. Total: %d", len(valid_users)
        )
        return success_response(data=valid_users)
    except Exception as e:
        logger.error("Erro ao recuperar usuários: %s", e)
        return internal_error_response(message="Erro ao recuperar usuários")


def register_routes(app):
    app.register_blueprint(user_bp, url_prefix="/users")
