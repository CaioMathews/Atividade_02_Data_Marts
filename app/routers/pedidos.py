from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.pedido import Pedido
from app.models.consumidor import Consumidor
from app.schemas.pedido import (
    PedidoCriar,
    PedidoAtualizar,
    PedidoResposta,
    PedidoDeletadoResposta
)
from app.routers.usuarios import obter_usuario_atual, exigir_gerente

import uuid

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


@router.get("/", response_model=List[PedidoResposta], dependencies=[Depends(exigir_gerente)])
async def listar_pedidos(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return db.query(Pedido).offset(skip).limit(limit).all()


@router.get("/buscar", response_model=List[PedidoResposta])
async def buscar_pedidos(
    status: Optional[str] = Query(None),
    entrega_no_prazo: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Pedido)

    if status:
        query = query.filter(Pedido.status.ilike(f"%{status}%"))
    if entrega_no_prazo:
        query = query.filter(Pedido.entrega_no_prazo == entrega_no_prazo)

    pedidos = query.all()

    if not pedidos:
        raise HTTPException(status_code=404, detail="Nenhum pedido encontrado.")

    return pedidos


@router.get("/consumidor/{id_consumidor}", response_model=List[PedidoResposta])
async def listar_pedidos_consumidor(id_consumidor: str, db: Session = Depends(get_db)):
    consumidor = db.query(Consumidor).filter(Consumidor.id_consumidor == id_consumidor).first()
    if not consumidor:
        raise HTTPException(status_code=404, detail="Consumidor não encontrado.")

    pedidos = db.query(Pedido).filter(Pedido.id_consumidor == id_consumidor).all()
    if not pedidos:
        raise HTTPException(status_code=404, detail="Nenhum pedido encontrado para este consumidor.")

    return pedidos


@router.get("/{id_pedido}", response_model=PedidoResposta)
async def buscar_pedido(id_pedido: str, db: Session = Depends(get_db)):
    pedido = db.query(Pedido).filter(Pedido.id_pedido == id_pedido).first()

    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")

    return pedido


@router.post("/", response_model=PedidoResposta, status_code=201, dependencies=[Depends(exigir_gerente)])
async def criar_pedido(dados: PedidoCriar, db: Session = Depends(get_db)):
    consumidor = db.query(Consumidor).filter(Consumidor.id_consumidor == dados.id_consumidor).first()
    if not consumidor:
        raise HTTPException(status_code=404, detail="Consumidor não encontrado.")

    pedido = Pedido(id_pedido=uuid.uuid4().hex, **dados.model_dump())
    db.add(pedido)
    db.commit()
    db.refresh(pedido)
    return pedido


@router.patch("/{id_pedido}", response_model=PedidoResposta, dependencies=[Depends(exigir_gerente)])
async def atualizar_pedido(id_pedido: str, dados: PedidoAtualizar, db: Session = Depends(get_db)):
    pedido = db.query(Pedido).filter(Pedido.id_pedido == id_pedido).first()

    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(pedido, campo, valor)

    db.commit()
    db.refresh(pedido)
    return pedido


@router.delete("/{id_pedido}", response_model=PedidoDeletadoResposta, dependencies=[Depends(exigir_gerente)])
async def deletar_pedido(id_pedido: str, db: Session = Depends(get_db)):
    pedido = db.query(Pedido).filter(Pedido.id_pedido == id_pedido).first()

    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")

    db.delete(pedido)
    db.commit()

    return PedidoDeletadoResposta(
        mensagem="Pedido deletado com sucesso.",
        id_pedido=pedido.id_pedido,
        status=pedido.status
    )