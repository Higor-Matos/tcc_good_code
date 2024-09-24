# utils.py


def calculate_price(services, age):
    prices = {"A": 100, "B": 200, "C": 300, "D": 400, "E": 500}
    total_price = sum(prices.get(service, 50) for service in services)
    discount = 0.1 * total_price if age > 60 else 0
    discount += 0.05 * total_price if "Premium" in services else 0
    tax = (total_price - discount) * 0.2
    final_price = total_price - discount + tax
    return total_price, discount, tax, final_price


def get_status(days_left):
    if days_left < 0:
        return "Expirado"
    elif days_left < 5:
        return "Expirando em breve"
    else:
        return "Ativo"


def format_user_data(user, status):
    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "address": user["address"],
        "phone": user["phone"],
        "services": user["services"].split(","),
        "expiration_date": user["expiration_date"],
        "status": status,
    }


def format_prices(total_price, discount, tax, final_price):
    return {
        "total_price": total_price,
        "discount": discount,
        "tax": tax,
        "final_price": final_price,
    }


def load_template(template_path, context):
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
