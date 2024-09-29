# tcc_good_code/app/domain/schemas/user_schema.py

import datetime
from typing import Optional, Union

import pendulum
from pydantic import BaseModel, EmailStr, field_validator

from app.infrastructure.logger import logger


class UserSchema(BaseModel):
    name: str
    email: EmailStr
    age: int
    address: Optional[str]
    phone: Optional[str]
    services: str
    expiration_date: Union[pendulum.Date, str, None]
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
            logger.debug("Validando expiration_date: %s (tipo: %s)", value, type(value))
            if isinstance(value, pendulum.Date):
                expiration_date = value
            elif isinstance(value, str):
                expiration_date = pendulum.parse(value).date()
            elif isinstance(value, datetime.date):
                expiration_date = pendulum.date(value.year, value.month, value.day)
            else:
                raise ValueError(
                    "Tipo de dado inválido para expiration_date. Esperado pendulum.Date, datetime.date ou string."
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
