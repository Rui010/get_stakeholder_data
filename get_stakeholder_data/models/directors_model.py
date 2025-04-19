from sqlalchemy import Column, String, Integer, ForeignKey
from get_stakeholder_data.models.base import Base
from get_stakeholder_data.domain.director import Director


class DirectorsModel(Base):
    __tablename__ = "directors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(
        String, ForeignKey("docs.doc_id"), nullable=False
    )  # docsテーブルとの関連付け
    name = Column(String, nullable=False)
    title = Column(String, nullable=True)
    birth_date = Column(String, nullable=True)
    biography = Column(String, nullable=True)
    shares_owned = Column(String, nullable=True)

    @classmethod
    def from_dataclass(cls, director: Director, doc_id: str) -> "DirectorsModel":
        return cls(
            doc_id=doc_id,
            name=director.name,
            title=director.title,
            birth_date=director.birth_date,
            biography=director.biography,
            shares_owned=director.shares_owned,
        )
