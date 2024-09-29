# tcc_good_code/app/services/user_service.py

from concurrent.futures import ThreadPoolExecutor, as_completed
import os

from app.infrastructure.logger import logger
from app.services.user_processing_service import UserProcessingService


class UserService:
    def __init__(self, user_repo, user_processing_service: UserProcessingService):
        self.user_repo = user_repo
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

    def process_all_users(self):
        """
        Processa todos os usuários, gerando as notas em PDF e enviando-as por e-mail.
        """
        logger.info("Iniciando o processamento de todos os usuários.")
        users = self.get_all_users()

        if not users:
            logger.warning("Nenhum usuário para processar.")
            return

        user_data_list = []
        for user in users:
            user_data = {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "expiration_date": user.expiration_date,
                "services": user.services,
                "age": user.age,
                "address": user.address,
                "phone": user.phone,
            }
            user_data_list.append(user_data)

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(
                    self.user_processing_service.process_user_and_generate_pdf,
                    user_data,
                ): user_data
                for user_data in user_data_list
            }
            for future in as_completed(futures):
                user_data = futures[future]
                try:
                    result, pdf_filename = future.result()
                    if result:
                        logger.info(
                            "Usuário %s processado com sucesso. PDF gerado: %s",
                            user_data["email"],
                            pdf_filename,
                        )
                    else:
                        logger.warning(
                            "Processamento falhou para o usuário %s.",
                            user_data["email"],
                        )
                except Exception as e:
                    logger.error(
                        "Erro ao processar usuário %s: %s", user_data["email"], e
                    )

        self.send_all_emails(user_data_list)

    def send_all_emails(self, user_data_list):
        """
        Envia e-mails para todos os usuários com os PDFs gerados anexados.
        """
        logger.info("Iniciando o envio de e-mails com os PDFs gerados.")
        for user_data in user_data_list:
            pdf_filename = os.path.join(
                self.user_processing_service.pdf_directory,
                f"{user_data['id']}_nota_debito.pdf",
            )
            if os.path.exists(pdf_filename):
                try:
                    self.user_processing_service.send_email_with_attachment(
                        user_data, pdf_filename
                    )
                    logger.info(
                        "Email enviado com sucesso para: %s", user_data["email"]
                    )
                except Exception as e:
                    logger.error(
                        "Erro ao enviar email para %s: %s", user_data["email"], e
                    )
            else:
                logger.warning(
                    "PDF não encontrado para o usuário %s. Email não enviado.",
                    user_data["email"],
                )

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
