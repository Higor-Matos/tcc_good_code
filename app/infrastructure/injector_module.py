# tcc_good_code/app/infrastructure/injector_module.py

import logging

from injector import Binder, Module, provider, singleton
from sqlalchemy.orm import Session, scoped_session, sessionmaker

from app.infrastructure.database import SessionLocal, init_db
from app.infrastructure.load_envs import load_envs
from app.infrastructure.logger import setup_logger
from app.repository.user_repository import UserRepository
from app.services.email_service import send_email
from app.services.pdf_service import generate_pdf
from app.services.user_service import UserService


class InjectorModule(Module):
    def configure(self, binder: Binder):
        binder.bind(sessionmaker, to=SessionLocal, scope=singleton)

        binder.bind(Session, to=self.provide_db_session, scope=singleton)

        binder.bind(UserRepository, to=UserRepository, scope=singleton)
        binder.bind(UserService, to=UserService, scope=singleton)
        binder.bind(logging.Logger, to=setup_logger(), scope=singleton)
        binder.bind("send_email", to=send_email, scope=singleton)
        binder.bind("generate_pdf", to=generate_pdf, scope=singleton)

    @provider
    @singleton
    def provide_user_service(
        self, user_repo: UserRepository, db: Session
    ) -> UserService:
        return UserService(user_repo, db, send_email, generate_pdf)

    @provider
    @singleton
    def provide_logger(self) -> logging.Logger:
        return setup_logger()

    @provider
    @singleton
    def provide_environment_loader(self) -> callable:
        return load_envs

    @provider
    @singleton
    def provide_database_initializer(self) -> callable:
        return init_db

    @provider
    @singleton
    def provide_db_session(self, session_factory: sessionmaker) -> Session:
        return scoped_session(session_factory)()
