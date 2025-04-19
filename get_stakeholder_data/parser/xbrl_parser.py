import io
import xml.etree.ElementTree as ET

from get_stakeholder_data.services.ai_parser import ai_parser
from get_stakeholder_data.utils.process_text import clean_text, html_table_to_array
from get_stakeholder_data.domain.director import Director
from get_stakeholder_data.domain.shareholder import Shareholder


class ParsingError(Exception):
    """パーサーでのエラーを表すカスタム例外"""

    pass


class XbrlParser:

    def __init__(self, xbrl_bytes: bytes):
        self.xbrl_bytes = xbrl_bytes
        self.root = ET.fromstring(xbrl_bytes)
        # 全プレフィックスとURIを取得
        self.namespaces = dict(
            node
            for _, node in ET.iterparse(io.BytesIO(xbrl_bytes), events=["start-ns"])
        )

        # 重要なタグが存在するプレフィックス（例：jpcrp_cor）を特定
        self.jp_prefix = self._detect_jp_namespace_prefix()
        self.ns = {self.jp_prefix: self.namespaces[self.jp_prefix]}

    def _detect_jp_namespace_prefix(self):
        """
        MajorShareholdersTextBlock が存在するプレフィックスを探索
        """
        for prefix, uri in self.namespaces.items():
            # プレフィックス付きでタグを探す
            # print(prefix, uri)
            if (
                self.root.find(f".//{prefix}:MajorShareholdersTextBlock", {prefix: uri})
                is not None
            ):
                return prefix
        raise ValueError("有効なMajorShareholdersTextBlockタグが見つかりませんでした")

    def extract_officer_block(self):
        """
        XBRLルートから役員情報TextBlockを抽出する（柔軟対応）
        """
        candidates = [
            "InformationAboutOfficersTextBlock",
            "InformationAboutDirectorsTextBlock",
            "InformationAboutDirectorsAndCorporateAuditorsTextBlock",
        ]
        for tag in candidates:
            el = self.root.findall(
                f'.//{self.jp_prefix}:{tag}[@contextRef="FilingDateInstant"]',
                self.ns,
            )
            if len(el) > 0 and el[0].text:
                return el
        return []

    def get_directors_and_auditors(self):
        try:
            # 役員
            names = self.root.findall(
                ".//jp:NameInformationAboutDirectorsAndCorporateAuditors", self.ns
            )
            titles = self.root.findall(
                ".//jp:OfficialTitleOrPositionInformationAboutDirectorsAndCorporateAuditors",
                self.ns,
            )
            births = self.root.findall(
                ".//jp:DateOfBirthInformationAboutDirectorsAndCorporateAuditors",
                self.ns,
            )
            # information_table = self.root.findall(
            #     './/jp:InformationAboutdirectorsTextBlock[@contextRef="FilingDateInstant"]',
            #     self.ns,
            # )
            information_table = self.extract_officer_block()
            information_table = html_table_to_array(information_table[0].text)
            directors = []
            for name, title, birth, information_row in zip(
                names, titles, births, information_table
            ):
                if len(information_row) < 4:
                    continue
                directors.append(
                    Director(
                        name=clean_text(name.text),  # 氏名
                        title=clean_text(title.text),  # 肩書き
                        birth_date=clean_text(birth.text),  # 生年月日
                        biography=information_row[3].replace("\u3000", "\n"),  # 略歴
                        shares_owned=clean_text(information_row[5]),  # 所有株式数(百株)
                    )
                )
            return directors
        except Exception as e:
            raise ParsingError(f"役員情報のパースに失敗しました: {e}")

    def get_major_shareholders(self):
        try:
            block = self.root.find(".//jp:MajorShareholdersTextBlock", self.ns)
            if block is None or not block.text:
                return []

            information_table = html_table_to_array(block.text)
            shareholders = []
            for row in information_table:
                if len(row) < 4:
                    continue
                shareholders.append(
                    Shareholder(
                        name=clean_text(row[0]),  # 氏名
                        address=clean_text(row[1]),  # 住所
                        shares_held=clean_text(row[2]),  # 保有株数
                        ownership_ratio=clean_text(row[3]),  # 保有割合
                    )
                )

            return shareholders
        except Exception as e:
            raise ParsingError(f"株主情報のパースに失敗しました: {e}")

    def get_major_shareholders_by_llm(self):
        try:
            block = self.root.find(
                f".//{self.jp_prefix}:MajorShareholdersTextBlock", self.ns
            )
            if block is None or not block.text:
                return []
            json_data = ai_parser(block.text, "shareholder_prompt.txt")
            return json_data
        except Exception as e:
            raise ParsingError(f"株主情報のパースに失敗しました: {e}")

    def get_major_officers_by_llm(self):
        try:
            block = self.extract_officer_block()
            if block is None or not block[0].text:
                return []
            json_data = ai_parser(block[0].text, "officer_prompt.txt")
            return json_data
        except Exception as e:
            raise ParsingError(f"役員情報のパースに失敗しました: {e}")
