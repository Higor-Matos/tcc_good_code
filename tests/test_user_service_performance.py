# tcc_good_code/tests/test_user_service_performance.py

import logging
import time
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from app.repository.user_repository import UserRepository
from app.services.user_processing_service import UserProcessingService
from app.services.user_service import UserService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture
def user_service():
    """
    Fixture para fornecer uma instância do UserService com dependências mockadas.
    """
    user_repo_mock = Mock(spec=UserRepository)
    user_processing_service_mock = Mock(spec=UserProcessingService)

    user_processing_service_mock.pdf_directory = "/path/to/pdf"

    def mock_process_user_and_generate_pdf():
        start_time = time.time()

        time.sleep(0.0002)

        time.sleep(2.3769)

        time.sleep(0.002)

        end_time = time.time()

        total_time = end_time - start_time
        logger.info(
            "Tempo total para processar e gerar PDF e enviar email para o usuário: %s segundos",
            f"{total_time:.4f}",
        )

        return True, "/path/to/pdf/1_nota_debito.pdf"

    user_processing_service_mock.process_user_and_generate_pdf.side_effect = (
        mock_process_user_and_generate_pdf
    )

    return UserService(user_repo_mock, user_processing_service_mock)


@pytest.mark.benchmark(group="user_service", min_rounds=5)
@pytest.mark.performance
def test_process_all_users_performance(benchmark, user_service):
    """
    Testa a performance da função `process_all_users` do `UserService`.
    """
    logger.info("Iniciando o teste de performance para 'process_all_users'.")

    user_service.get_all_users = Mock(
        return_value=[
            SimpleNamespace(
                id=1,
                email="teste@example.com",
                name="Teste",
                expiration_date="2024-12-31",
                services="service1,service2",
                age=30,
                address="Rua Teste, 123",
                phone="123456789",
            )
        ]
    )

    with patch("os.path.exists", return_value=True):
        result = benchmark(user_service.process_all_users)

    logger.info("Teste de performance concluído.")
    assert result is None
