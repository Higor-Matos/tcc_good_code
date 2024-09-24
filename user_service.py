from datetime import datetime

from database import get_db  # Importando o método de conexão com o banco de dados
from email_service import send_email  # Importando o serviço de envio de e-mail
from pdf_service import generate_pdf  # Importando o serviço de geração de PDF
from utils import (  # Importando utilitários
    calculate_price,
    format_prices,
    format_user_data,
    get_status,
)


def get_all_users():
    """
    Retorna todos os usuários do banco de dados, formatando cada um deles.
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    return [format_user(user) for user in users]


def format_user(user):
    """
    Formata o registro do usuário em um dicionário legível.

    Args:
        user (tuple): Tupla contendo dados do usuário no banco de dados.

    Returns:
        dict: Dicionário formatado com os dados do usuário.
    """
    return {
        "id": user[0],
        "name": user[1],
        "email": user[2],
        "age": user[3],
        "address": user[4],
        "phone": user[5],
        "services": user[6],
        "expiration_date": user[7],
        "notes": user[8],
    }


def add_new_user(user_data):
    """
    Adiciona um novo usuário ao banco de dados.

    Args:
        user_data (dict): Dicionário contendo os dados do usuário.

    Returns:
        bool: True se o usuário foi adicionado com sucesso, False caso contrário.
    """
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (name, email, age, address, phone, services, expiration_date, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                user_data["name"],
                user_data["email"],
                user_data["age"],
                user_data["address"],
                user_data["phone"],
                user_data["services"],
                user_data["expiration_date"],
                user_data.get("notes", ""),
            ),
        )
        db.commit()
        return True
    except Exception as e:
        print(f"Error adding user: {e}")
        return False


def process_all_users():
    """
    Processa todos os usuários cadastrados.
    """
    users = get_all_users()
    for user in users:
        process_user(user)


def process_user(user):
    """
    Processa as informações de um usuário específico.

    Args:
        user (dict): Dicionário contendo dados do usuário.
    """
    user_services = user["services"].split(",")
    total_price, discount, tax, final_price = calculate_price(
        user_services, user["age"]
    )

    expiration_date = datetime.strptime(user["expiration_date"], "%Y-%m-%d")
    today = datetime.now()
    days_left = (expiration_date - today).days

    status = get_status(days_left)
    update_user_status(user["id"], status)

    if status in ["Expirado", "Expirando em breve"]:
        user_data = format_user_data(user, status)
        prices = format_prices(total_price, discount, tax, final_price)
        pdf_file = generate_user_pdf(user_data, prices)
        email_body = (
            "Segue em anexo sua nota de débito."
            if status == "Expirado"
            else "Lembrete de Expiração"
        )
        send_email(
            user["email"], f"Sua Nota de Débito - {status}", email_body, pdf_file
        )


def update_user_status(user_id, status):
    """
    Atualiza o status de um usuário no banco de dados.

    Args:
        user_id (int): ID do usuário a ser atualizado.
        status (str): Novo status do usuário.
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE users SET notes=? WHERE id=?", (status, user_id))
    db.commit()


def generate_user_pdf(user_data, prices):
    """
    Gera um PDF com as informações do usuário.

    Args:
        user_data (dict): Dados formatados do usuário.
        prices (dict): Preços e cálculos relacionados aos serviços do usuário.

    Returns:
        str: Caminho do arquivo PDF gerado.
    """
    template_path = "templates/nota_debito.html"
    context = {"user": user_data, "prices": prices}
    pdf_filename = f'nota_debito_{user_data["id"]}.pdf'
    return generate_pdf(template_path, context, pdf_filename)
