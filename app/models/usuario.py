from datetime import datetime, date, timezone
from typing import Optional
import enum

from sqlalchemy import Date, String, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class TipoUsuario(str, enum.Enum):
    gerente = "gerente"
    usuario = "usuario"

class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome_usuario: Mapped[str] = mapped_column(String(255))
    email_usuario: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    senha_usuario: Mapped[str] = mapped_column(String(255))
    tipo_usuario: Mapped[TipoUsuario] = mapped_column(Enum(TipoUsuario), default=TipoUsuario.usuario)
    data_cadastro: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    data_nascimento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)