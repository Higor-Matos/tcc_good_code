# tcc_good_code/app/services/user_service.py

from concurrent.futures import ThreadPoolExecutor, as_completed
import os

from app.infrastructure.logger import logger
from app.services.user_processing_service import UserProcessingService


class UserService:
    def __init__(self, user_repo, db, user_processing_service: UserProcessingService):
        self.user_repo = user_repo
        self.db = db
        self.user_processing_service = user_processing_service

    def get_all_users(self):
        """Recupera todos os usuários para processamento."""
        logger.info("Recuperando todos os usuários.")
        try:
            users = self.user_repo.get_all_users()
            logger.debug("Total de usuários recuperados: %d", len(users))
            return users
        except Exception as e:
            logger.error("Erro ao recuperar usuários: %s", e)
            return []

    def add_user(self, user_data):
        """Adiciona um novo usuário ao sistema."""
        logger.info("Adicionando novo usuário: %s", user_data.email)
        try:
            new_user = self.user_repo.add_user(user_data)
            if new_user:
                logger.info("Usuário adicionado com sucesso: %s", new_user.email)
            return new_user
        except Exception as e:
            logger.error("Erro ao adicionar usuário: %s", e)
            return None

    def process_all_users(self):
        """
        Processa todos os usuários, gerando as notas em PDF e enviando-as por e-mail.
        """
        logger.info("Iniciando o processamento de todos os usuários.")
        users = self.get_all_users()

        if not users:
            logger.warning("Nenhum usuário para processar.")
            return

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(
                    self.user_processing_service.process_user_and_generate_pdf, user
                ): user
                for user in users
            }
            for future in as_completed(futures):
                user = futures[future]
                try:
                    result, pdf_filename = future.result()
                    if result:
                        logger.info(
                            "Usuário %s processado com sucesso. PDF gerado: %s",
                            user.email,
                            pdf_filename,
                        )
                    else:
                        logger.warning(
                            "Processamento falhou para o usuário %s.", user.email
                        )
                except Exception as e:
                    logger.error("Erro ao processar usuário %s: %s", user.email, e)

        self.send_all_emails(users)

    def send_all_emails(self, users):
        """
        Envia e-mails para todos os usuários com os PDFs gerados anexados.
        """
        logger.info("Iniciando o envio de e-mails com os PDFs gerados.")
        for user in users:
            pdf_filename = f"{user.id}_nota_debito.pdf"
            if os.path.exists(pdf_filename):
                try:
                    self.user_processing_service.send_email_with_attachment(
                        user, pdf_filename
                    )
                    logger.info("Email enviado com sucesso para: %s", user.email)
                except Exception as e:
                    logger.error("Erro ao enviar email para %s: %s", user.email, e)
            else:
                logger.warning(
                    "PDF não encontrado para o usuário %s. Email não enviado.",
                    user.email,
                )
