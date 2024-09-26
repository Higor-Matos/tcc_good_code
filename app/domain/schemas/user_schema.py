# tcc_good_code/app/domain/schemas/user_schema.py

from typing import Optional

import pendulum
from pydantic import BaseModel, EmailStr, field_validator

from app.infrastructure import logger


class UserSchema(BaseModel):
    name: str
    email: EmailStr
    age: int
    address: Optional[str]
    phone: Optional[str]
    services: str
    expiration_date: pendulum.Date
    notes: Optional[str]

    class Config:
        arbitrary_types_allowed = True
        orm_mode = True

    @field_validator("age")
    def validate_age(cls, value):
        """Valida a idade mínima"""
        if value <= 0:
            logger.error("Idade inválida: %s. A idade deve ser maior que zero.", value)
            raise ValueError("A idade deve ser maior que zero.")
        logger.debug("Idade validada com sucesso: %s", value)
        return value

    @field_validator("expiration_date", mode="before")
    def validate_expiration_date(cls, value):
        """Valida e converte a data de expiração usando pendulum"""
        try:
            expiration_date = (
                pendulum.parse(value).date() if isinstance(value, str) else value
            )
            if expiration_date < pendulum.today().date():
                logger.error(
                    "Data de expiração inválida: %s. Deve ser uma data futura.",
                    expiration_date,
                )
                raise ValueError("A data de expiração deve ser uma data futura.")
            logger.debug("Data de expiração validada com sucesso: %s", expiration_date)
            return expiration_date
        except Exception as e:
            logger.error("Erro ao validar a data de expiração: %s", e)
            raise ValueError(f"Erro ao validar a data de expiração: {e}") from e
