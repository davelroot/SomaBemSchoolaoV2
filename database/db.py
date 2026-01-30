from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ============================================================================
#                    IMPORTAR BASE UNIFICADA
# ============================================================================

from .base_database import Base, create_schemas












# ============================================================================
#                    CONFIGURAÇÃO DO BANCO DE DADOS
# ============================================================================

# MySQL/MariaDB
#DB_URL = "mysql+mysqlconnector://erpuser:erp123456@localhost/nzilacode_pos"

# PostgreSQL (Recomendado para AGT/OCA compliance)
DB_URL = "postgresql://erpuser:erp123456@192.168.5.12/nzilacode_pos"

# Criar engine
engine = create_engine(
    DB_URL, 
    echo=False,
    pool_pre_ping=True,  # Verifica conexão antes de usar
    pool_recycle=3600,   # Recicla conexões a cada hora
)

# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)
