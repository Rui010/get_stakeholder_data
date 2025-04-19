import os
from dotenv import load_dotenv
import requests

from get_stakeholder_data.domain.doc import Doc
from get_stakeholder_data.domain.docs import Docs
from get_stakeholder_data.services.logger import Logger

# ロガーの初期化
logger = Logger()


def get_documents(current_date):
    """
    指定した日付の有価証券報告書を取得する

    Args:
        current_date (datetime): 取得対象の日付

    Returns:
        list: 文書情報のリスト

    Raises:
        ValueError: 必要な環境変数が設定されていない場合
        RuntimeError: APIリクエストが失敗した場合
    """
    load_dotenv()  # .env を読み込む
    api_key = os.getenv("EDINET_API_KEY")
    api_endpoint_list = os.getenv("EDINET_API_ENDPOINT_LIST")
    if not api_key or not api_endpoint_list:
        raise Exception(
            "EDINET_API_KEY または EDINET_API_ENDPOINT_LIST が設定されていません"
        )

    params = {
        "date": current_date.strftime("%Y-%m-%d"),
        "type": "2",
        "Subscription-Key": api_key,
    }
    try:
        res = requests.get(api_endpoint_list, params=params)
        res.raise_for_status()  # HTTPエラーが発生した場合に例外をスロー
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"EDINET APIリクエストに失敗しました: {e}")

    try:
        obj = res.json()
    except ValueError as e:
        raise RuntimeError(f"APIレスポンスのJSONパースに失敗しました: {e}")

    if obj.get("metadata", {}).get("status") == "404":
        return Docs(documents=[])

    records = obj.get("results", [])
    docs = []
    for record in records:
        if (
            "有価証券報告書" in (record.get("docDescription") or "")
            and record.get("secCode") is not None
            and "訂正" not in (record.get("docDescription") or "")
        ):
            doc = Doc(
                doc_id=record.get("docID"),
                sec_code=record.get("secCode"),
                filer_name=record.get("filerName"),
                period_start=record.get("periodStart"),
                period_end=record.get("periodEnd"),
                submit_datetime=record.get("submitDateTime"),
                doc_description=record.get("docDescription"),
            )
            docs.append(doc)
    logger.info(
        f"有価証券報告書一覧取得完了 - current_date:{current_date.strftime("%Y-%m-%d")}"
    )
    return Docs(documents=docs)
