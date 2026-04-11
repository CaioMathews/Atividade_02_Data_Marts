from pydantic import BaseModel, Field


class ConsumidorBase(BaseModel):
    nome_consumidor: str = Field(..., min_length=2, max_length=255)
    prefixo_cep: str = Field(..., min_length=1, max_length=10)
    cidade: str = Field(..., min_length=2, max_length=100)
    estado: str = Field(..., min_length=2, max_length=2)


class ConsumidorCriar(ConsumidorBase):
    pass


class ConsumidorAtualizar(BaseModel):
    nome_consumidor: str | None = Field(None, min_length=2, max_length=255)
    prefixo_cep: str | None = Field(None, min_length=1, max_length=10)
    cidade: str | None = Field(None, min_length=2, max_length=100)
    estado: str | None = Field(None, min_length=2, max_length=2)


class ConsumidorResposta(ConsumidorBase):
    id_consumidor: str

    model_config = {"from_attributes": True}


class ConsumidorDeletadoResposta(BaseModel):
    mensagem: str
    id_consumidor: str
    nome_consumidor: str