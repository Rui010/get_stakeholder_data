import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

import requests
from get_stakeholder_data.services.get_documents import get_documents
from get_stakeholder_data.domain.doc import Doc
from get_stakeholder_data.domain.docs import Docs


class TestGetDocuments(unittest.TestCase):
    @patch("get_stakeholder_data.services.get_documents.requests.get")
    @patch("get_stakeholder_data.services.get_documents.os.getenv")
    def test_get_documents_success(self, mock_getenv, mock_requests_get):
        """
        正常系: 文書情報が正常に取得できる場合のテスト
        """
        # モックの設定
        mock_getenv.side_effect = lambda key: {
            "EDINET_API_KEY": "dummy_api_key",
            "EDINET_API_ENDPOINT_LIST": "https://dummy.endpoint/documents.json",
        }.get(key)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "metadata": {"status": "200"},
            "results": [
                {
                    "docID": "S100VJ7H",
                    "secCode": "12345",
                    "filerName": "Test Company",
                    "periodStart": "2025-01-01",
                    "periodEnd": "2025-03-31",
                    "submitDateTime": "2025-04-12T10:00:00",
                    "docDescription": "有価証券報告書",
                }
            ],
        }
        mock_requests_get.return_value = mock_response

        # テスト対象の関数を呼び出し
        current_date = datetime.strptime("2025-04-12", "%Y-%m-%d")
        docs = get_documents(current_date)

        # 結果の検証
        self.assertIsInstance(docs, Docs)
        self.assertEqual(len(docs.documents), 1)
        self.assertEqual(docs.documents[0].doc_id, "S100VJ7H")
        self.assertEqual(docs.documents[0].sec_code, "12345")
        self.assertEqual(docs.documents[0].filer_name, "Test Company")

    @patch("get_stakeholder_data.services.get_documents.requests.get")
    @patch("get_stakeholder_data.services.get_documents.os.getenv")
    def test_get_documents_no_results(self, mock_getenv, mock_requests_get):
        """
        正常系: 結果が空の場合のテスト
        """
        # モックの設定
        mock_getenv.side_effect = lambda key: {
            "EDINET_API_KEY": "dummy_api_key",
            "EDINET_API_ENDPOINT_LIST": "https://dummy.endpoint/documents.json",
        }.get(key)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"metadata": {"status": "404"}, "results": []}
        mock_requests_get.return_value = mock_response

        # テスト対象の関数を呼び出し
        current_date = datetime.strptime("2025-04-12", "%Y-%m-%d")
        docs = get_documents(current_date)

        # 結果の検証
        self.assertIsInstance(docs, Docs)
        self.assertEqual(len(docs.documents), 0)

    @patch("get_stakeholder_data.services.get_documents.requests.get")
    @patch("get_stakeholder_data.services.get_documents.os.getenv")
    def test_get_documents_api_error(self, mock_getenv, mock_requests_get):
        """
        異常系: APIリクエストが失敗する場合のテスト
        """
        # モックの設定
        mock_getenv.side_effect = lambda key: {
            "EDINET_API_KEY": "dummy_api_key",
            "EDINET_API_ENDPOINT_LIST": "https://dummy.endpoint/documents.json",
        }.get(key)

        mock_requests_get.side_effect = requests.exceptions.RequestException(
            "API Error"
        )

        # テスト対象の関数を呼び出し
        current_date = datetime.strptime("2025-04-12", "%Y-%m-%d")
        with self.assertRaises(RuntimeError) as context:
            get_documents(current_date)

        # エラーメッセージの検証
        self.assertIn("EDINET APIリクエストに失敗しました", str(context.exception))

    @patch("get_stakeholder_data.services.get_documents.requests.get")
    @patch("get_stakeholder_data.services.get_documents.os.getenv")
    def test_get_documents_invalid_json(self, mock_getenv, mock_requests_get):
        """
        異常系: APIレスポンスが不正なJSONの場合のテスト
        """
        # モックの設定
        mock_getenv.side_effect = lambda key: {
            "EDINET_API_KEY": "dummy_api_key",
            "EDINET_API_ENDPOINT_LIST": "https://dummy.endpoint/documents.json",
        }.get(key)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_requests_get.return_value = mock_response

        # テスト対象の関数を呼び出し
        current_date = datetime.strptime("2025-04-12", "%Y-%m-%d")
        with self.assertRaises(RuntimeError) as context:
            get_documents(current_date)

        # エラーメッセージの検証
        self.assertIn("APIレスポンスのJSONパースに失敗しました", str(context.exception))


if __name__ == "__main__":
    unittest.main()
