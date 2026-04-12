from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.avaliacao_pedido import AvaliacaoPedido
from app.models.pedido import Pedido
from app.schemas.avaliacao_pedido import (
    AvaliacaoPedidoCriar,
    AvaliacaoPedidoAtualizar,
    AvaliacaoPedidoResposta,
    AvaliacaoPedidoDeletadoResposta
)
from app.routers.usuarios import obter_usuario_atual, exigir_gerente

import uuid

router = APIRouter(prefix="/avaliacoes", tags=["Avaliações"])


@router.get("/", response_model=List[AvaliacaoPedidoResposta], dependencies=[Depends(exigir_gerente)])
async def listar_avaliacoes(db: Session = Depends(get_db)):
    return db.query(AvaliacaoPedido).all()


@router.get("/{id_avaliacao}", response_model=AvaliacaoPedidoResposta)
async def buscar_avaliacao(id_avaliacao: str, db: Session = Depends(get_db)):
    avaliacao = db.query(AvaliacaoPedido).filter(AvaliacaoPedido.id_avaliacao == id_avaliacao).first()

    if not avaliacao:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada.")

    return avaliacao


@router.post("/", response_model=AvaliacaoPedidoResposta, status_code=201)
async def criar_avaliacao(
    dados: AvaliacaoPedidoCriar,
    db: Session = Depends(get_db),
    usuario_atual=Depends(obter_usuario_atual)
):
    pedido = db.query(Pedido).filter(Pedido.id_pedido == dados.id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")

    avaliacao = AvaliacaoPedido(id_avaliacao=uuid.uuid4().hex, **dados.model_dump())
    db.add(avaliacao)
    db.commit()
    db.refresh(avaliacao)
    return avaliacao


@router.patch("/{id_avaliacao}", response_model=AvaliacaoPedidoResposta)
async def atualizar_avaliacao(
    id_avaliacao: str,
    dados: AvaliacaoPedidoAtualizar,
    db: Session = Depends(get_db),
    usuario_atual=Depends(obter_usuario_atual)
):
    avaliacao = db.query(AvaliacaoPedido).filter(AvaliacaoPedido.id_avaliacao == id_avaliacao).first()

    if not avaliacao:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada.")

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(avaliacao, campo, valor)

    db.commit()
    db.refresh(avaliacao)
    return avaliacao


@router.delete("/{id_avaliacao}", response_model=AvaliacaoPedidoDeletadoResposta, dependencies=[Depends(exigir_gerente)])
async def deletar_avaliacao(id_avaliacao: str, db: Session = Depends(get_db)):
    avaliacao = db.query(AvaliacaoPedido).filter(AvaliacaoPedido.id_avaliacao == id_avaliacao).first()

    if not avaliacao:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada.")

    db.delete(avaliacao)
    db.commit()

    return AvaliacaoPedidoDeletadoResposta(
        mensagem="Avaliação deletada com sucesso.",
        id_avaliacao=avaliacao.id_avaliacao,
        id_pedido=avaliacao.id_pedido
    )