import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from get_stakeholder_data.models.stocks_model import StocksModel
from get_stakeholder_data.interface.database import Base, SessionLocal, init_db


def import_stocks(excel_file_path: str) -> None:
    """
    EXCELファイルからデータを読み込み、銘柄情報をデータベースに挿入する関数。
    指定したテーブルが存在する場合、テーブルを削除してから新たに作成する。

    :param excel_file_path: EXCELファイルのパス
    :return: None
    """
    # データベースの初期化
    init_db()

    # セッションを作成
    session = SessionLocal()

    # テーブルを再作成
    Base.metadata.drop_all(bind=session.bind, tables=[StocksModel.__table__])
    Base.metadata.create_all(bind=session.bind, tables=[StocksModel.__table__])

    # Excelファイルを読み込む
    input_book = pd.ExcelFile(excel_file_path)
    df = input_book.parse("Sheet1")

    # 市場名の変換辞書
    dict_market = {
        "市場第一部（内国株）": "東証1部",
        "JASDAQ(スタンダード・内国株）": "JASDAQ(スタンダード）",
        "JASDAQ(グロース・内国株）": "JASDAQ(グロース）",
        "マザーズ（内国株）": "マザーズ",
        "市場第二部（内国株）": "東証2部",
        "市場第一部（外国株）": "東証1部(外国株)",
        "市場第二部（外国株）": "東証2部(外国株)",
        "-": "",
        "プライム（内国株式）": "プライム",
        "グロース（内国株式）": "グロース",
        "スタンダード（内国株式）": "スタンダード",
        "プライム（外国株式）": "プライム(外国株)",
        "グロース（外国株式）": "グロース(外国株)",
        "スタンダード（外国株式）": "スタンダード(外国株)",
    }
    df.replace(dict_market, inplace=True)

    # データをデータベースに挿入
    try:
        for _, row in df.iterrows():
            stock = StocksModel(
                code=row["コード"],
                name=row["銘柄名"],
                market=row["市場・区分"],
                sector_33=row["33業種コード"],
                sector_17=row["17業種コード"],
                scale=row["規模"],
            )
            session.add(stock)
        session.commit()
        print("データベースにデータを挿入しました。")
    except Exception as e:
        session.rollback()
        print(f"エラーが発生しました: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    import_stocks(
        "get_stakeholder_data\stocks_data\data_j.xls",
    )
