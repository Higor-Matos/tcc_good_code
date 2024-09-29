# tcc_good_code/app/services/user_processing_service.py

from datetime import date, datetime

from app.domain import utils
from app.infrastructure.logger import logger


class UserProcessingService:
    def __init__(self, user_repo, notification_service):
        self.user_repo = user_repo
        self.notification_service = notification_service

    def process_user_and_generate_pdf(self, user):
        """
        Processa o usuário, gera o PDF da nota de débito e salva na raiz do projeto.
        """
        logger.info("Processando usuário: %s", user.email)
        try:

            if not isinstance(user.expiration_date, date):
                if isinstance(user.expiration_date, str):
                    user.expiration_date = datetime.strptime(
                        user.expiration_date, "%Y-%m-%d"
                    ).date()
                else:
                    raise ValueError(
                        "Data de expiração deve ser do tipo datetime.date ou string."
                    )

            total_price, discount, tax, final_price = utils.calculate_price(
                user.services.split(","), user.age
            )
            days_left = (user.expiration_date - date.today()).days
            status = utils.get_status(days_left)

            self.user_repo.update_user_status(user.id, status)

            pdf_filename = self.notification_service.generate_pdf_for_user(
                user, status, total_price, discount, tax, final_price
            )

            return True, pdf_filename
        except ValueError as e:
            logger.error("Erro de valor ao processar usuário %s: %s", user.email, e)
            return False, None
        except Exception as e:
            logger.error("Erro inesperado ao processar usuário %s: %s", user.email, e)
            return False, None

    def send_email_with_attachment(self, user, pdf_filename):
        """Envia um email com o PDF gerado anexado."""
        try:
            email_subject = f"Sua Nota de Débito - {user.notes}"
            email_body = (
                "Segue em anexo sua nota de débito."
                if user.notes == "Expirado"
                else "Lembrete de Expiração"
            )
            self.notification_service.send_user_notification(
                user, email_subject, email_body, pdf_filename
            )
        except Exception as e:
            logger.error("Erro ao enviar e-mail para usuário %s: %s", user.email, e)
