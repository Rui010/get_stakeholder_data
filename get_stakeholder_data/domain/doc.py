from dataclasses import dataclass
from typing import Optional


@dataclass
class Doc:
    """
    個別の文書情報を表すデータクラス
    """

    doc_id: str
    sec_code: Optional[str]
    filer_name: Optional[str]
    period_start: Optional[str]
    period_end: Optional[str]
    submit_datetime: Optional[str]
    doc_description: Optional[str]
