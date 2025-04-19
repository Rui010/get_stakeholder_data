from dataclasses import dataclass
from typing import List
from get_stakeholder_data.domain.doc import Doc


@dataclass
class Docs:
    """
    複数の文書情報を管理するデータクラス
    """

    documents: List[Doc]
