from sqlalchemy import Column, String, Integer, ForeignKey
from get_stakeholder_data.models.base import Base


class StocksModel(Base):
    __tablename__ = "stocks"

    code = Column(String, primary_key=True)
    name = Column(String, nullable=True)
    market = Column(String, nullable=True)
    sector_33 = Column(String, nullable=True)
    sector_17 = Column(String, nullable=True)
    scale = Column(String, nullable=True)
