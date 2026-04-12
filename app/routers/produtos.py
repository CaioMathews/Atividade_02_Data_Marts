from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.produto import Produto
from app.models.item_pedido import ItemPedido
from app.models.avaliacao_pedido import AvaliacaoPedido
from app.schemas.produto import (
    ProdutoCriar,
    ProdutoAtualizar,
    ProdutoResposta,
    ProdutoDeletadoResposta
)
from app.routers.usuarios import obter_usuario_atual, exigir_gerente

router = APIRouter(prefix="/produtos", tags=["Produtos"])


@router.get("/", response_model=List[ProdutoResposta])
async def listar_produtos(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return db.query(Produto).offset(skip).limit(limit).all()


@router.get("/buscar", response_model=List[ProdutoResposta])
async def buscar_produtos(
    nome: Optional[str] = Query(None),
    categoria: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Produto)

    if nome:
        query = query.filter(Produto.nome_produto.ilike(f"%{nome}%"))
    if categoria:
        query = query.filter(Produto.categoria_produto.ilike(f"%{categoria}%"))

    produtos = query.all()

    if not produtos:
        raise HTTPException(status_code=404, detail="Nenhum produto encontrado.")

    return produtos


@router.get("/{id_produto}", response_model=ProdutoResposta)
async def buscar_produto(id_produto: str, db: Session = Depends(get_db)):
    produto = db.query(Produto).filter(Produto.id_produto == id_produto).first()

    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")

    return produto


@router.get("/{id_produto}/avaliacoes")
async def avaliacoes_produto(id_produto: str, db: Session = Depends(get_db)):
    produto = db.query(Produto).filter(Produto.id_produto == id_produto).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")

    avaliacoes = (
        db.query(AvaliacaoPedido)
        .join(ItemPedido, ItemPedido.id_pedido == AvaliacaoPedido.id_pedido)
        .filter(ItemPedido.id_produto == id_produto)
        .all()
    )

    media = (
        db.query(func.avg(AvaliacaoPedido.avaliacao))
        .join(ItemPedido, ItemPedido.id_pedido == AvaliacaoPedido.id_pedido)
        .filter(ItemPedido.id_produto == id_produto)
        .scalar()
    )

    return {
        "id_produto": id_produto,
        "nome_produto": produto.nome_produto,
        "total_avaliacoes": len(avaliacoes),
        "media_avaliacao": round(media, 2) if media else None,
        "avaliacoes": [
            {
                "avaliacao": a.avaliacao,
                "titulo_comentario": a.titulo_comentario,
                "comentario": a.comentario,
                "data_comentario": a.data_comentario,
            }
            for a in avaliacoes
        ]
    }


@router.post("/", response_model=ProdutoResposta, status_code=201, dependencies=[Depends(exigir_gerente)])
async def criar_produto(dados: ProdutoCriar, db: Session = Depends(get_db)):
    import uuid
    produto = Produto(id_produto=uuid.uuid4().hex, **dados.model_dump())
    db.add(produto)
    db.commit()
    db.refresh(produto)
    return produto


@router.patch("/{id_produto}", response_model=ProdutoResposta, dependencies=[Depends(exigir_gerente)])
async def atualizar_produto(id_produto: str, dados: ProdutoAtualizar, db: Session = Depends(get_db)):
    produto = db.query(Produto).filter(Produto.id_produto == id_produto).first()

    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(produto, campo, valor)

    db.commit()
    db.refresh(produto)
    return produto


@router.delete("/{id_produto}", response_model=ProdutoDeletadoResposta, dependencies=[Depends(exigir_gerente)])
async def deletar_produto(id_produto: str, db: Session = Depends(get_db)):
    produto = db.query(Produto).filter(Produto.id_produto == id_produto).first()

    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")

    db.delete(produto)
    db.commit()

    return ProdutoDeletadoResposta(
        mensagem="Produto deletado com sucesso.",
        id_produto=produto.id_produto,
        nome_produto=produto.nome_produto
    )