from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.auth import LoginEntrada, TokenResposta
from app.core.seguranca import verificar_senha, criar_token_acesso
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Autenticação"])

oauth2_esquema = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.post("/login", response_model=TokenResposta)
async def login(dados: LoginEntrada, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email_usuario == dados.email_usuario).first()

    if not usuario or not verificar_senha(dados.senha_usuario, usuario.senha_usuario):
        raise HTTPException(status_code=401, detail="E-mail ou senha inválidos.")

    token = criar_token_acesso({"sub": str(usuario.id_usuario)})

    return TokenResposta(access_token=token)