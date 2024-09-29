# tcc_good_code/app/infrastructure/database.py

import os

from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

import app.domain.entities.user as user_models
from app.infrastructure.logger import logger

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/database.db")

try:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Conexão com o banco de dados inicializada com sucesso.")
except SQLAlchemyError as e:
    logger.error("Erro ao conectar com o banco de dados: %s", e)
    raise


def init_db():
    try:
        inspector = inspect(engine)
        if "users" not in inspector.get_table_names():
            user_models.Base.metadata.create_all(bind=engine)
            logger.info("Banco de dados inicializado e tabelas criadas com sucesso.")
        else:
            logger.info(
                "Tabela 'users' já existe. Nenhuma alteração foi feita no banco de dados."
            )
    except SQLAlchemyError as e:
        logger.error("Erro ao inicializar o banco de dados: %s", e)
        raise
    except Exception as e:
        logger.error("Erro inesperado ao inicializar o banco de dados: %s", e)
        raise
