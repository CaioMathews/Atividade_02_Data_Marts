import pandas as pd
from sqlalchemy import text
from app.database import engine

def seed():
    tabelas = [
        ("csv/dim_consumidores.csv",       "consumidores",       None),
        ("csv/dim_vendedores.csv",         "vendedores",         None),
        ("csv/dim_produtos.csv",           "produtos",           ["id_produto", "nome_produto", "categoria_produto", "peso_produto_gramas", "comprimento_centimetros", "altura_centimetros", "largura_centimetros"]),
        ("csv/fat_pedidos.csv",            "pedidos",            None),
        ("csv/fat_itens_pedidos.csv",      "itens_pedidos",      None),
        ("csv/fat_avaliacoes_pedidos.csv", "avaliacoes_pedidos", ["id_avaliacao", "id_pedido", "nota_avaliacao", "titulo_avaliacao", "comentario_avaliacao", "data_criacao_avaliacao", "data_resposta_avaliacao"]),
    ]

    for arquivo, tabela, colunas in tabelas:
        with engine.connect() as conn:
            resultado = conn.execute(text(f"SELECT COUNT(*) FROM {tabela}"))
            total = resultado.scalar()

        if total > 0:
            print(f"⚠ '{tabela}' já possui {total} registros, pulando...")
            continue

        df = pd.read_csv(arquivo)
        if colunas:
            df = df[colunas]  

        renomear = {
            "nota_avaliacao": "avaliacao",
            "titulo_avaliacao": "titulo_comentario",
            "comentario_avaliacao": "comentario",
            "data_criacao_avaliacao": "data_comentario",
            "data_resposta_avaliacao": "data_resposta",
        }
        df = df.rename(columns=renomear)
        
        df.to_sql(tabela, engine, if_exists="append", index=False)
        print(f"✓ {len(df)} registros carregados em '{tabela}'")

    print("✅ Seed concluído!")

if __name__ == "__main__":
    seed()