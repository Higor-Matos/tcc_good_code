# tcc_good_code/app/repository/user_repository.py

from injector import inject
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from app.domain.entities.user import User
from app.domain.schemas.user_schema import UserSchema
from app.infrastructure.logger import logger


class UserRepository:
    @inject
    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory

    def create_session(self):
        return self.session_factory()

    def get_all_users(self):
        """Recupera todos os usuários do banco de dados."""
        session = self.create_session()
        try:
            users = session.query(User).all()
            logger.info("Obtidos todos os usuários com sucesso. Total: %d", len(users))
            return users
        except SQLAlchemyError as e:
            logger.error("Erro ao obter todos os usuários: %s", e)
            return []
        finally:
            session.close()

    def get_user_by_id(self, session: Session, user_id: int):
        """Recupera um usuário pelo ID."""
        try:
            user = session.query(User).filter(User.id == user_id).first()
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
        session = self.create_session()
        try:
            new_user = self._create_user_instance(user_data)
            self._save_user(session, new_user)
            logger.info("Novo usuário adicionado com sucesso: ID %s", new_user.id)
            return new_user
        except SQLAlchemyError as e:
            session.rollback()
            logger.error("Erro ao adicionar novo usuário: %s", e)
            return None
        finally:
            session.close()

    def update_user_status(self, session: Session, user_id: int, status: str):
        """Atualiza o status de um usuário existente."""
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                self._set_user_status(user, status)
                session.commit()
                logger.info("Status do usuário %s atualizado para: %s", user_id, status)
                return user
            logger.warning(
                "Usuário não encontrado para atualizar status: ID %s", user_id
            )
            return None
        except SQLAlchemyError as e:
            session.rollback()
            logger.error("Erro ao atualizar status do usuário %s: %s", user_id, e)
            return None

    def _create_user_instance(self, user_data: UserSchema):
        """Cria uma instância de usuário a partir dos dados fornecidos."""
        return User(**user_data.dict())

    def _save_user(self, session: Session, user: User):
        """Salva um usuário no banco de dados."""
        session.add(user)
        session.commit()
        session.refresh(user)

    def _set_user_status(self, user: User, status: str):
        """Define o status de um usuário."""
        user.notes = status
        logger.debug("Status do usuário %s definido como: %s", user.id, status)
