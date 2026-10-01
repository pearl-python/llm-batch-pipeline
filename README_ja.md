# LLM Batch Pipeline

CSVに並んだ複数のプロンプトをLLM APIへ順番に送信し、回答・成功／失敗・エラー内容・処理時間を記録してCSVへ保存するPython製バッチ処理ツールです。

## 主な機能

- pandasによるCSV読み込み
- 必須列・欠損値チェック
- 複数プロンプトの逐次API送信
- 環境変数によるAPI設定
- 通信エラー、HTTPエラー、JSON解析エラー処理
- success / failed の記録
- エラー内容の記録
- 1件ごとの処理時間計測
- 結果CSV出力
- INFO / ERRORログ
- pytest / mockによるAPIテスト

## 処理フロー

```text
prompts.csv
    ↓
load_prompts()
    ↓
validate_prompts()
    ↓
1件ずつsend_prompt()
    ↓
answer / status / error
    ↓
処理時間計測
    ↓
DataFrame化
    ↓
output/results.csv
    ↓
output/app.log
```

## ディレクトリ構成

```text
llm-batch-pipeline/
├─ main.py
├─ pipeline.py
├─ test_pipeline.py
├─ requirements.txt
├─ .env.example
├─ .gitignore
├─ README.md
├─ README_ja.md
├─ sample/
│  └─ prompts.csv
└─ output/
   └─ .gitkeep
```

`output/` 内の生成ファイルはGit管理対象外です。

## 入力CSV

例：

```csv
id,prompt
1,Pythonとは何ですか？
2,pandasの特徴を3つ説明してください
3,CSVとJSONの違いを簡潔に説明してください
```

必須列：

- `id`
- `prompt`

必須列がない場合や、`prompt` に欠損値がある場合はAPI処理へ進む前に失敗します。

## 環境変数

`.env.example` をコピーして `.env` を作成します。

```env
LLM_API_URL=https://your-api.example.com/v1/chat/completions
LLM_MODEL=your-model-name
```

`.env` はGit管理対象外です。

現在の実装では、APIレスポンスが次の形式であることを前提にしています。

```json
{
  "choices": [
    {
      "message": {
        "content": "response text"
      }
    }
  ]
}
```

## セットアップ

```powershell
git clone https://github.com/pearl-python/llm-batch-pipeline.git
cd llm-batch-pipeline

python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

`.env` に使用するAPI URLとモデル名を設定します。

## 実行

```powershell
python main.py
```

出力：

- `output/results.csv`
- `output/app.log`

## 出力CSV

主な列：

```text
id
prompt
answer
status
error
elapsed_seconds
```

`status` は `success` または `failed` です。

成功時は `error` が空になります。  
失敗時は `answer` が空になり、`error` に失敗理由を保存します。

## logging

ログには以下を記録します。

- batch start
- 各promptの成功／失敗
- 各promptの処理時間
- エラー内容
- 全処理件数
- 成功件数
- 失敗件数
- batch end

例：

```text
2026-10-01 17:10:00 INFO batch start
2026-10-01 17:11:32 INFO id=1 status=success elapsed=92.15
2026-10-01 17:11:33 ERROR id=2 status=failed elapsed=0.21 error=...
2026-10-01 17:11:33 INFO batch end total=2 success=1 failed=1
```

## pytest

```powershell
python -m pytest -v
```

現在は **11個のテスト** を実装しています。

- 正常な入力
- 必須列不足
- prompt欠損
- resultsからDataFrame作成
- API設定不足
- API正常応答
- HTTPエラー
- 通信例外
- JSON解析エラー
- CSV保存
- CSV読み込み

APIテストでは実際のLLM APIを呼ばず、pytestの `monkeypatch` と偽レスポンスを利用します。

使用している主なpytest機能：

- `monkeypatch.setenv()`
- `monkeypatch.delenv()`
- `monkeypatch.setattr()`
- `tmp_path`

これにより、外部API・本番環境変数・本番CSVを壊さず、高速にテストできます。

## 設計上のポイント

### API設定をソースコードへ直接書かない
API URLとモデル名を環境変数へ分離しています。

### CSVとログの役割を分ける
`results.csv` は構造化された処理結果、`app.log` は実行履歴・障害調査用です。

### 1件失敗しても結果を残せる
`send_prompt()` は以下を返します。

```text
answer, status, error
```

各promptについて成功／失敗と原因を個別に記録できます。

### APIテストではmockを使う
正常応答、HTTP 500、通信例外、JSON解析エラーなどを偽レスポンスで再現し、外部サービスに依存しないテストにしています。

## 現在の制約

- API処理は逐次実行
- retry未実装
- rate limit対策未実装
- `choices[0].message.content` 形式を前提
- 入出力パスは現在コード内で固定
- 空白文字だけのpromptは別途検証していない
- logging開始前に`output`ディレクトリが必要

## 今後の改善候補

- retry / backoff
- rate limit対応
- CLI引数
- 入出力パスの設定化
- 空白だけのprompt検証
- 型ヒント
- GitHub Actions / CI
- 必要に応じた並列／非同期処理

## ポートフォリオ上の位置づけ

この作品では、

```text
CSV / pandas
↓
入力検証
↓
LLM API
↓
例外処理
↓
複数件バッチ処理
↓
結果CSV
↓
logging
↓
pytest / mock
```

までを1本のツールとして組み合わせています。

Python基礎から一歩進み、外部APIを利用した自動処理を「入力・実行・エラー管理・記録・テスト」まで含めて構築できることを示すためのポートフォリオ作品です。
