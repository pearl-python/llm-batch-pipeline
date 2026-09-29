from pipeline import (
        load_prompts,
        validate_prompts,
        send_prompt
    )
#プロンプトcsvをロード
df = load_prompts("sample/prompts.csv")
#必須カラムのチェック
if validate_prompts(df):
    #csvからプロンプトを取得する
    prompt = df["prompt"].iloc[0]
    answer = send_prompt(prompt)
    print(answer)


