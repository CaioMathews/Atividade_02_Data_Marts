from pydantic import BaseModel, Field

class ProdutoBase(BaseModel):
    nome_produto: str = Field(..., min_length=2, max_length=255)
    categoria_produto: str = Field(..., min_length=2, max_length=100)
    peso_produto_gramas: float | None = Field(None, gt=0)
    comprimento_centimetros: float | None = Field(None, gt=0)
    altura_centimetros: float | None = Field(None, gt=0)
    largura_centimetros: float | None = Field(None, gt=0)

class ProdutoCriar(ProdutoBase):
    pass

class ProdutoAtualizar(BaseModel):
    nome_produto: str | None = Field(None, min_length=2, max_length=255)
    categoria_produto: str | None = Field(None, min_length=2, max_length=100)
    peso_produto_gramas: float | None = Field(None, gt=0)
    comprimento_centimetros: float | None = Field(None, gt=0)
    altura_centimetros: float | None = Field(None, gt=0)
    largura_centimetros: float | None = Field(None, gt=0)

class ProdutoResposta(ProdutoBase):
    id_produto: str

    model_config = {"from_attributes": True}

class ProdutoDeletadoResposta(BaseModel):
    mensagem: str
    id_produto: str
    nome_produto: str
        