from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.vendedor import Vendedor
from app.schemas.vendedor import (
    VendedorCriar,
    VendedorAtualizar,
    VendedorResposta,
    VendedorDeletadoResposta
)
from app.routers.usuarios import exigir_gerente

import uuid

router = APIRouter(prefix="/vendedores", tags=["Vendedores"])


@router.get("/", response_model=List[VendedorResposta], dependencies=[Depends(exigir_gerente)])
async def listar_vendedores(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return db.query(Vendedor).offset(skip).limit(limit).all()


@router.get("/buscar", response_model=List[VendedorResposta], dependencies=[Depends(exigir_gerente)])
async def buscar_vendedores(
    nome: Optional[str] = Query(None),
    cidade: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Vendedor)

    if nome:
        query = query.filter(Vendedor.nome_vendedor.ilike(f"%{nome}%"))
    if cidade:
        query = query.filter(Vendedor.cidade.ilike(f"%{cidade}%"))
    if estado:
        query = query.filter(Vendedor.estado.ilike(f"%{estado}%"))

    vendedores = query.all()

    if not vendedores:
        raise HTTPException(status_code=404, detail="Nenhum vendedor encontrado.")

    return vendedores


@router.get("/{id_vendedor}", response_model=VendedorResposta, dependencies=[Depends(exigir_gerente)])
async def buscar_vendedor(id_vendedor: str, db: Session = Depends(get_db)):
    vendedor = db.query(Vendedor).filter(Vendedor.id_vendedor == id_vendedor).first()

    if not vendedor:
        raise HTTPException(status_code=404, detail="Vendedor não encontrado.")

    return vendedor


@router.post("/", response_model=VendedorResposta, status_code=201, dependencies=[Depends(exigir_gerente)])
async def criar_vendedor(dados: VendedorCriar, db: Session = Depends(get_db)):
    vendedor = Vendedor(id_vendedor=uuid.uuid4().hex, **dados.model_dump())
    db.add(vendedor)
    db.commit()
    db.refresh(vendedor)
    return vendedor


@router.patch("/{id_vendedor}", response_model=VendedorResposta, dependencies=[Depends(exigir_gerente)])
async def atualizar_vendedor(id_vendedor: str, dados: VendedorAtualizar, db: Session = Depends(get_db)):
    vendedor = db.query(Vendedor).filter(Vendedor.id_vendedor == id_vendedor).first()

    if not vendedor:
        raise HTTPException(status_code=404, detail="Vendedor não encontrado.")

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(vendedor, campo, valor)

    db.commit()
    db.refresh(vendedor)
    return vendedor


@router.delete("/{id_vendedor}", response_model=VendedorDeletadoResposta, dependencies=[Depends(exigir_gerente)])
async def deletar_vendedor(id_vendedor: str, db: Session = Depends(get_db)):
    vendedor = db.query(Vendedor).filter(Vendedor.id_vendedor == id_vendedor).first()

    if not vendedor:
        raise HTTPException(status_code=404, detail="Vendedor não encontrado.")

    db.delete(vendedor)
    db.commit()

    return VendedorDeletadoResposta(
        mensagem="Vendedor deletado com sucesso.",
        id_vendedor=vendedor.id_vendedor,
        nome_vendedor=vendedor.nome_vendedor
    )