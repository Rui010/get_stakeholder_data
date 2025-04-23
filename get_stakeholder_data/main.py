from get_stakeholder_data.domain.director import Director
from get_stakeholder_data.parser.xbrl_parser import (
    XbrlParser,
    ParsingError,
)  # カスタム例外をインポート
from get_stakeholder_data.services.get_document import get_document
from get_stakeholder_data.services.get_documents import get_documents
from get_stakeholder_data.interface.database import SessionLocal, init_db
from get_stakeholder_data.models.docs_model import DocsModel
from get_stakeholder_data.models.directors_model import DirectorsModel
from get_stakeholder_data.models.shareholders_model import ShareholdersModel
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from get_stakeholder_data.services.logger import Logger  # ロガーをインポート
from get_stakeholder_data.domain.shareholder import Shareholder


def main():
    """
    メイン関数
    """
    init_db()  # DBの初期化
    session = SessionLocal()
    logger = Logger()  # ロガーのインスタンスを作成
    start_date = datetime(2025, 3, 1)
    end_date = datetime(2025, 3, 31)
    current = start_date
    while current <= end_date:
        docs = get_documents(current)
        for doc in docs.documents:
            try:
                # ドキュメントが既に存在するか確認
                existing_doc = (
                    session.query(DocsModel).filter_by(doc_id=doc.doc_id).first()
                )
                if existing_doc:
                    logger.info(
                        f"ドキュメント {doc.doc_id} は既に存在するためスキップします"
                    )
                    continue  # 既存データがある場合はスキップ
                # ドキュメント情報を保存
                session.add(DocsModel.from_dataclass(doc))
                # XBRLファイルを取得
                xbrl_byte = get_document(
                    doc.doc_id, company_code=doc.sec_code, save_dir="xbrl_data"
                )
                parser = XbrlParser(xbrl_byte)

                # 役員情報を保存
                officers = parser.get_major_officers_by_llm()
                for officer in officers["役員の状況"]["data"]:
                    director_dataclass = Director(
                        name=officer["氏名"]
                        .replace("\u3000", " ")
                        .replace("\n", " ")
                        .strip(),
                        title=officer["役職名"].replace("\u3000", " ").strip(),
                        birth_date=officer["生年月日"].replace("\u3000", " ").strip(),
                        biography=officer["略歴"].replace("\u3000", " ").strip(),
                        shares_owned=officer["所有株式数(千株)"],
                    )
                    session.add(
                        DirectorsModel.from_dataclass(director_dataclass, doc.doc_id)
                    )
                # 株主情報を保存
                major_shareholders = parser.get_major_shareholders_by_llm()
                for shareholder in major_shareholders["大株主の状況"]["data"]:
                    if shareholder["氏名又は名称"] == "計":
                        continue
                    shareholder_dataclass = Shareholder(
                        name=shareholder["氏名又は名称"].replace("\u3000", " ").strip(),
                        address=shareholder["住所"].replace("\u3000", " ").strip(),
                        shares_held=shareholder["所有株式数(千株)"],
                        ownership_ratio=shareholder["所有割合(％)"],
                    )
                    session.add(
                        ShareholdersModel.from_dataclass(
                            shareholder_dataclass, doc.doc_id
                        )
                    )

                session.commit()  # 一本ずつコミット
                logger.info(f"ドキュメント {doc.doc_id} の処理が完了しました")

            except IntegrityError:
                session.rollback()  # エラー時にロールバック
                logger.error(f"主キーの重複エラーをスキップ: {doc}")

            except ParsingError as e:
                session.rollback()  # エラー時にロールバック
                logger.error(f"パーサーエラーをスキップ: {doc}, エラー内容: {e}")

            except Exception as e:
                session.rollback()  # その他のエラーもロールバック
                logger.error(f"予期しないエラーが発生: {doc}, エラー内容: {e}")

        current += timedelta(days=1)

    session.close()


def test():
    xbrl_byte = get_document("S100TA7H", company_code="75900", save_dir="xbrl_data")
    parser = XbrlParser(xbrl_byte)
    officers = parser.get_major_shareholders_by_llm()
    print(officers)


if __name__ == "__main__":

    main()
    # test()
