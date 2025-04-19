import io
import os
import zipfile
from dotenv import load_dotenv
import requests
from get_stakeholder_data.services.logger import Logger

# ロガーの初期化
logger = Logger()


def get_document(doc_id: str, company_code="unknown", save_dir="xbrl_data") -> bytes:
    """
    指定した日付の有価証券報告書を取得する

    Args:
        doc_id (str): 取得対象の日付
        company_code(str): 企業コード
        save_dir (str): 保存先ディレクトリ

    Returns:
        str: XBRLファイルのバイナリデータ

    Raises:
        ValueError: 必要な環境変数が設定されていない場合
        RuntimeError: APIリクエストが失敗した場合
    """
    load_dotenv()
    api_key = os.getenv("EDINET_API_KEY")
    api_endpoint_doc = os.getenv("EDINET_API_ENDPOINT_DOC")
    if not api_key or not api_endpoint_doc:
        raise Exception(
            "EDINET_API_KEY または EDINET_API_ENDPOINT_DOC が設定されていません"
        )

    company_dir = os.path.join(save_dir, company_code)
    os.makedirs(company_dir, exist_ok=True)

    save_path = os.path.join(company_dir, f"{doc_id}.xbrl")

    # 既存ファイルの確認
    if os.path.exists(save_path):
        logger.info(
            f"既存のXBRLファイルを使用します - doc_id:{doc_id} - company_code:{company_code}"
        )
        with open(save_path, "rb") as existing_file:
            return existing_file.read()

    # APIリクエスト
    url = f"{api_endpoint_doc}/{doc_id}"
    params = {"type": 1, "Subscription-Key": api_key}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # HTTPエラーが発生した場合に例外をスロー
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"EDINET APIリクエストに失敗しました: {e}")

    # ZIPファイルからXBRLファイルを抽出
    try:
        with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
            if not zf.namelist():
                raise Exception("ZIPファイルが空です")
            for name in zf.namelist():
                if name.endswith(".xbrl"):
                    with zf.open(name) as f:
                        xbrl_bytes = f.read()
                    break
            else:
                raise Exception("XBRLファイルが見つかりませんでした")
    except zipfile.BadZipFile as e:
        raise Exception(f"ZIPファイルが不正です: {e}")

    with open(save_path, "wb") as out:
        out.write(xbrl_bytes)

    # TODO：ログ出力する
    logger.info(f"XBRL取得完了 - doc_id:{doc_id} - company_code:{company_code}")
    return xbrl_bytes
