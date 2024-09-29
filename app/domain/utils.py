# tcc_good_code/app/domain/utils.py

import logging

from app.domain.schemas.user_schema import UserSchema

logger = logging.getLogger(__name__)


def calculate_price(services, age):
    logger.debug("Calculando preço para serviços: %s e idade: %s", services, age)
    if not isinstance(age, int):
        logger.error("Idade fornecida não é um número inteiro: %s", age)
        raise ValueError("Idade deve ser um número inteiro.")

    prices = {"A": 100, "B": 200, "C": 300, "D": 400, "E": 500}
    total_price = sum(prices.get(service.strip(), 50) for service in services)
    discount = 0.1 * total_price if age > 60 else 0
    discount += 0.05 * total_price if "Premium" in services else 0
    tax = (total_price - discount) * 0.2
    final_price = total_price - discount + tax

    logger.debug(
        "Preço calculado: Total: %s, Desconto: %s, Taxa: %s, Final: %s",
        total_price,
        discount,
        tax,
        final_price,
    )
    return total_price, discount, tax, final_price


def get_status(days_left):
    logger.debug("Verificando status com dias restantes: %s", days_left)
    if not isinstance(days_left, int):
        logger.error("Dias restantes deve ser um número inteiro: %s", days_left)
        raise ValueError("Dias restantes deve ser um número inteiro.")

    if days_left < 0:
        return "Expirado"
    if days_left < 5:
        return "Expirando em breve"
    return "Ativo"


def format_user_data(user, status):
    logger.debug("Formatando dados do usuário: %s", user.email)
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "address": user.address,
        "phone": user.phone,
        "services": user.services.split(",") if user.services else [],
        "expiration_date": user.expiration_date,
        "status": status,
    }


def format_prices(total_price, discount, tax, final_price):
    logger.debug(
        "Formatando preços: Total: %s, Desconto: %s, Taxa: %s, Final: %s",
        total_price,
        discount,
        tax,
        final_price,
    )
    return {
        "total_price": total_price,
        "discount": discount,
        "tax": tax,
        "final_price": final_price,
    }


def load_template(template_path, context):
    logger.debug("Carregando template de %s com contexto: %s", template_path, context)
    try:
        with open(template_path, "r", encoding="utf-8") as file:
            template = file.read()
        for key, value in context.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    template = template.replace(
                        f"{{{{ {key}.{sub_key} }}}}", str(sub_value)
                    )
            else:
                template = template.replace(f"{{{{ {key} }}}}", str(value))
        return template
    except FileNotFoundError:
        logger.error("Template não encontrado: %s", template_path)
        raise
    except Exception as e:
        logger.error("Erro ao carregar template: %s", e)
        raise


def validate_user(user):
    """
    Função auxiliar para validar um único usuário.
    Retorna um dicionário válido ou None em caso de erro.
    """
    try:
        user_schema = UserSchema.model_validate(user, from_attributes=True)
        return user_schema.model_dump()
    except Exception as e:
        logger.error("Erro ao validar usuário %s: %s", user.id, e)
        return None
