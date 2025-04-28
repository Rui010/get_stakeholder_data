from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from get_stakeholder_data.models.base import Base  # declarative_base() で定義
from get_stakeholder_data.models.docs_model import DocsModel  # 既存のモデル
from get_stakeholder_data.models.directors_model import DirectorsModel  # 新しいモデル
from get_stakeholder_data.models.shareholders_model import (
    ShareholdersModel,
)  # 新しいモデル
from get_stakeholder_data.models.stocks_model import StocksModel  # 新しいモデル


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise Exception("DATABASE_URL が設定されていません")
# エンジン作成（echo=True にするとSQLログが表示されて便利）
engine = create_engine(DATABASE_URL, echo=False, future=True)

# セッションのファクトリ
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


# テーブルを作成（なければ）
def init_db():
    Base.metadata.create_all(bind=engine)
