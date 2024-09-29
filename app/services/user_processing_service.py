# tcc_good_code/app/services/user_processing_service.py

from datetime import date, datetime
import os
import time

from app.domain import utils
from app.infrastructure.logger import logger
from app.repository.user_repository import UserRepository


def log_time(operation, elapsed_time):
    with open("process_times_good_code.txt", "a", encoding="utf-8") as f:
        f.write(f"Tempo para {operation}: {elapsed_time:.4f} segundos\n")


class UserProcessingService:
    def __init__(self, user_repository: UserRepository, notification_service):
        """Inicializa o serviço com repositório de usuários e serviço de notificação."""
        self.user_repository = user_repository
        self.notification_service = notification_service

        self.pdf_directory = os.path.join(os.getcwd(), "pdfs")
        self._create_pdf_directory()

    def _create_pdf_directory(self):
        """Cria o diretório para armazenar PDFs, se não existir."""
        if not os.path.exists(self.pdf_directory):
            os.makedirs(self.pdf_directory)
            logger.info(
                "Diretório '%s' criado para armazenar os PDFs.", self.pdf_directory
            )

    def process_user_and_generate_pdf(self, user_data):
        """Processa o usuário e gera um PDF da nota de débito."""
        logger.info("Iniciando processamento do usuário: %s", user_data["email"])
        session = self.user_repository.create_session()
        try:
            start_time = time.time()
            user = self.user_repository.get_user_by_id(session, user_data["id"])

            self._validate_and_update_user(session, user)
            pdf_filename = self._generate_user_pdf(user)

            total_time = time.time() - start_time
            log_time("processar e gerar PDF para usuário", total_time)

            return True, pdf_filename
        except ValueError as e:
            logger.error(
                "Erro de valor ao processar usuário %s: %s", user_data["email"], e
            )
            return False, None
        except Exception as e:
            logger.error(
                "Erro inesperado ao processar usuário %s: %s", user_data["email"], e
            )
            return False, None
        finally:
            session.close()

    def _validate_and_update_user(self, session, user):
        """Valida e atualiza o usuário no banco de dados."""
        user.expiration_date = self._parse_expiration_date(user.expiration_date)
        total_price, discount, tax, final_price = self._calculate_user_price(user)

        start_time = time.time()
        status = self._determine_user_status(user.expiration_date)
        elapsed_time = time.time() - start_time
        log_time("calcular o preço e status", elapsed_time)

        self._update_user_status_in_database(session, user.id, status)
        user.total_price = total_price
        user.discount = discount
        user.tax = tax
        user.final_price = final_price
        user.status = status

    def _parse_expiration_date(self, expiration_date):
        """Converte a data de expiração para datetime.date."""
        if isinstance(expiration_date, date):
            return expiration_date
        if isinstance(expiration_date, str):
            try:
                return datetime.strptime(expiration_date, "%Y-%m-%d").date()
            except ValueError as e:
                raise ValueError(
                    "Data de expiração deve estar no formato 'YYYY-MM-DD'."
                ) from e
        raise ValueError("Data de expiração deve ser datetime.date ou string.")

    def _calculate_user_price(self, user):
        """Calcula o preço dos serviços do usuário."""
        services = user.services.split(",") if user.services else []
        return utils.calculate_price(services, user.age)

    def _determine_user_status(self, expiration_date):
        """Define o status do usuário com base na data de expiração."""
        days_left = (expiration_date - date.today()).days
        return utils.get_status(days_left)

    def _update_user_status_in_database(self, session, user_id, status):
        """Atualiza o status do usuário no banco de dados."""
        try:
            self.user_repository.update_user_status(session, user_id, status)
        except Exception as e:
            logger.error("Erro ao atualizar status do usuário %s: %s", user_id, e)
            raise

    def _generate_user_pdf(self, user):
        """Gera o PDF com os dados do usuário."""
        context = self._prepare_pdf_context(user)
        template_path = os.path.join(os.getcwd(), "templates", "nota_debito.html")
        pdf_filename = os.path.join(self.pdf_directory, f"{user.id}_nota_debito.pdf")

        start_time = time.time()
        pdf_generated = self.notification_service.generate_pdf(
            template_path, context, pdf_filename
        )
        elapsed_time = time.time() - start_time
        log_time("gerar PDF para o usuário", elapsed_time)

        if pdf_generated:
            logger.info("PDF gerado e salvo com sucesso: %s", pdf_filename)
        else:
            logger.warning("Falha ao gerar PDF para o usuário: %s", user.email)
        return pdf_filename

    def _prepare_pdf_context(self, user):
        """Prepara o contexto de dados para geração do PDF."""
        return {
            "user": {
                "name": user.name,
                "email": user.email,
                "address": user.address,
                "phone": user.phone,
                "services": user.services,
                "expiration_date": user.expiration_date.strftime("%d/%m/%Y"),
                "status": user.status,
            },
            "prices": {
                "total_price": user.total_price,
                "discount": user.discount,
                "tax": user.tax,
                "final_price": user.final_price,
            },
        }

    def _prepare_email_content(self, user_data):
        """Prepara o assunto e o corpo do email."""
        email_subject = f"Sua Nota de Débito - {user_data.get('notes', '')}"
        email_body = (
            "Segue em anexo sua nota de débito."
            if user_data.get("notes") == "Expirado"
            else "Lembrete de Expiração"
        )
        return email_subject, email_body
