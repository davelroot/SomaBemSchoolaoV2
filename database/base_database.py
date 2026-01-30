from datetime import datetime, date
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Boolean, func, text
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import Session

# ============================================================================
#                    BASE ÚNICA PARA TODO O SISTEMA
# ============================================================================

Base = declarative_base()












def create_schemas(engine):

    pass