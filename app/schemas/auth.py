from pydantic import BaseModel, EmailStr


class LoginEntrada(BaseModel):
    email_usuario: EmailStr
    senha_usuario: str


class TokenResposta(BaseModel):
    access_token: str
    