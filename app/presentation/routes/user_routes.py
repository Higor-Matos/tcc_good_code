# tcc_good_code/app/presentation/routes/user_routes.py

from flasgger import swag_from
from flask import Blueprint, g

from app.domain.responses.api_response import internal_error_response, success_response
from app.domain.schemas.user_schema import UserSchema
from app.infrastructure.logger import logger
from app.repository.user_repository import UserRepository

user_bp = Blueprint("user_bp", __name__)


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

        for user in users:
            try:

                user_schema = UserSchema.model_validate(user, from_attributes=True)
                valid_users.append(user_schema.model_dump())
            except Exception as e:

                logger.error("Erro ao validar usuário %s: %s", user.id, e)

        logger.info(
            "Usuários válidos recuperados com sucesso. Total: %d", len(valid_users)
        )
        return success_response(data=valid_users)
    except Exception as e:
        logger.error("Erro ao recuperar usuários: %s", e)
        return internal_error_response(message="Erro ao recuperar usuários")


def register_routes(app):
    app.register_blueprint(user_bp, url_prefix="/users")
