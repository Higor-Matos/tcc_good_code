# tcc_good_code/app/infrastructure/load_envs.py

import logging
import os

import yaml

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def load_envs(yaml_file_path=None):
    """
    Carrega variáveis de ambiente de um arquivo YAML.

    :param yaml_file_path: Caminho para o arquivo YAML que contém as variáveis de ambiente.
                           Se não for fornecido, usará o caminho padrão na raiz do projeto.
    """
    if yaml_file_path is None:
        yaml_file_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../tcc_good_code/envs.yaml")
        )

    if not os.path.exists(yaml_file_path):
        logger.error("Arquivo de configuração %s não encontrado.", yaml_file_path)
        raise FileNotFoundError(
            f"Arquivo de configuração {yaml_file_path} não encontrado."
        )

    logger.info("Carregando variáveis de ambiente do arquivo: %s", yaml_file_path)

    try:
        with open(yaml_file_path, "r", encoding="utf-8") as yaml_file:
            config = yaml.safe_load(yaml_file)
    except yaml.YAMLError as e:
        logger.error("Erro ao ler o arquivo YAML: %s", e)
        raise ValueError(f"Erro ao ler o arquivo YAML: {e}") from e
    except Exception as e:
        logger.error("Erro inesperado ao abrir o arquivo: %s", e)
        raise e

    for category, settings in config.items():
        for key, value in settings.items():
            env_var_name = f"{category.upper()}_{key.upper()}"
            os.environ[env_var_name] = str(value)
            logger.debug("Variável de ambiente definida: %s=%s", env_var_name, value)

    logger.info("Todas as variáveis de ambiente foram carregadas com sucesso.")


try:
    load_envs()
except Exception as e:
    logger.error("Erro ao carregar variáveis de ambiente: %s", e)
