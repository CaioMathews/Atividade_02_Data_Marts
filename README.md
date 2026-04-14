# Backend — Sistema de Compras Online

API REST construída com **FastAPI** e **SQLite**, utilizando SQLAlchemy como ORM e Alembic para migrations.

---

## Requisitos

- Python 3.11+

---

## Instalação

**1. Crie e ative um ambiente virtual**

```bash
python -m venv venv
```

Windows:
```bash
venv\Scripts\activate
```


**2. Instale as dependências**

```bash
pip install -r requirements.txt
```

**3. Configure as variáveis de ambiente**

Copie o arquivo de exemplo e ajuste se necessário:
Crie um arquivo .env na raiz do backend baseado no arquivo .env.example.
⚠️ IMPORTANTE: Você deve obrigatoriamente definir uma SECRET_KEY= dentro do seu arquivo .env
---

## Banco de dados

### Criar as tabelas

```bash
alembic upgrade head
```

Este comando lê os arquivos dentro de `alembic/versions/` e cria todas as tabelas no banco.

### Ver o estado atual

```bash
alembic current
```

---
### Adicionar csv

Criar a pasta csv (Atividade_02_Data_Marts\csv) e colocar todos os csv nela

### População do Banco de Dados (Seed)

Execute os scripts para carregar os dados iniciais dos arquivos CSV 
```bash
python -m app.scripts.seed
python -m app.scripts.seed_imagens
```

## Rodando a API

```bash
uvicorn app.main:app --reload
```

A API estará disponível em: [http://localhost:8000](http://localhost:8000)


---
## 💻 Configuração do Frontend
Para rodar a interface do usuário, utilize o terminal na pasta raiz do frontend:

### 1. Instalação das Dependências
Utilize o pnpm para instalar os pacotes necessários:

```bash
pnpm install
```

### 2. Execução do Projeto
Inicie o servidor de desenvolvimento do Vite:

```bash
pnpm dev
```

OBS: o front está no repositorio 
https://github.com/CaioMathews/Atividade_02_Data_Marts_front.git

## Estrutura do projeto

```
backend/
├── app/
│   ├── main.py              # Ponto de entrada da aplicação
│   ├── database.py          # Configuração do banco de dados
│   ├── config.py            # Variáveis de ambiente
│   ├── models/              # Models do SQLAlchemy 
│   │   ├── consumidor.py
│   │   ├── produto.py
│   │   ├── vendedor.py
│   │   ├── pedido.py
│   │   ├── item_pedido.py
│   │   └── avaliacao_pedido.py
│   ├── schemas/             # Schemas do Pydantic
│   │   ├── consumidor.py
│   │   ├── produto.py
│   │   ├── vendedor.py
│   │   ├── pedido.py
│   │   ├── item_pedido.py
│   │   └── avaliacao_pedido.py
│   ├── routers/             # Rotas da API
│   │   ├── consumidores.py
│   │   ├── produtos.py
│   │   ├── vendedores.py
│   │   ├── pedidos.py
│   │   ├── itens_pedidos.py
│   │   └── avaliacoes_pedidos.py
│   └── scripts/             # Scripts de população (seed)
├── alembic/
│   ├── env.py               # Configuração do Alembic
│   └── versions/            # Arquivos de migration
├── csv/                     # Arquivos .csv para o seed
├── alembic.ini              # Configuração principal do Alembic
├── requirements.txt
└── .env.example
```
