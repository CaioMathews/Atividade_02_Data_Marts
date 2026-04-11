from pydantic import BaseModel, Field

class VendedorBase(BaseModel):
    nome_vendedor: str = Field(..., min_length=2, max_length=255)
    prefixo_cep: str = Field(..., min_length=1, max_length=10)
    cidade: str = Field(..., min_length=2, max_length=100)
    estado: str = Field(..., min_length=2, max_length=2)

class VendedorCriar(VendedorBase):
    pass

class VendedorAtualizar(BaseModel):
    nome_vendedor: str | None = Field(None, min_length=2, max_length=255)
    prefixo_cep: str | None = Field(None, min_length=1, max_length=10)
    cidade: str | None = Field(None, min_length=2, max_length=100)
    estado: str | None = Field(None, min_length=2, max_length=2)

class VendedorResposta(VendedorBase):
    id_vendedor: str

    model_config = {"from_attributes": True}

class VendedorDeletadoResposta(BaseModel):
    mensagem: str
    id_vendedor: str
    nome_vendedor: str