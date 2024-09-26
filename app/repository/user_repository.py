# tcc_good_code/app/repository/user_repository.py

from injector import inject
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.domain.entities.user import User
from app.domain.schemas.user_schema import UserSchema
from app.infrastructure.logger import logger


class UserRepository:
    @inject
    def __init__(self, db: Session):
        self.db = db

    def get_all_users(self):
        """Recupera todos os usuários do banco de dados."""
        try:
            users = self.db.query(User).all()
            logger.info("Obtidos todos os usuários com sucesso. Total: %d", len(users))
            return users
        except SQLAlchemyError as e:
            logger.error("Erro ao obter todos os usuários: %s", e)
            return []

    def get_user_by_id(self, user_id: int):
        """Recupera um usuário pelo ID."""
        try:
            user = self._find_user_by_id(user_id)
            if user:
                logger.info("Usuário obtido com sucesso: ID %s", user_id)
            else:
                logger.warning("Usuário não encontrado: ID %s", user_id)
            return user
        except SQLAlchemyError as e:
            logger.error("Erro ao obter o usuário com ID %s: %s", user_id, e)
            return None

    def add_user(self, user_data: UserSchema):
        """Adiciona um novo usuário ao banco de dados."""
        try:
            new_user = self._create_user_instance(user_data)
            self._save_user(new_user)
            logger.info("Novo usuário adicionado com sucesso: ID %s", new_user.id)
            return new_user
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error("Erro ao adicionar novo usuário: %s", e)
            return None

    def update_user_status(self, user_id: int, status: str):
        """Atualiza o status de um usuário existente."""
        try:
            user = self._find_user_by_id(user_id)
            if user:
                self._set_user_status(user, status)
                self.db.commit()
                logger.info("Status do usuário %s atualizado para: %s", user_id, status)
                return user
            logger.warning(
                "Usuário não encontrado para atualizar status: ID %s", user_id
            )
            return None
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error("Erro ao atualizar status do usuário %s: %s", user_id, e)
            return None

    def _find_user_by_id(self, user_id: int):
        """Método auxiliar para encontrar usuário pelo ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    def _create_user_instance(self, user_data: UserSchema):
        """Cria uma instância de usuário a partir dos dados fornecidos."""
        return User(**user_data.dict())

    def _save_user(self, user: User):
        """Salva um usuário no banco de dados."""
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

    def _set_user_status(self, user: User, status: str):
        """Define o status de um usuário."""
        user.notes = status
        logger.debug("Status do usuário %s definido como: %s", user.id, status)
