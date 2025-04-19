# Get Stakeholder Data

このプロジェクトは、XBRLデータを解析し、企業の役員情報や大株主情報を取得・保存するためのツールです。Gemini APIやEDINET APIを活用してデータを収集し、データベースに保存します。

---

## 📋 機能

- EDINET APIを使用して企業のXBRLデータを取得
- XBRLデータから役員情報や大株主情報を解析
- Gemini APIを使用して自然言語処理を実行
- データをSQLiteデータベースに保存
- ログ出力によるエラー追跡

---

## 🛠️ 必要な環境

- Python 3.9以上
- 必要なライブラリは `requirements.txt` に記載

---

## 🚀 環境構築手順

### 1. リポジトリをクローン

```bash
git clone https://github.com/your-username/get_stakeholder_data.git
cd get_stakeholder_data
```

### 2. 仮想環境を作成して有効化

```bash
python -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate
```

### 3. 必要なライブラリをインストール

```bash
pip install -r requirements.txt
```

### 4. .env ファイルを作成

```bash
# .env の例
EDINET_API_KEY=your_edinet_api_key
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=sqlite:///stakeholders.db
```

## 📦 使用方法

### 1. データベースの初期化

以下のコマンドでデータベースを初期化します。

```bash
python -m get_stakeholder_data.main
```

### 2. データの取得

指定した期間のXBRLデータを取得し、解析します。

🧪 テスト
テストを実行するには以下のコマンドを使用します。

```bash
python -m unittest discover -s tests
```

## 📂 ディレクトリ構造

get_stakeholder_data/
├── get_stakeholder_data/
│   ├── parser/               # XBRLデータの解析ロジック
│   ├── services/             # API呼び出しやユーティリティ
│   ├── models/               # データベースモデル
│   ├── domain/               # ドメインロジック
│   ├── interface/            # データベース接続
│   └── main.py               # メインエントリポイント
├── tests/                    # テストコード
├── .env.example              # 環境変数のテンプレート
├── .gitignore                # Git管理対象外ファイル
├── requirements.txt          # 必要なライブラリ
└── [README.md](http://_vscodecontentref_/1)                 # このファイル

## 🛡️ 注意事項

- .env ファイルには秘匿情報（APIキーなど）を含めるため、絶対に公開しないでください。
- Gemini APIの利用制限に注意してください。制限に達した場合、プログラムは自動的に終了します。
