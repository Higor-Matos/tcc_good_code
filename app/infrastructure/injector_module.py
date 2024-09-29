# tcc_good_code/app/infrastructure/injector_module.py

import logging

from injector import Binder, Module, provider, singleton
from sqlalchemy.orm import sessionmaker

from app.infrastructure.database import SessionLocal, init_db
from app.infrastructure.load_envs import load_envs
from app.infrastructure.logger import setup_logger
from app.repository.user_repository import UserRepository
from app.services.email_service import send_email
from app.services.pdf_service import generate_pdf
from app.services.user_notification_service import UserNotificationService
from app.services.user_processing_service import UserProcessingService
from app.services.user_service import UserService


class InjectorModule(Module):
    def configure(self, binder: Binder):
        binder.bind(sessionmaker, to=SessionLocal, scope=singleton)
        binder.bind(UserRepository, to=self.provide_user_repository, scope=singleton)
        binder.bind(callable, to=self.provide_send_email, scope=singleton)
        binder.bind(callable, to=self.provide_generate_pdf, scope=singleton)
        binder.bind(
            UserNotificationService,
            to=self.provide_user_notification_service,
            scope=singleton,
        )
        binder.bind(
            UserProcessingService,
            to=self.provide_user_processing_service,
            scope=singleton,
        )
        binder.bind(UserService, to=self.provide_user_service, scope=singleton)
        binder.bind(logging.Logger, to=setup_logger(), scope=singleton)

    @provider
    @singleton
    def provide_user_repository(self, session_factory: sessionmaker) -> UserRepository:
        return UserRepository(session_factory)

    @provider
    @singleton
    def provide_user_service(
        self,
        user_repo: UserRepository,
        user_processing_service: UserProcessingService,
    ) -> UserService:
        return UserService(user_repo, user_processing_service)

    @provider
    @singleton
    def provide_user_processing_service(
        self, user_repo: UserRepository, notification_service: UserNotificationService
    ) -> UserProcessingService:
        return UserProcessingService(user_repo, notification_service)

    @provider
    @singleton
    def provide_user_notification_service(
        self, send_email: callable, generate_pdf: callable
    ) -> UserNotificationService:
        return UserNotificationService(send_email, generate_pdf)

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
    def provide_send_email(self) -> callable:
        return send_email

    @provider
    @singleton
    def provide_generate_pdf(self) -> callable:
        return generate_pdf
