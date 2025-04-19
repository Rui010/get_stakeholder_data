import json
import os
from pathlib import Path
import re
from dotenv import load_dotenv
from typing import Any, Dict, Optional

from google import genai
from google.genai.errors import APIError

from get_stakeholder_data.services.logger import Logger

logger = Logger()


def load_prompt_template(filename: str, **kwargs) -> str:
    """
    指定されたテンプレートファイルを読み込み、変数を埋め込んで返す
    """
    base_dir = Path(__file__).resolve().parents[1]  # プロジェクトルート
    prompt_path = base_dir / "prompts" / filename

    with open(prompt_path, encoding="utf-8") as f:
        template = f.read()
    return template.format(**kwargs)


def ai_parser(xml_data: str, prompt_filename: str) -> Optional[Dict[str, Any]]:
    """
    Gemini APIを使って大株主情報のJSONデータを辞書で返す。

    Returns:
        dict: パース済みのデータ（辞書形式）。失敗時は None。
    """
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEYが設定されていません")

    prompt = load_prompt_template(prompt_filename, xml_data=xml_data)

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt,
        )
        # Markdownコードブロック（```json ～ ```）を除去
        cleaned_text = re.sub(
            r"^```json\s*|\s*```$", "", response.text.strip(), flags=re.DOTALL
        )
        return json.loads(cleaned_text)

    except APIError as e:  # API制限エラー
        logger.error(f"Gemini APIの制限に達しました: {e}")
        raise SystemExit("Gemini APIの制限に達したため、プログラムを終了します。")

    except json.JSONDecodeError as e:
        logger.error(f"[JSON ERROR] パース失敗: {e}")
        logger.error(f"[RAW OUTPUT] {response.text}")
        return None

    except Exception as e:
        logger.error(f"予期しないエラーが発生しました: {e}")
        return None
