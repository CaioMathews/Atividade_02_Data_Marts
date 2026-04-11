from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt
from typing import Optional
from app.config import settings 

contexto_senha = CryptContext(schemes=["bcrypt"], deprecated="auto")


def criar_token_acesso(dados: dict, tempo_expiracao: Optional[timedelta] = None):
    dados_para_codificar = dados.copy()
    
    if tempo_expiracao:
        expiracao = datetime.now(timezone.utc) + tempo_expiracao
    else:   
        expiracao = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    dados_para_codificar.update({"exp": expiracao})
    
    token_jwt = jwt.encode(
        dados_para_codificar, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    
    return token_jwt

def obter_hash_senha(senha: str) -> str:
    return contexto_senha.hash(senha)

def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
    return contexto_senha.verify(senha_plana, senha_hash)

