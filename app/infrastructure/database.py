# tcc_good_code/app/infrastructure/database.py

import os

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

import app.domain.entities.user as user_models
from app.infrastructure.logger import logger

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database.db")

try:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Conexão com o banco de dados inicializada com sucesso.")
except SQLAlchemyError as e:
    logger.error("Erro ao conectar com o banco de dados: %s", e)
    raise


def init_db():
    try:
        user_models.Base.metadata.create_all(bind=engine)
        logger.info("Banco de dados inicializado e tabelas criadas com sucesso.")
    except SQLAlchemyError as e:
        logger.error("Erro ao inicializar o banco de dados: %s", e)
        raise
    except Exception as e:
        logger.error("Erro inesperado ao inicializar o banco de dados: %s", e)
        raise
