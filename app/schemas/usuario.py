# schemas/usuario.py
from datetime import datetime, date
from typing import Optional
import re

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.usuario import TipoUsuario


class UsuarioBase(BaseModel):
    nome_usuario: str = Field(..., min_length=3, max_length=255)
    email_usuario: EmailStr
    data_nascimento: Optional[date] = None
    tipo_usuario: TipoUsuario = TipoUsuario.usuario


class UsuarioCriar(UsuarioBase):
    senha_usuario: str = Field(..., min_length=8, max_length=255)

    @field_validator("senha_usuario")
    @classmethod
    def validar_senha(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("A senha deve conter ao menos uma letra maiúscula.")
        if not re.search(r"[0-9]", v):
            raise ValueError("A senha deve conter ao menos um número.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("A senha deve conter ao menos um caractere especial.")
        return v


class UsuarioAtualizar(BaseModel):
    nome_usuario: Optional[str] = Field(None, min_length=3, max_length=255)
    email_usuario: Optional[EmailStr] = None
    data_nascimento: Optional[date] = None
    tipo_usuario: Optional[TipoUsuario] = None
    senha_usuario: Optional[str] = Field(None, min_length=8, max_length=255)

    @field_validator("senha_usuario")
    @classmethod
    def validar_senha(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not re.search(r"[A-Z]", v):
            raise ValueError("A senha deve conter ao menos uma letra maiúscula.")
        if not re.search(r"[0-9]", v):
            raise ValueError("A senha deve conter ao menos um número.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("A senha deve conter ao menos um caractere especial.")
        return v


class UsuarioResposta(UsuarioBase):
    id_usuario: int
    data_cadastro: datetime

    model_config = {"from_attributes": True}


class UsuarioRespostaCompleta(UsuarioResposta):
    senha_usuario: str

    model_config = {"from_attributes": True}


class UsuarioDeletadoResposta(BaseModel):
    mensagem: str
    id_usuario: int
    nome_usuario: str