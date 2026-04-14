import pandas as pd
from sqlalchemy import text
from app.database import engine

def seed_imagens():
    df = pd.read_csv("csv/dim_categoria_imagens.csv")

    with engine.connect() as conn:
        for _, row in df.iterrows():
            conn.execute(
                text("""
                    UPDATE produtos
                    SET imagem_url = :url
                    WHERE categoria_produto = :categoria
                """),
                {"url": row["Link"], "categoria": row["Categoria"]}
            )
        conn.commit()
        print(f"✅ {len(df)} categorias com imagens atualizadas!")

if __name__ == "__main__":
    seed_imagens()