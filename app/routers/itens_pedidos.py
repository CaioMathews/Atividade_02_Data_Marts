from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.item_pedido import ItemPedido
from app.models.pedido import Pedido
from app.models.produto import Produto
from app.schemas.item_pedido import (
    ItemPedidoCriar,
    ItemPedidoAtualizar,
    ItemPedidoResposta,
    ItemPedidoDeletadoResposta
)
from app.routers.usuarios import exigir_gerente

router = APIRouter(prefix="/itens-pedidos", tags=["Itens de Pedidos"])


@router.get("/", response_model=List[ItemPedidoResposta], dependencies=[Depends(exigir_gerente)])
async def listar_itens(db: Session = Depends(get_db)):
    return db.query(ItemPedido).all()


@router.get("/pedido/{id_pedido}", response_model=List[ItemPedidoResposta])
async def listar_itens_por_pedido(id_pedido: str, db: Session = Depends(get_db)):
    pedido = db.query(Pedido).filter(Pedido.id_pedido == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")

    itens = db.query(ItemPedido).filter(ItemPedido.id_pedido == id_pedido).all()
    if not itens:
        raise HTTPException(status_code=404, detail="Nenhum item encontrado para este pedido.")

    return itens


@router.get("/{id_pedido}/{id_item}", response_model=ItemPedidoResposta)
async def buscar_item(id_pedido: str, id_item: int, db: Session = Depends(get_db)):
    item = db.query(ItemPedido).filter(
        ItemPedido.id_pedido == id_pedido,
        ItemPedido.id_item == id_item
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado.")

    return item


@router.post("/", response_model=ItemPedidoResposta, status_code=201, dependencies=[Depends(exigir_gerente)])
async def criar_item(dados: ItemPedidoCriar, db: Session = Depends(get_db)):
    pedido = db.query(Pedido).filter(Pedido.id_pedido == dados.id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")

    produto = db.query(Produto).filter(Produto.id_produto == dados.id_produto).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")

    ultimo_item = (
        db.query(ItemPedido)
        .filter(ItemPedido.id_pedido == dados.id_pedido)
        .order_by(ItemPedido.id_item.desc())
        .first()
    )
    proximo_id_item = (ultimo_item.id_item + 1) if ultimo_item else 1

    item = ItemPedido(id_item=proximo_id_item, **dados.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/{id_pedido}/{id_item}", response_model=ItemPedidoResposta, dependencies=[Depends(exigir_gerente)])
async def atualizar_item(
    id_pedido: str,
    id_item: int,
    dados: ItemPedidoAtualizar,
    db: Session = Depends(get_db)
):
    item = db.query(ItemPedido).filter(
        ItemPedido.id_pedido == id_pedido,
        ItemPedido.id_item == id_item
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado.")

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(item, campo, valor)

    db.commit()
    db.refresh(item)
    return item


@router.delete("/{id_pedido}/{id_item}", response_model=ItemPedidoDeletadoResposta, dependencies=[Depends(exigir_gerente)])
async def deletar_item(id_pedido: str, id_item: int, db: Session = Depends(get_db)):
    item = db.query(ItemPedido).filter(
        ItemPedido.id_pedido == id_pedido,
        ItemPedido.id_item == id_item
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado.")

    db.delete(item)
    db.commit()

    return ItemPedidoDeletadoResposta(
        mensagem="Item deletado com sucesso.",
        id_pedido=item.id_pedido,
        id_item=item.id_item
    )