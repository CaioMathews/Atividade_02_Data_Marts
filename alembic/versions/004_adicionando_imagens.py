"""Adiciona imagem_url na tabela de produtos

Revision ID: 004
Revises: 003
Create Date: 2026-04-13

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("produtos", sa.Column("imagem_url", sa.String(500), nullable=True))


def downgrade() -> None:
    op.drop_column("produtos", "imagem_url")