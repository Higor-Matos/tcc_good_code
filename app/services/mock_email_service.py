# tcc_good_code/app/services/mock_email_service.py

from app.infrastructure.logger import logger


def send_email(to_address, subject, body, attachment=None):
    """
    Mock de envio de e-mail. Apenas loga a tentativa de envio.
    """
    logger.info(
        "Mock - Email enviado com sucesso para %s com assunto '%s'. Anexo: %s",
        to_address,
        subject,
        attachment,
    )

    return True
