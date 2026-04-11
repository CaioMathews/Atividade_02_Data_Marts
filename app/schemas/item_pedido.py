from pydantic import BaseModel, Field


class ItemPedidoBase(BaseModel):
    id_pedido: str = Field(..., min_length=32, max_length=32)
    id_produto: str = Field(..., min_length=32, max_length=32)
    id_vendedor: str = Field(..., min_length=32, max_length=32)
    preco_BRL: float = Field(..., gt=0)
    preco_frete: float = Field(..., ge=0)


class ItemPedidoCriar(ItemPedidoBase):
    pass


class ItemPedidoAtualizar(BaseModel):
    id_produto: str | None = Field(None, min_length=32, max_length=32)
    id_vendedor: str | None = Field(None, min_length=32, max_length=32)
    preco_BRL: float | None = Field(None, gt=0)
    preco_frete: float | None = Field(None, ge=0)


class ItemPedidoResposta(ItemPedidoBase):
    id_item: int

    model_config = {"from_attributes": True}


class ItemPedidoDeletadoResposta(BaseModel):
    mensagem: str
    id_pedido: str
    id_item: int