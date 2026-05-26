# utils/translator.py
import requests

VAK_API_URL = "http://localhost:8000"
VAK_API_KEY = "vak-SEHY3BBOJkduPvgqjBzK1JUM6jf7zKaW"
HEADERS     = {"X-API-Key": VAK_API_KEY}

def translate(text: str, tgt_lang: str, src_lang="eng_Latn") -> str:
    res = requests.post(
        f"{VAK_API_URL}/translate",
        headers=HEADERS,
        json={"text": text, "src_lang": src_lang, "tgt_lang": tgt_lang},
    )
    return res.json()["translation"]

def translate_batch(texts: list, tgt_lang: str, src_lang="eng_Latn") -> list:
    res = requests.post(
        f"{VAK_API_URL}/translate/batch",
        headers=HEADERS,
        json={"texts": texts, "src_lang": src_lang, "tgt_lang": tgt_lang},
    )
    return res.json()["translations"]