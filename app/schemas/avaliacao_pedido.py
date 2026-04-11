from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class AvaliacaoPedidoBase(BaseModel):
    id_pedido: str = Field(..., min_length=32, max_length=32)
    avaliacao: int = Field(..., ge=1, le=5)
    titulo_comentario: Optional[str] = Field(None, max_length=255)
    comentario: Optional[str] = Field(None, max_length=1000)
    data_comentario: Optional[datetime] = None
    data_resposta: Optional[datetime] = None


class AvaliacaoPedidoCriar(AvaliacaoPedidoBase):
    pass


class AvaliacaoPedidoAtualizar(BaseModel):
    avaliacao: Optional[int] = Field(None, ge=1, le=5)
    titulo_comentario: Optional[str] = Field(None, max_length=255)
    comentario: Optional[str] = Field(None, max_length=1000)
    data_comentario: Optional[datetime] = None
    data_resposta: Optional[datetime] = None


class AvaliacaoPedidoResposta(AvaliacaoPedidoBase):
    id_avaliacao: str

    model_config = {"from_attributes": True}


class AvaliacaoPedidoDeletadoResposta(BaseModel):
    mensagem: str
    id_avaliacao: str
    id_pedido: str