"""Criar conta de gerente padrao

Revision ID: 003
Revises: 002
Create Date: 2026-04-11

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        INSERT INTO usuarios (nome_usuario, email_usuario, senha_usuario, tipo_usuario, data_cadastro)
        VALUES (
            'Admin',
            'admin@email.com',
            '$2b$12$nPHrTzrsW4ZCoG17OqIfHuvYeuDvcLUZi1e4tjqKQCLp5I15LMphi', 
            'gerente',
            CURRENT_TIMESTAMP
        )
    """)
#senha: admin123

def downgrade() -> None:
    op.execute("DELETE FROM usuarios WHERE email_usuario = 'admin@email.com'")