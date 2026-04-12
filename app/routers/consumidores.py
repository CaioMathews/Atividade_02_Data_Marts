from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.consumidor import Consumidor
from app.schemas.consumidor import (
    ConsumidorCriar,
    ConsumidorAtualizar,
    ConsumidorResposta,
    ConsumidorDeletadoResposta
)
from app.routers.usuarios import exigir_gerente

import uuid

router = APIRouter(prefix="/consumidores", tags=["Consumidores"])


@router.get("/", response_model=List[ConsumidorResposta], dependencies=[Depends(exigir_gerente)])
async def listar_consumidores(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return db.query(Consumidor).offset(skip).limit(limit).all()


@router.get("/buscar", response_model=List[ConsumidorResposta], dependencies=[Depends(exigir_gerente)])
async def buscar_consumidores(
    nome: Optional[str] = Query(None),
    cidade: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Consumidor)

    if nome:
        query = query.filter(Consumidor.nome_consumidor.ilike(f"%{nome}%"))
    if cidade:
        query = query.filter(Consumidor.cidade.ilike(f"%{cidade}%"))
    if estado:
        query = query.filter(Consumidor.estado.ilike(f"%{estado}%"))

    consumidores = query.all()

    if not consumidores:
        raise HTTPException(status_code=404, detail="Nenhum consumidor encontrado.")

    return consumidores


@router.get("/{id_consumidor}", response_model=ConsumidorResposta, dependencies=[Depends(exigir_gerente)])
async def buscar_consumidor(id_consumidor: str, db: Session = Depends(get_db)):
    consumidor = db.query(Consumidor).filter(Consumidor.id_consumidor == id_consumidor).first()

    if not consumidor:
        raise HTTPException(status_code=404, detail="Consumidor não encontrado.")

    return consumidor


@router.post("/", response_model=ConsumidorResposta, status_code=201, dependencies=[Depends(exigir_gerente)])
async def criar_consumidor(dados: ConsumidorCriar, db: Session = Depends(get_db)):
    consumidor = Consumidor(id_consumidor=uuid.uuid4().hex, **dados.model_dump())
    db.add(consumidor)
    db.commit()
    db.refresh(consumidor)
    return consumidor


@router.patch("/{id_consumidor}", response_model=ConsumidorResposta, dependencies=[Depends(exigir_gerente)])
async def atualizar_consumidor(id_consumidor: str, dados: ConsumidorAtualizar, db: Session = Depends(get_db)):
    consumidor = db.query(Consumidor).filter(Consumidor.id_consumidor == id_consumidor).first()

    if not consumidor:
        raise HTTPException(status_code=404, detail="Consumidor não encontrado.")

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(consumidor, campo, valor)

    db.commit()
    db.refresh(consumidor)
    return consumidor


@router.delete("/{id_consumidor}", response_model=ConsumidorDeletadoResposta, dependencies=[Depends(exigir_gerente)])
async def deletar_consumidor(id_consumidor: str, db: Session = Depends(get_db)):
    consumidor = db.query(Consumidor).filter(Consumidor.id_consumidor == id_consumidor).first()

    if not consumidor:
        raise HTTPException(status_code=404, detail="Consumidor não encontrado.")

    db.delete(consumidor)
    db.commit()

    return ConsumidorDeletadoResposta(
        mensagem="Consumidor deletado com sucesso.",
        id_consumidor=consumidor.id_consumidor,
        nome_consumidor=consumidor.nome_consumidor
    )