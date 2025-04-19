from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import requests
import zipfile
import io
import xml.etree.ElementTree as ET
from itertools import zip_longest
from bs4 import BeautifulSoup
import re


def extract_major_shareholders_from_html(root, ns):
    block = root.find(".//jp:MajorShareholdersTextBlock", ns)
    if block is None or not block.text:
        return []

    soup = BeautifulSoup(block.text, "html.parser")
    rows = soup.find_all("tr")

    result = []
    for row in rows:
        cols = [td.get_text(strip=True) for td in row.find_all("td")]
        if len(cols) >= 3:
            result.append({"氏名": cols[0], "保有株数": cols[1], "保有割合": cols[2]})
    return result


def parse_xbrl_latest(xbrl_bytes):
    ns = {
        "jp": "http://disclosure.edinet-fsa.go.jp/taxonomy/jpcrp/2023-12-01/jpcrp_cor"
    }
    root = ET.fromstring(xbrl_bytes)

    def clean_text(text):
        import re

        if not text:
            return ""
        text = text.replace("\n", "").replace("\r", "")
        text = re.sub(r"\s+", " ", text)
        text = text.replace("\u3000", " ")
        return text.strip()

    # 代表者
    rep = root.find(".//jp:TitleAndNameOfRepresentativeCoverPage", ns)
    representative = clean_text(rep.text) if rep is not None and rep.text else None

    major_shareholders = extract_major_shareholders_from_html(root, ns)

    # 役員
    names = root.findall(".//jp:NameInformationAboutDirectorsAndCorporateAuditors", ns)
    titles = root.findall(
        ".//jp:OfficialTitleOrPositionInformationAboutDirectorsAndCorporateAuditors", ns
    )
    births = root.findall(
        ".//jp:DateOfBirthInformationAboutDirectorsAndCorporateAuditors", ns
    )

    officers = []
    for name, title, birth in zip(names, titles, births):
        officers.append(
            {
                "氏名": clean_text(name.text),
                "肩書き": clean_text(title.text),
                "生年月日": clean_text(birth.text),
            }
        )

    return {
        "代表者": representative,
        "大株主": major_shareholders,
        "役員一覧": officers,
    }


def find_elements_by_partial_tag(xbrl_bytes, keyword):
    root = ET.fromstring(xbrl_bytes)
    results = []
    for el in root.iter():
        if keyword.lower() in el.tag.lower():  # 大文字小文字を無視して検索
            text = el.text.strip() if el.text else ""
            results.append((el.tag, text[:100]))  # テキストは最初の100文字だけ表示
    return results


# テスト実行（例：KDDI：S100QY2Z ※提出書類ID）
doc_id = "S100VJ7H"
xbrl_data = download_edinet_xbrl(doc_id)
# print(xbrl_data.decode("utf-8")[:3000])
# info = parse_xbrl(xbrl_data)

# print("■ 代表者：", info["代表者"])
# print("■ 役員一覧：", info["役員一覧"][:200], "…")  # 長いので一部だけ
# print("■ 大株主：", info["大株主"][:200], "…")

# keywords = ["Representative", "Shareholder", "Officer", "Management", "Director"]

# for kw in keywords:
#     print(f"\n🔍 キーワード: {kw}")
#     for tag, text in find_elements_by_partial_tag(xbrl_data, kw):
#         print(f"{tag} → {text}")

result = parse_xbrl_latest(xbrl_data)

print("■ 代表者:", result["代表者"])

print("\n■ 大株主:")
for s in result["大株主"]:
    print(f" - {s['氏名']} / {s['保有株数']} / {s['保有割合']}")

print("\n■ 役員一覧:")
for o in result["役員一覧"]:
    print(f" - {o['氏名']}（{o['肩書き']}） 生年: {o['生年月日']}")
