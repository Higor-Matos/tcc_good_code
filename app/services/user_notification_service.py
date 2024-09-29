# tcc_good_code/app/services/user_notification_service.py

import os

from app.infrastructure.logger import logger
from app.services.pdf_service import generate_pdf


class UserNotificationService:
    def __init__(self, send_email, generate_pdf):
        self.send_email = send_email
        self.generate_pdf = generate_pdf
        self.template_dir = self._get_template_directory()

    def generate_pdf_for_user(
        self, user, status, total_price, discount, tax, final_price
    ):
        """
        Gera um arquivo PDF com os dados do usuário e salva na raiz do projeto.
        """
        user_data = self._build_user_data(
            user, status, total_price, discount, tax, final_price
        )
        pdf_filename = f"{user.id}_nota_debito.pdf"
        pdf_path = os.path.join(os.getcwd(), pdf_filename)
        template_path = os.path.join(self.template_dir, "email_template.html")

        if not os.path.exists(template_path):
            logger.error("Template não encontrado: %s", template_path)
            return None

        if self._generate_pdf(template_path, user_data, pdf_path):
            return pdf_filename
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

    def _build_user_data(self, user, status, total_price, discount, tax, final_price):
        """
        Constrói o dicionário com os dados do usuário para gerar o PDF.
        """
        return {
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

    def _generate_pdf(self, template_path, user_data, pdf_path):
        """
        Gera o PDF com base no template fornecido e dados do usuário.
        """
        try:
            generate_pdf(template_path, user_data, pdf_path)
            logger.info("PDF gerado e salvo na raiz do projeto: %s", pdf_path)
            return True
        except Exception as e:
            logger.error("Erro ao gerar PDF: %s", e)
            return False

    def _get_template_directory(self):
        """
        Retorna o diretório onde os templates estão armazenados.
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, "templates")
