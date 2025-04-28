import re
from get_stakeholder_data.interface.database import SessionLocal, init_db
from get_stakeholder_data.models.directors_model import DirectorsModel
from datetime import datetime


def clean_directors():
    session = SessionLocal()
    try:
        for director in session.query(DirectorsModel).all():
            director.name_clean = normalize_name(director.name)
            director.birth_date_iso = normalize_date(director.birth_date)
            session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
    finally:
        session.close()


def normalize_name(name: str) -> str:

    if not name or name.strip() == "":
        return None

    # 1. 全角英数字を半角に
    name = name.translate(
        str.maketrans(
            "ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ"
            "ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ"
            "０１２３４５６７８９",
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ" "abcdefghijklmnopqrstuvwxyz" "0123456789",
        )
    )

    # 2. 括弧（）内を削除
    name = re.sub(r"\（.*?\）|\(.*?\)", "", name)

    # 3. 日本語を含むかチェック
    if re.search(r"[\u3040-\u30FF\u4E00-\u9FFF]", name):
        # 日本語が含まれる場合はすべてスペース削除
        name = re.sub(r"\s+", "", name)
    else:
        # 英語だけならスペース1個に整形
        name = re.sub(r"\s+", " ", name)

    return name.strip()


def normalize_date(date_str: str) -> str:
    """
    日付文字列を正規化してISO形式に変換する関数。

    Args:
        date_str (str): 入力の日付文字列（全角・半角混在可）

    Returns:
        str: ISO形式の日付文字列（YYYY-MM-DD）
    """
    if not date_str:
        return None
    # 全角数字を半角に変換
    date_str = date_str.translate(str.maketrans("０１２３４５６７８９", "0123456789"))

    # 全角スペースを半角スペースに変換
    date_str = date_str.replace("　", " ")

    # 「年」「月」をハイフンに置き換え
    date_str = re.sub(r"[年月]", "-", date_str)

    # 「日」「生」「()」「（）」余計な文字を削除
    ext_chars = ["日", "生", "(", "（", ")", "）"]
    for char in ext_chars:
        date_str = date_str.replace(char, "")

    # 不要なスペースを削除
    date_str = date_str.strip()

    # 月や日の1桁を2桁に補正
    date_str = re.sub(r"-(\d)-", r"-0\1-", date_str)  # 月
    date_str = re.sub(r"-(\d)$", r"-0\1", date_str)  # 日

    # ISO形式に変換
    try:
        parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
        return parsed_date.strftime("%Y-%m-%d")
    except ValueError:
        return None  # パースできない場合は None を返す


if __name__ == "__main__":
    clean_directors()
