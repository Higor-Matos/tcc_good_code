# tcc_good_code/app/domain/responses/api_response.py

from flask import jsonify

from app.infrastructure.logger import logger


def api_response(message, data=None, status_code=200):
    """
    Função genérica para criar respostas da API.

    :param message: Mensagem de resposta.
    :param data: Dados adicionais (opcional).
    :param status_code: Código de status HTTP da resposta.
    :return: Resposta JSON.
    """
    logger.info("Criando resposta com status %s: %s", status_code, message)
    response = {"message": message, "data": data if data is not None else {}}
    return jsonify(response), status_code


def success_response(data=None, message="Operação realizada com sucesso"):
    """
    Resposta de sucesso padrão.

    :param data: Dados adicionais (opcional).
    :param message: Mensagem de sucesso.
    :return: Resposta JSON de sucesso.
    """
    logger.info("Criando resposta de sucesso: %s", message)
    return api_response(message, data, 200)


def created_response(data=None, message="Recurso criado com sucesso"):
    """
    Resposta de recurso criado.

    :param data: Dados adicionais (opcional).
    :param message: Mensagem de criação.
    :return: Resposta JSON de recurso criado.
    """
    logger.info("Criando resposta de recurso criado: %s", message)
    return api_response(message, data, 201)


def bad_request_response(message="Requisição inválida"):
    """
    Resposta para requisição inválida.

    :param message: Mensagem de erro.
    :return: Resposta JSON de erro.
    """
    logger.warning("Criando resposta de requisição inválida: %s", message)
    return api_response(message, status_code=400)


def unauthorized_response(message="Não autorizado"):
    """
    Resposta para não autorizado.

    :param message: Mensagem de erro.
    :return: Resposta JSON de erro.
    """
    logger.warning("Criando resposta de não autorizado: %s", message)
    return api_response(message, status_code=401)


def not_found_response(message="Recurso não encontrado"):
    """
    Resposta para recurso não encontrado.

    :param message: Mensagem de erro.
    :return: Resposta JSON de erro.
    """
    logger.warning("Criando resposta de recurso não encontrado: %s", message)
    return api_response(message, status_code=404)


def internal_error_response(message="Erro interno do servidor"):
    """
    Resposta para erro interno do servidor.

    :param message: Mensagem de erro.
    :return: Resposta JSON de erro.
    """
    logger.error("Criando resposta de erro interno do servidor: %s", message)
    return api_response(message, status_code=500)
