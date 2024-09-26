# tcc_good_code/app/services/email_service.py

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import smtplib

from app.infrastructure.logger import logger

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")


def send_email(to_address, subject, body, attachment=None):
    """
    Envia um e-mail utilizando o servidor SMTP.
    """
    try:
        msg = create_email_message(to_address, subject, body, attachment)
        send_email_via_smtp(msg)
        logger.info("Email enviado com sucesso para %s", to_address)
    except Exception as e:
        logger.error("Erro ao enviar email para %s: %s", to_address, e)


def create_email_message(to_address, subject, body, attachment=None):
    """
    Cria a mensagem de e-mail com ou sem anexo.
    """
    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_USER
        msg["To"] = to_address
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        if attachment:
            attach_file(msg, attachment)

        logger.debug(
            "Mensagem de e-mail criada para %s com assunto %s", to_address, subject
        )
        return msg
    except Exception as e:
        logger.error("Erro ao criar mensagem de e-mail: %s", e)
        raise


def attach_file(msg, attachment):
    """
    Anexa um arquivo à mensagem de e-mail.
    """
    try:
        with open(attachment, "rb") as file:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(file.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition", f'attachment; filename="{attachment}"'
            )
            msg.attach(part)
        logger.debug("Arquivo anexado ao e-mail: %s", attachment)
    except FileNotFoundError:
        logger.error("Arquivo de anexo não encontrado: %s", attachment)
        raise
    except Exception as e:
        logger.error("Erro ao anexar arquivo: %s", e)
        raise


def send_email_via_smtp(msg):
    """
    Envia a mensagem de e-mail usando o servidor SMTP configurado.
    """
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(msg["From"], msg["To"], msg.as_string())
            logger.debug("Conexão com SMTP encerrada corretamente.")
    except smtplib.SMTPAuthenticationError:
        logger.error("Erro de autenticação SMTP ao enviar o e-mail.")
        raise
    except smtplib.SMTPException as e:
        logger.error("Erro SMTP ao enviar o e-mail: %s", e)
        raise
    except Exception as e:
        logger.error("Erro inesperado ao enviar o e-mail: %s", e)
        raise
