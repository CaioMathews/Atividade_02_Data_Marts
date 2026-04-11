# schemas/pedido.py
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field


class PedidoBase(BaseModel):
    id_consumidor: str = Field(..., min_length=32, max_length=32)
    status: str = Field(..., min_length=2, max_length=50)
    pedido_compra_timestamp: Optional[datetime] = None
    pedido_entregue_timestamp: Optional[datetime] = None
    data_estimada_entrega: Optional[date] = None
    tempo_entrega_dias: Optional[float] = Field(None, gt=0)
    tempo_entrega_estimado_dias: Optional[float] = Field(None, gt=0)
    diferenca_entrega_dias: Optional[float] = None
    entrega_no_prazo: Optional[str] = Field(None, max_length=10)


class PedidoCriar(PedidoBase):
    pass


class PedidoAtualizar(BaseModel):
    id_consumidor: Optional[str] = Field(None, min_length=32, max_length=32)
    status: Optional[str] = Field(None, min_length=2, max_length=50)
    pedido_compra_timestamp: Optional[datetime] = None
    pedido_entregue_timestamp: Optional[datetime] = None
    data_estimada_entrega: Optional[date] = None
    tempo_entrega_dias: Optional[float] = Field(None, gt=0)
    tempo_entrega_estimado_dias: Optional[float] = Field(None, gt=0)
    diferenca_entrega_dias: Optional[float] = None
    entrega_no_prazo: Optional[str] = Field(None, max_length=10)


class PedidoResposta(PedidoBase):
    id_pedido: str

    model_config = {"from_attributes": True}


class PedidoDeletadoResposta(BaseModel):
    mensagem: str
    id_pedido: str
    status: str