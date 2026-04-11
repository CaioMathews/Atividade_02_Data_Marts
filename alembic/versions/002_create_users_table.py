"""Criacao da tabela de usuarios

Revision ID: 002
Revises: 001
Create Date: 2026-04-11

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "usuarios",
        sa.Column("id_usuario", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("nome_usuario", sa.String(255), nullable=False),
        sa.Column("email_usuario", sa.String(255), nullable=False, unique=True),
        sa.Column("senha_usuario", sa.String(255), nullable=False),
        sa.Column(
            "tipo_usuario",
            sa.Enum("gerente", "usuario", name="tipousuario"),
            nullable=False,
            server_default="usuario"
        ),
        sa.Column("data_cadastro", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("data_nascimento", sa.Date(), nullable=True),
    )

    op.create_index("ix_usuarios_email", "usuarios", ["email_usuario"])


def downgrade() -> None:
    op.drop_index("ix_usuarios_email", table_name="usuarios")
    op.drop_table("usuarios")