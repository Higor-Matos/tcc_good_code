# email_service.py

"""
Módulo responsável por enviar e-mails utilizando o servidor SMTP do Outlook.
"""

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

SMTP_SERVER = "smtp.office365.com"
SMTP_PORT = 587
SMTP_USER = "bot_assinaturas@outlook.com"
SMTP_PASSWORD = "senha_secreta"


def send_email(to_address, subject, body, attachment=None):
    """
    Envia um e-mail utilizando o servidor SMTP do Outlook.

    Args:
        to_address (str): Endereço de e-mail do destinatário.
        subject (str): Assunto do e-mail.
        body (str): Corpo do e-mail em texto plano.
        attachment (str, optional): Caminho para o arquivo a ser anexado.
                                    Default é None.

    Raises:
        smtplib.SMTPException: Para erros específicos de SMTP.
    """
    try:
        # Conecta ao servidor SMTP
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.ehlo()
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)

        # Cria a mensagem do e-mail
        msg = MIMEMultipart()
        msg["From"] = SMTP_USER
        msg["To"] = to_address
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Anexa arquivo, se fornecido
        if attachment:
            with open(attachment, "rb") as file:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(file.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition", f'attachment; filename="{attachment}"'
                )
                msg.attach(part)

        # Envia o e-mail
        server.sendmail(SMTP_USER, to_address, msg.as_string())
    except smtplib.SMTPException as e:
        print(f"Failed to send email: {e}")
    finally:
        server.quit()
