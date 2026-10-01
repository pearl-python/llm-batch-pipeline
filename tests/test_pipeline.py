import pandas as pd

from pipeline import (
    load_prompts,
    validate_prompts,
    create_result_dataframe,
    send_prompt,
    save_csv
)

import pipeline
import requests


def test_validate_prompts_success():
    df = pd.DataFrame({
        "id": [1, 2],
        "prompt": ["Pythonとは？", "pandasとは？"]
    })

    result = validate_prompts(df)

    assert result is True

def test_validate_prompts_missing_prompt_column():
    df = pd.DataFrame({
        "id": [1, 2]
    })

    result = validate_prompts(df)

    assert result is False

def test_validate_prompts_missing_value():
    df = pd.DataFrame({
        "id": [1, 2, 3],
        "prompt": [
            "Pythonとは？",
            None,
            "pandasとは？"
        ]
    })

    result = validate_prompts(df)

    assert result is False

def test_create_result_dataframe():
    results = [
        {
            "id": 1,
            "prompt": "Pythonとは？",
            "answer": "Pythonは...",
            "status": "success",
            "error": None,
            "elapsed_seconds": 1.23
        },
        {
            "id": 2,
            "prompt": "pandasとは？",
            "answer": None,
            "status": "failed",
            "error": "API error",
            "elapsed_seconds": 0.45
        }
    ]

    df = create_result_dataframe(results)

    assert len(df) == 2
    assert df["id"].tolist() == [1, 2]
    assert df["status"].tolist() == ["success", "failed"]

def test_send_prompt_missing_api_config(monkeypatch):
    monkeypatch.delenv("LLM_API_URL", raising=False)
    monkeypatch.delenv("LLM_MODEL", raising=False)

    answer, status, error = send_prompt("Pythonとは？")

    assert answer is None
    assert status == "failed"
    assert error == "API設定がありません"

class FakeResponse:
    status_code = 200

    def json(self):
        return {
            "choices": [
                {
                    "message": {
                        "content": "これはテスト回答です"
                    }
                }
            ]
        }

def test_send_prompt_success(monkeypatch):
    monkeypatch.setenv("LLM_API_URL", "https://example.com/api")
    monkeypatch.setenv("LLM_MODEL", "test-model")

    def fake_post(url, json, timeout):
        return FakeResponse()

    monkeypatch.setattr(
        pipeline.requests,
        "post",
        fake_post
    )

    answer, status, error = send_prompt("Pythonとは？")

    assert answer == "これはテスト回答です"
    assert status == "success"
    assert error is None

class FakeErrorResponse:
    status_code = 500

def test_send_prompt_http_error(monkeypatch):
    monkeypatch.setenv("LLM_API_URL", "https://example.com/api")
    monkeypatch.setenv("LLM_MODEL", "test-model")

    def fake_post(url, json, timeout):
        return FakeErrorResponse()

    monkeypatch.setattr(
        pipeline.requests,
        "post",
        fake_post
    )

    answer, status, error = send_prompt("Pythonとは？")

    assert answer is None
    assert status == "failed"
    assert error == "APIステータスコードエラー:500"

def test_send_prompt_request_exception(monkeypatch):
    monkeypatch.setenv("LLM_API_URL", "https://example.com/api")
    monkeypatch.setenv("LLM_MODEL", "test-model")

    def fake_post(url, json, timeout):
        raise requests.RequestException("接続失敗")

    monkeypatch.setattr(
        pipeline.requests,
        "post",
        fake_post
    )

    answer, status, error = send_prompt("Pythonとは？")

    assert answer is None
    assert status == "failed"
    assert error == "API通信に失敗しました:接続失敗"

class FakeInvalidJsonResponse:
    status_code = 200

    def json(self):
        raise requests.exceptions.JSONDecodeError(
            "JSON解析失敗",
            "",
            0
        )

def test_send_prompt_json_decode_error(monkeypatch):
    monkeypatch.setenv("LLM_API_URL", "https://example.com/api")
    monkeypatch.setenv("LLM_MODEL", "test-model")

    def fake_post(url, json, timeout):
        return FakeInvalidJsonResponse()

    monkeypatch.setattr(
        pipeline.requests,
        "post",
        fake_post
    )

    answer, status, error = send_prompt("Pythonとは？")

    assert answer is None
    assert status == "failed"
    assert "JSON解析エラー:" in error

def test_save_csv(tmp_path):
    df = pd.DataFrame({
        "id": [1, 2],
        "status": ["success", "failed"]
    })

    file_path = tmp_path / "results.csv"

    save_csv(df, file_path)

    loaded_df = pd.read_csv(file_path)

    assert len(loaded_df) == 2
    assert loaded_df["id"].tolist() == [1, 2]
    assert loaded_df["status"].tolist() == ["success", "failed"]

def test_load_prompts(tmp_path):
    file_path = tmp_path / "prompts.csv"

    test_df = pd.DataFrame({
        "id": [1, 2],
        "prompt": ["Pythonとは？", "pandasとは？"]
    })

    test_df.to_csv(file_path, index=False)

    loaded_df = load_prompts(file_path)

    assert len(loaded_df) == 2
    assert loaded_df["id"].tolist() == [1, 2]
    assert loaded_df["prompt"].tolist() == [
        "Pythonとは？",
        "pandasとは？"
    ]