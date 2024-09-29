# tcc_good_code/app/services/user_notification_service.py

import os

from app.infrastructure.logger import logger
from app.services.pdf_service import generate_pdf


class UserNotificationService:
    def __init__(self, send_email):
        self.send_email = send_email

    def generate_pdf_for_user(
        self, user, status, total_price, discount, tax, final_price
    ):
        """
        Gera um arquivo PDF com os dados do usuário e salva na raiz do projeto.
        """
        try:
            user_data = {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "address": user.address,
                "phone": user.phone,
                "services": user.services.split(",") if user.services else [],
                "expiration_date": user.expiration_date,
                "status": status,
                "total_price": total_price,
                "discount": discount,
                "tax": tax,
                "final_price": final_price,
            }

            pdf_filename = f"{user.id}_nota_debito.pdf"
            pdf_path = os.path.join(os.getcwd(), pdf_filename)

            generate_pdf(
                "tcc_good_code/templates/email_template.html", user_data, pdf_path
            )

            logger.info("PDF gerado e salvo na raiz do projeto: %s", pdf_filename)
            return pdf_filename
        except Exception as e:
            logger.error("Erro ao gerar PDF para o usuário %s: %s", user.email, e)
            return None

    def send_user_notification(self, user, subject, body, pdf_filename):
        """
        Envia o email com o PDF anexado.
        """
        try:
            self.send_email(user.email, subject, body, pdf_filename)
            logger.info("Email enviado para %s com anexo %s", user.email, pdf_filename)
        except Exception as e:
            logger.error("Erro ao enviar email para %s: %s", user.email, e)
