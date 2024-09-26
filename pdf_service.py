# tcc_good_code/pdf_service.py

import time

import pdfkit
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from app.domain.utils import load_template


def generate_pdf(template_path, context, pdf_filename):
    """
    Gera um arquivo PDF a partir de um template HTML e contexto fornecidos.

    Args:
        template_path (str): Caminho para o arquivo de template HTML.
        context (dict): Contexto de dados para preencher o template.
        pdf_filename (str): Nome do arquivo PDF de saída.

    Returns:
        str: Caminho do arquivo PDF gerado.
    """
    html_content = load_template(template_path, context)
    html_file = pdf_filename.replace(".pdf", ".html")

    with open(html_file, "w", encoding="utf-8") as file:
        file.write(html_content)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(f"file:///{html_file}")
    time.sleep(5)  # Esperar a página carregar completamente
    driver.quit()

    pdfkit.from_file(html_file, pdf_filename)
    return pdf_filename
