# tcc_good_code/app/services/user_service.py

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime

from injector import inject
from sqlalchemy.orm import Session

from app.domain import utils
from app.domain.schemas.user_schema import UserSchema
from app.infrastructure.database import SessionLocal
from app.infrastructure.logger import logger
from app.repository.user_repository import UserRepository


class UserService:
    @inject
    def __init__(
        self, user_repo: UserRepository, db: Session, send_email, generate_pdf
    ):
        self.user_repo = user_repo
        self.db = db
        self.send_email = send_email
        self.generate_pdf = generate_pdf

    def get_all_users(self):
        logger.info("Recuperando todos os usuários.")
        try:
            users = self.user_repo.get_all_users()
            logger.debug("Total de usuários recuperados: %d", len(users))
            return users
        except Exception as e:
            logger.error("Erro ao recuperar usuários: %s", e)
            return []

    def add_user(self, user_data: UserSchema):
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
        logger.info("Processando todos os usuários.")
        users = self.get_all_users()

        if not users:
            logger.warning("Nenhum usuário para processar.")
            return

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(self.process_user_safe, user): user for user in users
            }
            for future in as_completed(futures):
                user = futures[future]
                try:
                    result = future.result()
                    if result:
                        logger.info("Usuário %s processado com sucesso.", user.email)
                    else:
                        logger.warning(
                            "Processamento falhou para o usuário %s.", user.email
                        )
                except Exception as e:
                    logger.error("Erro ao processar usuário %s: %s", user.email, e)

    def process_user_safe(self, user):
        """
        Wrapper seguro para processar usuários, garantindo sessão independente por thread.
        """
        session = SessionLocal()
        try:
            user_repo = UserRepository(session)
            self.process_user(user_repo, user)
            session.commit()
            return True
        except Exception as e:
            logger.error("Erro ao processar usuário %s: %s", user.email, e)
            session.rollback()
            return False
        finally:
            session.close()

    def process_user(self, user_repo, user):
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

            total_price, discount, tax, final_price = self.calculate_user_prices(user)
            days_left = (user.expiration_date - date.today()).days
            status = utils.get_status(days_left)

            self.update_user_status(user_repo, user, status)

            if status in ["Expirado", "Expirando em breve"]:
                self.send_user_notification(
                    user, status, total_price, discount, tax, final_price
                )
        except ValueError as e:
            logger.error("Erro de valor ao processar usuário %s: %s", user.email, e)
        except Exception as e:
            logger.error("Erro inesperado ao processar usuário %s: %s", user.email, e)

    def calculate_user_prices(self, user):
        """Calcula o preço total com desconto e imposto baseado nos serviços do usuário."""
        if isinstance(user.services, str):
            user_services = user.services.split(",")
        elif isinstance(user.services, list):
            user_services = user.services
        else:
            user_services = []
        total_price, discount, tax, final_price = utils.calculate_price(
            user_services, user.age
        )
        logger.debug(
            "Preços calculados para usuário %s: Total: %s, Desconto: %s, Taxa: %s, Final: %s",
            user.email,
            total_price,
            discount,
            tax,
            final_price,
        )
        return total_price, discount, tax, final_price

    def update_user_status(self, user_repo, user, status):
        """Atualiza o status do usuário no banco de dados."""
        try:
            if user_repo.update_user_status(user.id, status):
                logger.info(
                    "Status do usuário %s atualizado para: %s", user.email, status
                )
            else:
                logger.warning("Falha ao atualizar status para usuário %s", user.email)
        except Exception as e:
            logger.error("Erro ao atualizar status do usuário %s: %s", user.email, e)

    def send_user_notification(
        self, user, status, total_price, discount, tax, final_price
    ):
        """Envia notificação ao usuário com o PDF gerado, dependendo do status."""
        try:
            user_data = utils.format_user_data(user, status)
            formatted_prices = utils.format_prices(
                total_price, discount, tax, final_price
            )
            user_data.update(formatted_prices)

            pdf_file = self.generate_pdf(
                "template_path.html", user_data, f"{user.id}_nota_debito.pdf"
            )

            email_subject = f"Sua Nota de Débito - {status}"
            email_body = (
                "Segue em anexo sua nota de débito."
                if status == "Expirado"
                else "Lembrete de Expiração"
            )

            self.send_email(user.email, email_subject, email_body, pdf_file)
            logger.info("Nota de débito enviada para: %s", user.email)
        except Exception as e:
            logger.error(
                "Erro ao enviar notificação para usuário %s: %s", user.email, e
            )
