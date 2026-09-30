from pipeline import (
        load_prompts,
        validate_prompts,
        send_prompt,
        create_result_dataframe,
        save_csv
    )
import time
import logging

#ログ管理用
logging.basicConfig(
    filename="output/app.log",
    level=logging.INFO,
    encoding="utf-8",
    format="%(asctime)s %(levelname)s %(message)s"
)

#プロンプトcsvをロード
df = load_prompts("sample/prompts.csv")
#必須カラムのチェック
if validate_prompts(df):
    results = []
    success_count = 0
    failed_count = 0
    logging.info("batch start")
    #csvからプロンプトを取得する
    for _, row in df.iterrows():
        prompt_id = row["id"]
        prompt = row["prompt"]
        start_time = time.perf_counter()
        answer, status, error = send_prompt(prompt)
        end_time = time.perf_counter()
        elapsed_seconds = round(end_time - start_time, 2)

        if status == "success":
            logging.info(
                f"id={prompt_id} status={status} elapsed={elapsed_seconds:.2f}"
            )
            success_count += 1
        else:
            logging.error(
                f"id={prompt_id} status={status} "
                f"elapsed={elapsed_seconds:.2f} error={error}"
            )
            failed_count += 1

        results.append({
            "id": prompt_id,
            "prompt": prompt,
            "answer": answer,
            "status": status,
            "error": error,
            "elapsed_seconds": elapsed_seconds
        })

    result_df = create_result_dataframe(results)
    save_csv(result_df, "output/results.csv")

    logging.info(
        f"batch end total={len(results)} "
        f"success={success_count} failed={failed_count}"
    )