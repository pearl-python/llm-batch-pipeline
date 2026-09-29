from pipeline import (
        load_prompts,
        validate_prompts,
        send_prompt,
        create_result_dataframe,
        save_csv
    )
#プロンプトcsvをロード
df = load_prompts("sample/prompts.csv")
#必須カラムのチェック
if validate_prompts(df):
    results = []
    #csvからプロンプトを取得する
    for _, row in df.iterrows():
        prompt_id = row["id"]
        prompt = row["prompt"]
        answer = send_prompt(prompt)
        results.append({
            "id": prompt_id,
            "prompt": prompt,
            "answer": answer
        })

    result_df = create_result_dataframe(results)

    save_csv(result_df, "output/results.csv")



