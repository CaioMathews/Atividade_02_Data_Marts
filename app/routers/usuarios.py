from datetime import timezone, datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario, TipoUsuario
from app.schemas.usuario import (
    UsuarioCriar,
    UsuarioAtualizar,
    UsuarioResposta,
    UsuarioDeletadoResposta
)
from app.core.seguranca import obter_hash_senha
from app.config import settings

router = APIRouter(prefix="/usuarios", tags=["Usuários"])

seguranca = HTTPBearer()

def obter_usuario_atual(
    credenciais: HTTPAuthorizationCredentials = Depends(seguranca),
    db: Session = Depends(get_db)
) -> Usuario:
    token = credenciais.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        id_usuario: str = payload.get("sub")

        if id_usuario is None:
            raise HTTPException(status_code=401, detail="Token inválido.")

    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado.")

    usuario = db.query(Usuario).filter(Usuario.id_usuario == int(id_usuario)).first()

    if not usuario:
        raise HTTPException(status_code=401, detail="Usuário não encontrado.")

    return usuario

def exigir_gerente(usuario_atual: Usuario = Depends(obter_usuario_atual)) -> Usuario:
    if usuario_atual.tipo_usuario != TipoUsuario.gerente:
        raise HTTPException(status_code=403, detail="Acesso restrito a gerentes.")
    return usuario_atual


@router.post("/", response_model=UsuarioResposta, status_code=201)
async def criar_usuario(dados: UsuarioCriar, db: Session = Depends(get_db)):
    email_existe = db.query(Usuario).filter(Usuario.email_usuario == dados.email_usuario).first()
    if email_existe:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado.")

    novo_usuario = Usuario(
        nome_usuario=dados.nome_usuario,
        email_usuario=dados.email_usuario,
        senha_usuario=obter_hash_senha(dados.senha_usuario),
        tipo_usuario=dados.tipo_usuario,
        data_nascimento=dados.data_nascimento,
        data_cadastro=datetime.now(timezone.utc)
    )

    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    return novo_usuario


@router.get("/", response_model=List[UsuarioResposta], dependencies=[Depends(exigir_gerente)])
async def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(Usuario).all()


@router.get("/{id_usuario}", response_model=UsuarioResposta)
async def buscar_usuario(id_usuario: str, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    return usuario


@router.patch("/{id_usuario}", response_model=UsuarioResposta)
async def atualizar_usuario(
    id_usuario: str,
    dados: UsuarioAtualizar,
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(obter_usuario_atual)
):
    usuario = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    if usuario_atual.id_usuario != id_usuario and usuario_atual.tipo_usuario != TipoUsuario.gerente:
        raise HTTPException(status_code=403, detail="Sem permissão para atualizar este usuário.")

    if dados.tipo_usuario is not None and usuario_atual.tipo_usuario != TipoUsuario.gerente:
        raise HTTPException(status_code=403, detail="Apenas gerentes podem alterar o tipo de usuário.")

    campos_atualizados = dados.model_dump(exclude_unset=True)

    if "senha_usuario" in campos_atualizados:
        campos_atualizados["senha_usuario"] = obter_hash_senha(campos_atualizados["senha_usuario"])

    for campo, valor in campos_atualizados.items():
        setattr(usuario, campo, valor)

    db.commit()
    db.refresh(usuario)

    return usuario


@router.delete("/{id_usuario}", response_model=UsuarioDeletadoResposta, dependencies=[Depends(exigir_gerente)])
async def deletar_usuario(id_usuario: str, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    db.delete(usuario)
    db.commit()

    return UsuarioDeletadoResposta(
        mensagem="Usuário deletado com sucesso.",
        id_usuario=usuario.id_usuario,
        nome_usuario=usuario.nome_usuario
    )