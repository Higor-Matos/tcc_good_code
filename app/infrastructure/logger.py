# tcc_good_code/app/infrastructure/logger.py

import logging
from logging.handlers import RotatingFileHandler
import os


def setup_logger():
    try:
        log_level = os.getenv("LOGGING_LEVEL", "DEBUG")
        log_file = os.getenv("LOGGING_LOG_FILE", "logs/app.log")

        log_level = getattr(logging, log_level.upper(), logging.DEBUG)

        log_dir = os.path.dirname(log_file)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            print(f"Diretório de logs criado: {log_dir}")

        file_handler = RotatingFileHandler(
            log_file, maxBytes=5 * 1024 * 1024, backupCount=3
        )
        file_handler.setLevel(log_level)

        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] [%(name)s] - %(message)s", "%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)

        logging.basicConfig(level=log_level, handlers=[file_handler, console_handler])
        logger = logging.getLogger(__name__)

        logger.info(
            "Logger configurado com sucesso. Logs serão armazenados em %s", log_file
        )

    except PermissionError as e:
        print(f"Erro de permissão ao configurar o logger: {e}")
        logger = logging.getLogger(__name__)
        logger.addHandler(logging.StreamHandler())
        logger.error("Erro de permissão ao configurar o logger: %s", e)
    except FileNotFoundError as e:
        print(f"Erro ao encontrar o caminho para o arquivo de log: {e}")
        logger = logging.getLogger(__name__)
        logger.addHandler(logging.StreamHandler())
        logger.error("Erro ao encontrar o caminho para o arquivo de log: %s", e)
    except Exception as e:
        print(f"Erro inesperado ao configurar o logger: {e}")
        logger = logging.getLogger(__name__)
        logger.addHandler(logging.StreamHandler())
        logger.error("Erro inesperado ao configurar o logger: %s", e)

    return logger


logger = setup_logger()
