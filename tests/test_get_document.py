import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import io

import requests
from get_stakeholder_data.services.get_document import get_document


class TestGetDocument(unittest.TestCase):
    @patch("get_stakeholder_data.services.get_document.requests.get")
    @patch("get_stakeholder_data.services.get_document.os.getenv")
    @patch("get_stakeholder_data.services.get_document.zipfile.ZipFile")
    @patch("get_stakeholder_data.services.get_document.open", new_callable=mock_open)
    @patch("get_stakeholder_data.services.get_document.os.makedirs")
    def test_get_document_success(
        self,
        mock_makedirs,
        mock_open_file,
        mock_zipfile,
        mock_getenv,
        mock_requests_get,
    ):
        """
        正常系: XBRLファイルが正常に取得できる場合のテスト
        """
        # モックの設定
        mock_getenv.side_effect = lambda key: {
            "EDINET_API_KEY": "dummy_api_key",
            "EDINET_API_ENDPOINT_DOC": "https://dummy.endpoint/documents",
        }.get(key)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"dummy_zip_content"
        mock_requests_get.return_value = mock_response

        mock_zip = MagicMock()
        mock_zip.namelist.return_value = ["dummy.xbrl"]
        mock_zip.open.return_value = io.BytesIO(b"dummy_xbrl_content")
        mock_zipfile.return_value.__enter__.return_value = mock_zip

        # テスト対象の関数を呼び出し
        doc_id = "S100VJ7H"
        company_code = "12345"
        save_dir = "test_xbrl_data"
        result = get_document(doc_id, company_code, save_dir)

        # 検証
        self.assertEqual(result, b"dummy_xbrl_content")
        mock_requests_get.assert_called_once_with(
            "https://dummy.endpoint/documents/S100VJ7H",
            params={"type": 1, "Subscription-Key": "dummy_api_key"},
        )
        mock_makedirs.assert_called_once_with(
            os.path.join(save_dir, company_code), exist_ok=True
        )
        mock_open_file.assert_called_once_with(
            os.path.join(save_dir, company_code, f"{doc_id}.xbrl"), "wb"
        )

    @patch("get_stakeholder_data.services.get_document.os.makedirs")
    @patch("get_stakeholder_data.services.get_document.os.path.exists")
    @patch("get_stakeholder_data.services.get_document.open", new_callable=mock_open)
    def test_get_document_existing_file(
        self, mock_open_file, mock_path_exists, mock_makedirs
    ):
        """
        正常系: 既存のXBRLファイルが存在する場合のテスト
        """
        # モックの設定
        mock_path_exists.return_value = True  # ファイルが存在する
        mock_open_file.return_value.read.return_value = b"existing_xbrl_content"

        # テスト対象の関数を呼び出し
        doc_id = "S100VJ7H"
        company_code = "12345"
        save_dir = "test_xbrl_data"
        result = get_document(doc_id, company_code, save_dir)

        # 検証
        self.assertEqual(result, b"existing_xbrl_content")
        mock_path_exists.assert_any_call(
            os.path.join(save_dir, company_code, f"{doc_id}.xbrl")
        )
        mock_open_file.assert_called_once_with(
            os.path.join(save_dir, company_code, f"{doc_id}.xbrl"), "rb"
        )

    @patch("get_stakeholder_data.services.get_document.requests.get")
    @patch("get_stakeholder_data.services.get_document.os.getenv")
    def test_get_document_api_error(self, mock_getenv, mock_requests_get):
        """
        異常系: APIリクエストが失敗する場合のテスト
        """
        # モックの設定
        mock_getenv.side_effect = lambda key: {
            "EDINET_API_KEY": "dummy_api_key",
            "EDINET_API_ENDPOINT_DOC": "https://dummy.endpoint/documents",
        }.get(key)

        # `requests.exceptions.RequestException` をスローするように設定
        mock_requests_get.side_effect = requests.exceptions.RequestException(
            "API Error"
        )

        # テスト対象の関数を呼び出し
        doc_id = "S100VJ7H"
        with self.assertRaises(RuntimeError) as context:
            get_document(doc_id)

        # 検証
        self.assertIn("EDINET APIリクエストに失敗しました", str(context.exception))

    @patch("get_stakeholder_data.services.get_document.requests.get")
    @patch("get_stakeholder_data.services.get_document.os.getenv")
    @patch("get_stakeholder_data.services.get_document.zipfile.ZipFile")
    def test_get_document_no_xbrl_file(
        self, mock_zipfile, mock_getenv, mock_requests_get
    ):
        """
        異常系: ZIPファイルにXBRLファイルが含まれていない場合のテスト
        """
        # モックの設定
        mock_getenv.side_effect = lambda key: {
            "EDINET_API_KEY": "dummy_api_key",
            "EDINET_API_ENDPOINT_DOC": "https://dummy.endpoint/documents",
        }.get(key)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"dummy_zip_content"
        mock_requests_get.return_value = mock_response

        mock_zip = MagicMock()
        mock_zip.namelist.return_value = []  # XBRLファイルが含まれていない
        mock_zipfile.return_value.__enter__.return_value = mock_zip

        # テスト対象の関数を呼び出し
        doc_id = "S100VJ7H"
        with self.assertRaises(Exception) as context:
            get_document(doc_id)

        # 検証
        self.assertIn("XBRLファイルが見つかりませんでした", str(context.exception))


if __name__ == "__main__":
    unittest.main()
