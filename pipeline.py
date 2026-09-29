import pandas as pd
import os
import requests
from dotenv import load_dotenv

#API環境設定読み込み
load_dotenv()

#csvの読み込み関数
def load_prompts(file_path):
    df = pd.read_csv(file_path)
    return df

# 必須カラムのチェック
def validate_prompts(df):
    required_columns = ["id", "prompt"]
    is_valid = True

    for column in required_columns:
        if column not in df.columns:
            print(f"必須列がありません: {column}")
            is_valid = False

    # 必須列が欠けているなら、ここで終了
    if not is_valid:
        return False

    if df["prompt"].isna().sum() > 0:
        missing_ids = df.loc[
            df["prompt"].isna(),
            "id"
        ].tolist()

        print(f"プロンプトに空白があります：{df['prompt'].isna().sum()}件")
        print(f"対象id：{missing_ids}")

        is_valid = False

    if is_valid:
        print("入力データOK")

    return is_valid

#プロンプトをAPIに送信する
def send_prompt(prompt):

    api_url = os.getenv("LLM_API_URL")
    model = os.getenv("LLM_MODEL")

    if not api_url or not model:
        print("API設定がありません")
        return None

    data = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    try:
        response = requests.post(
            api_url,
            json=data,
            timeout=(10, 180)
        )
    except requests.RequestException as e:
        print(f"API通信に失敗しました:{e}")
        return None
    else:
        if response.status_code == 200:
            try:
                result = response.json()
            except requests.exceptions.JSONDecodeError as e:
                print(f"JSON解析エラー:{e}")
                return None
            else:
                return result["choices"][0]["message"]["content"]
        else:
            print(f"APIステータスコードエラー:{response.status_code}")
            return None