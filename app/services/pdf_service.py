# tcc_good_code/app/services/pdf_service.py

import os
import time

import pdfkit

from app.domain.utils import load_template
from app.infrastructure.logger import logger


def log_time(operation, elapsed_time):
    with open("process_times_good_code.txt", "a", encoding="utf-8") as f:
        f.write(f"Tempo para {operation}: {elapsed_time:.4f} segundos\n")


def generate_pdf(template_path, context, pdf_filename):
    """
    Gera um arquivo PDF a partir de um template HTML e contexto fornecidos.
    """
    html_file = None
    try:
        html_content = generate_html_content(template_path, context)
        html_file = create_html_file(
            html_content, pdf_filename.replace(".pdf", ".html")
        )

        start_time = time.time()
        render_html_to_pdf(html_file, pdf_filename)
        elapsed_time = time.time() - start_time
        log_time("gerar HTML e PDF", elapsed_time)

        logger.info("PDF gerado com sucesso: %s", pdf_filename)
        return pdf_filename
    except Exception as e:
        logger.error("Erro ao gerar PDF %s: %s", pdf_filename, e)
        return None
    finally:
        cleanup_temp_files(html_file)


def generate_html_content(template_path, context):
    """
    Gera o conteúdo HTML a partir de um template e contexto fornecidos.
    """
    try:
        html_content = load_template(template_path, context)
        logger.info("Template HTML carregado com sucesso.")
        return html_content
    except Exception as e:
        logger.error("Erro ao carregar template HTML: %s", e)
        raise


def create_html_file(html_content, html_filename):
    """
    Cria um arquivo HTML temporário para geração do PDF.
    """
    try:
        with open(html_filename, "w", encoding="utf-8") as file:
            file.write(html_content)
        logger.info("Arquivo HTML criado com sucesso: %s", html_filename)
        return html_filename
    except Exception as e:
        logger.error("Erro ao criar arquivo HTML temporário: %s", e)
        raise


def render_html_to_pdf(html_file, pdf_filename):
    """
    Renderiza o arquivo HTML em um arquivo PDF.
    """
    try:
        options = {"quiet": "", "enable-local-file-access": "", "encoding": "UTF-8"}

        start_time = time.time()
        pdfkit.from_file(html_file, pdf_filename, options=options)
        elapsed_time = time.time() - start_time
        log_time("gerar PDF", elapsed_time)

        logger.info("PDF gerado a partir do arquivo HTML: %s", pdf_filename)
    except Exception as e:
        logger.error("Erro ao renderizar o PDF: %s", e)
        raise


def cleanup_temp_files(*files):
    """
    Remove arquivos temporários criados durante o processo de geração do PDF.
    """
    try:
        for file in files:
            if file and os.path.exists(file):
                os.remove(file)
                logger.info("Arquivo temporário removido: %s", file)
    except Exception as e:
        logger.warning("Erro ao remover arquivos temporários: %s", e)
