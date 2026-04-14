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

@router.get("/categorias", response_model=dict)
async def listar_categorias(db: Session = Depends(get_db)):

    AGRUPAMENTO = {
        'Tecnologia & Eletrônicos': ['consoles_games', 'informatica_acessorios', 'audio', 'telefonia', 'telefonia_fixa', 'eletronicos', 'pcs', 'tablets_impressao_imagem', 'pc_gamer', 'cine_foto'],
        'Casa, Móveis & Construção': ['cama_mesa_banho', 'moveis_decoracao', 'utilidades_domesticas', 'casa_conforto', 'casa_conforto_2', 'moveis_escritorio', 'moveis_sala', 'moveis_quarto', 'moveis_colchao_e_estofado', 'moveis_cozinha_area_de_servico_jantar_e_jardim', 'climatizacao', 'eletrodomesticos', 'eletrodomesticos_2', 'eletroportateis', 'portateis_casa_forno_e_cafe', 'portateis_cozinha_e_preparadores_de_alimentos', 'casa_construcao', 'construcao_ferramentas_construcao', 'construcao_ferramentas_ferramentas', 'construcao_ferramentas_iluminacao', 'construcao_ferramentas_jardim', 'construcao_ferramentas_seguranca'],
        'Moda & Beleza': ['beleza_saude', 'fashion_calcados', 'perfumaria', 'relogios_presentes', 'fashion_bolsas_e_acessorios', 'fashion_roupas_masculinas', 'fashion_roupas_femininas', 'fashion_underwear_e_moda_praia', 'fashion_esporte', 'fashion_roupa_feminina', 'fashion_roupa_infanto_juvenil', 'fashion_roupa_masculina', 'malas_acessorios'],
        'Esporte & Entretenimento': ['esporte_lazer', 'brinquedos', 'cool_stuff', 'instrumentos_musicais', 'artigos_de_festas', 'artigos_de_natal', 'cds_dvds_musicais', 'dvds_blu_ray', 'musica', 'livros_interesse_geral', 'livros_importados', 'livros_tecnicos', 'artes', 'artes_e_artesanato'],
        'Bebês & Pets': ['bebes', 'fraldas_higiene', 'pet_shop'],
        'Supermercado & Diversos': ['alimentos', 'alimentos_bebidas', 'bebidas', 'agro_industria_e_comercio', 'industria_comercio_e_negocios', 'ferramentas_jardim', 'papelaria', 'flores', 'la_cuisine', 'market_place', 'seguros_e_servicos', 'sinalizacao_e_seguranca', 'automotivo', 'nao_informado']
    }

    resultado = db.query(Produto.categoria_produto).distinct().all()
    categorias_banco = sorted([linha[0] for linha in resultado if linha[0]])
    
    categorias_agrupadas = {}
    
    for cat in categorias_banco:
        encontrou = False
        for grupo, itens in AGRUPAMENTO.items():
            if cat in itens:
                if grupo not in categorias_agrupadas:
                    categorias_agrupadas[grupo] = []
                categorias_agrupadas[grupo].append(cat)
                encontrou = True
                break
                
        if not encontrou:
            if "Outros" not in categorias_agrupadas:
                categorias_agrupadas["Outros"] = []
            categorias_agrupadas["Outros"].append(cat)
            
    return categorias_agrupadas

@router.get("/", response_model=dict)
async def listar_produtos(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    busca: Optional[str] = Query(None),
    categoria: Optional[str] = Query(None),
    avaliacao_minima: Optional[float] = Query(None, ge=0, le=5),
    ordenar: Optional[str] = Query(None),  
    db: Session = Depends(get_db)
):
    query = db.query(Produto)

    if busca:
        query = query.filter(Produto.nome_produto.ilike(f"%{busca}%"))
    if categoria:
        query = query.filter(Produto.categoria_produto == categoria)

    if avaliacao_minima is not None and avaliacao_minima > 0:
        subq = (
            db.query(
                ItemPedido.id_produto,
                func.avg(AvaliacaoPedido.avaliacao).label("media"),
            )
            .join(AvaliacaoPedido, AvaliacaoPedido.id_pedido == ItemPedido.id_pedido)
            .group_by(ItemPedido.id_produto)
            .subquery()
        )
        query = (
            query
            .join(subq, subq.c.id_produto == Produto.id_produto)
            .filter(subq.c.media >= avaliacao_minima)
        )

    total = query.with_entities(func.count(func.distinct(Produto.id_produto))).scalar()

    if ordenar == "nome_asc":
        query = query.order_by(Produto.nome_produto.asc())
    elif ordenar == "nome_desc":
        query = query.order_by(Produto.nome_produto.desc())

    produtos = query.offset(skip).limit(limit).all()

    return {
        "total": total,
        "produtos": [ProdutoResposta.model_validate(p) for p in produtos],
    }


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

    total_vendas = db.query(ItemPedido).filter(ItemPedido.id_produto == id_produto).count()

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
        "total_vendas": total_vendas, 
        "avaliacoes": [
            {
                "avaliacao": a.avaliacao,
                "titulo_comentario": a.titulo_comentario,
                "comentario": a.comentario,
                "data_comentario": a.data_comentario,
            }
            for a in avaliacoes
        ],
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
        nome_produto=produto.nome_produto,
    )