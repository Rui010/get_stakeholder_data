import re
from get_stakeholder_data.interface.database import SessionLocal, init_db
from get_stakeholder_data.models.directors_model import DirectorsModel
from datetime import datetime


def clean_directors():
    session = SessionLocal()
    for director in session.query(DirectorsModel).limit(10).all():
        director.name_clean = director.name.replace(" ", "")
        # director.title_clean = director.title.replace(" ", "")
        director.birth_date_iso = normalize_date(director.birth_date)


def normalize_date(date_str: str) -> str:
    """
    日付文字列を正規化してISO形式に変換する関数。

    Args:
        date_str (str): 入力の日付文字列（全角・半角混在可）

    Returns:
        str: ISO形式の日付文字列（YYYY-MM-DD）
    """
    # 全角数字を半角に変換
    date_str = date_str.translate(str.maketrans("０１２３４５６７８９", "0123456789"))

    # 全角スペースを半角スペースに変換
    date_str = date_str.replace("　", " ")

    # 「年」「月」をハイフンに置き換え
    date_str = re.sub(r"[年月]", "-", date_str)

    # 「日」「生」を削除
    date_str = date_str.replace("日", "")
    date_str = date_str.replace("生", "")

    # 不要なスペースを削除
    date_str = date_str.strip()

    # 月や日の1桁を2桁に補正
    date_str = re.sub(r"-(\d)-", r"-0\1-", date_str)  # 月
    date_str = re.sub(r"-(\d)$", r"-0\1", date_str)  # 日
    print(date_str)

    # ISO形式に変換
    try:
        parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
        return parsed_date.strftime("%Y-%m-%d")
    except ValueError:
        return None  # パースできない場合は None を返す


if __name__ == "__main__":
    clean_directors()
