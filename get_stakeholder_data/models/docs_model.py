from sqlalchemy import Column, String
from get_stakeholder_data.domain.doc import Doc
from get_stakeholder_data.models.base import Base


class DocsModel(Base):
    __tablename__ = "docs"

    doc_id = Column(String, primary_key=True)
    sec_code = Column(String, nullable=True)
    filer_name = Column(String, nullable=True)
    period_start = Column(String, nullable=True)
    period_end = Column(String, nullable=True)
    submit_datetime = Column(String, nullable=True)
    doc_description = Column(String, nullable=True)

    @classmethod
    def from_dataclass(cls, doc: Doc) -> "DocsModel":
        return cls(
            doc_id=doc.doc_id,
            sec_code=doc.sec_code,
            filer_name=doc.filer_name,
            period_start=doc.period_start,
            period_end=doc.period_end,
            submit_datetime=doc.submit_datetime,
            doc_description=doc.doc_description,
        )

    def to_dataclass(self) -> Doc:
        return Doc(
            doc_id=self.doc_id,
            sec_code=self.sec_code,
            filer_name=self.filer_name,
            period_start=self.period_start,
            period_end=self.period_end,
            submit_datetime=self.submit_datetime,
            doc_description=self.doc_description,
        )
