from sqlalchemy import Column, String, Integer, ForeignKey
from get_stakeholder_data.models.base import Base
from get_stakeholder_data.domain.shareholder import Shareholder


class ShareholdersModel(Base):
    __tablename__ = "shareholders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(
        String, ForeignKey("docs.doc_id"), nullable=False
    )  # docsテーブルとの関連付け
    name = Column(String, nullable=False)
    address = Column(String, nullable=True)
    shares_held = Column(String, nullable=True)
    ownership_ratio = Column(String, nullable=True)

    @classmethod
    def from_dataclass(
        cls, shareholder: Shareholder, doc_id: str
    ) -> "ShareholdersModel":
        return cls(
            doc_id=doc_id,
            name=shareholder.name,
            address=shareholder.address,
            shares_held=shareholder.shares_held,
            ownership_ratio=shareholder.ownership_ratio,
        )
