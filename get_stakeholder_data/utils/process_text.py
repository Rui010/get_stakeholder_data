import re
from bs4 import BeautifulSoup


def clean_text(text):
    """改行・全角スペース・連続空白を除去"""
    if not text:
        return ""
    text = text.replace("\n", "").replace("\r", "")
    text = re.sub(r"\s+", " ", text)  # 複数空白を1つに
    text = text.replace("\u3000", " ")  # 全角スペースを半角へ
    return text.strip()


def strip_html_tags(html):
    """
    HTMLタグを除去してテキスト情報だけを抽出する

    Args:
        html (str): HTML文字列

    Returns:
        str: HTMLタグが除去されたテキスト
    """
    if not html:
        return ""
    # HTMLタグを除去
    text = re.sub(r"<[^>]+>", "", html)
    # 改行や余分な空白を削除
    text = re.sub(r"\s+", " ", text)
    return text.strip()


from bs4 import BeautifulSoup


from bs4 import BeautifulSoup
import html


def html_table_to_array(html_str: str) -> list[list[str]]:
    """
    HTMLテーブルを配列形式に変換する

    Args:
        html_str (str): HTML文字列（&lt;などが含まれていてもOK）

    Returns:
        list of list: 行ごとのテキスト配列
    """
    if not html_str:
        return []

    # HTMLエスケープを解除
    html_str = html.unescape(html_str)
    soup = BeautifulSoup(html_str, "html.parser")

    table = []

    for row in soup.find_all("tr"):
        cells = []

        # <td> または <th> を対象にする
        for cell in row.find_all(["td", "th"]):
            # 各セル内のすべての <p> や <br> を含めて改行で結合
            text_parts = []

            for p in cell.find_all(["p", "br"]):
                txt = p.get_text(strip=True)
                if txt:
                    text_parts.append(txt)

            # 空なら全体テキスト、それ以外は結合
            if text_parts:
                cell_text = " / ".join(text_parts)
            else:
                cell_text = cell.get_text(strip=True)

            cells.append(cell_text)

        if cells:
            table.append(cells)

    return table
