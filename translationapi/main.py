"""
Vak Public Translation API
==========================
A production-ready translation API that any website in the world can use.
Websites send their page content and get it back in the user's language.

Install:
    pip install -r requirements.txt

Run:
    uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2

Swagger docs:
    http://localhost:8000/docs
"""

import os
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HUGGINGFACE_HUB_LOCAL_DIR_USE_SYMLINKS"] = "False"

import time
import hashlib
import logging
import secrets
from typing import Optional

import ctranslate2
from fastapi import FastAPI, HTTPException, Request, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from huggingface_hub import snapshot_download
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from transformers import NllbTokenizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Rate limiter setup
# ---------------------------------------------------------------------------

limiter = Limiter(key_func=get_remote_address)

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Vak Translation API",
    description=(
        "A public translation API for websites. "
        "Integrate a language switcher on any website and translate your content "
        "into 200+ languages in real time."
    ),
    version="1.0.0",
    contact={"name": "Vak API Support", "email": "support@example.com"},
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Allow ALL origins — any website can call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# In-memory stores (replace with Redis + a real DB in production)
# ---------------------------------------------------------------------------

# API keys store: { api_key: { "owner": str, "created_at": float, "active": bool } }
API_KEYS: dict = {}

# Translation cache: { cache_key: translated_text }
TRANSLATION_CACHE: dict = {}

# ---------------------------------------------------------------------------
# Model — loaded once at startup
# ---------------------------------------------------------------------------

MODEL_ID = "shunyalabs/vak-translate-1.3b-ct2"
tokenizer: Optional[NllbTokenizer] = None
translator: Optional[ctranslate2.Translator] = None


@app.on_event("startup")
async def load_model():
    global tokenizer, translator

    # Create a default demo API key on startup
    demo_key = "demo-key-12345"
    API_KEYS[demo_key] = {"owner": "demo", "created_at": time.time(), "active": True}
    logger.info("Demo API key created: %s", demo_key)

    logger.info("Loading translation model: %s", MODEL_ID)
    model_dir = snapshot_download(MODEL_ID)
    tokenizer = NllbTokenizer.from_pretrained(MODEL_ID)
    device = "cuda" if ctranslate2.get_cuda_device_count() > 0 else "cpu"
    logger.info("Using device: %s", device)
    translator = ctranslate2.Translator(model_dir, device=device)
    logger.info("Model ready.")


# ---------------------------------------------------------------------------
# API Key auth — shows 🔒 Authorize button in Swagger UI
# ---------------------------------------------------------------------------

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_api_key(
    request: Request,
    api_key_header_val: str = Security(api_key_header),
) -> str:
    """Read API key from header X-API-Key or query param ?api_key="""
    key = api_key_header_val or request.query_params.get("api_key")
    if not key:
        raise HTTPException(
            status_code=401,
            detail="Missing API key. Click 🔒 Authorize in Swagger UI and enter your key, or pass header X-API-Key.",
        )
    entry = API_KEYS.get(key)
    if not entry or not entry["active"]:
        raise HTTPException(status_code=403, detail="Invalid or inactive API key.")
    return key


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class TranslateOneRequest(BaseModel):
    text: str = Field(..., description="Text to translate", example="Welcome to our website!")
    src_lang: str = Field("eng_Latn", description="Source language NLLB code")
    tgt_lang: str = Field(..., description="Target language NLLB code", example="rus_Cyrl")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Welcome to our website!",
                "src_lang": "eng_Latn",
                "tgt_lang": "rus_Cyrl",
            }
        }


class TranslateOneResponse(BaseModel):
    translation: str
    src_lang: str
    tgt_lang: str
    cached: bool = False


class TranslateBatchRequest(BaseModel):
    texts: list[str] = Field(..., description="List of texts to translate")
    src_lang: str = Field("eng_Latn", description="Source language NLLB code")
    tgt_lang: str = Field(..., description="Target language NLLB code", example="rus_Cyrl")
    beam_size: int = Field(4, ge=1, le=10)
    max_decoding_length: int = Field(256, ge=1, le=512)

    class Config:
        json_schema_extra = {
            "example": {
                "texts": ["Home", "About Us", "Contact", "Buy Now"],
                "src_lang": "eng_Latn",
                "tgt_lang": "hin_Deva",
            }
        }


class TranslateBatchResponse(BaseModel):
    translations: list[str]
    src_lang: str
    tgt_lang: str
    count: int


class RegisterRequest(BaseModel):
    owner: str = Field(..., description="Your name or website domain", example="myshop.com")


class RegisterResponse(BaseModel):
    api_key: str
    owner: str
    message: str


# ---------------------------------------------------------------------------
# Core translation function
# ---------------------------------------------------------------------------

def _run_translation(
    texts: list[str],
    tgt_lang: str,
    beam_size: int = 4,
    max_decoding_length: int = 256,
) -> list[str]:
    if translator is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet. Try again shortly.")

    all_src_tokens = [
        tokenizer.convert_ids_to_tokens(tokenizer(t)["input_ids"])
        for t in texts
    ]

    results = translator.translate_batch(
        all_src_tokens,
        target_prefix=[[tgt_lang]] * len(texts),
        beam_size=beam_size,
        max_decoding_length=max_decoding_length,
    )

    translations = []
    for result in results:
        ids = tokenizer.convert_tokens_to_ids(result.hypotheses[0])
        translations.append(tokenizer.decode(ids, skip_special_tokens=True))

    return translations


def _cache_key(text: str, src_lang: str, tgt_lang: str) -> str:
    raw = f"{src_lang}|{tgt_lang}|{text}"
    return hashlib.md5(raw.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/", tags=["Info"])
def root():
    return {
        "name": "Vak Translation API",
        "description": "Translate website content into 200+ languages",
        "docs": "/docs",
        "register": "POST /register — get a free API key",
        "endpoints": {
            "single": "POST /translate",
            "batch": "POST /translate/batch",
            "languages": "GET /languages",
            "health": "GET /health",
        },
    }


@app.get("/health", tags=["Info"])
def health():
    """Check if the API and model are ready."""
    return {
        "status": "ok",
        "model_loaded": translator is not None,
        "cached_translations": len(TRANSLATION_CACHE),
    }


@app.post("/register", response_model=RegisterResponse, tags=["Auth"])
def register(req: RegisterRequest):
    """
    Register your website and get a free API key.
    Use this key in every translation request via the X-API-Key header.
    """
    new_key = "vak-" + secrets.token_urlsafe(24)
    API_KEYS[new_key] = {
        "owner": req.owner,
        "created_at": time.time(),
        "active": True,
    }
    logger.info("New API key issued for: %s", req.owner)
    return RegisterResponse(
        api_key=new_key,
        owner=req.owner,
        message="Save this key — it won't be shown again. Pass it as header X-API-Key.",
    )


@app.post("/translate", response_model=TranslateOneResponse, tags=["Translation"])
@limiter.limit("60/minute")
def translate_one(
    request: Request,
    req: TranslateOneRequest,
    api_key: str = Depends(get_api_key),
):
    """
    Translate a **single** piece of text.

    Ideal for translating individual UI elements (buttons, headings, paragraphs)
    when a user switches the language on your website.

    Results are cached — repeated requests for the same text return instantly.
    """
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="'text' must not be empty.")

    # Check cache
    ck = _cache_key(req.text, req.src_lang, req.tgt_lang)
    if ck in TRANSLATION_CACHE:
        return TranslateOneResponse(
            translation=TRANSLATION_CACHE[ck],
            src_lang=req.src_lang,
            tgt_lang=req.tgt_lang,
            cached=True,
        )

    translated = _run_translation([req.text], req.tgt_lang)[0]
    TRANSLATION_CACHE[ck] = translated

    return TranslateOneResponse(
        translation=translated,
        src_lang=req.src_lang,
        tgt_lang=req.tgt_lang,
        cached=False,
    )


@app.post("/translate/batch", response_model=TranslateBatchResponse, tags=["Translation"])
@limiter.limit("20/minute")
def translate_batch(
    request: Request,
    req: TranslateBatchRequest,
    api_key: str = Depends(get_api_key),
):
    """
    Translate a **batch** of texts in one call.

    Best used when a user first opens your website — send all visible
    text elements at once (nav links, headings, buttons, paragraphs) and
    get all translations back together.

    Max 100 texts per request.
    """
    if not req.texts:
        raise HTTPException(status_code=400, detail="'texts' must not be empty.")
    if len(req.texts) > 100:
        raise HTTPException(status_code=400, detail="Max 100 texts per batch request.")

    # Split into cached vs needs-translation
    results = [None] * len(req.texts)
    to_translate_indices = []
    to_translate_texts = []

    for i, text in enumerate(req.texts):
        ck = _cache_key(text, req.src_lang, req.tgt_lang)
        if ck in TRANSLATION_CACHE:
            results[i] = TRANSLATION_CACHE[ck]
        else:
            to_translate_indices.append(i)
            to_translate_texts.append(text)

    # Translate only what's not cached
    if to_translate_texts:
        translated = _run_translation(
            to_translate_texts,
            req.tgt_lang,
            req.beam_size,
            req.max_decoding_length,
        )
        for idx, text, translation in zip(to_translate_indices, to_translate_texts, translated):
            ck = _cache_key(text, req.src_lang, req.tgt_lang)
            TRANSLATION_CACHE[ck] = translation
            results[idx] = translation

    return TranslateBatchResponse(
        translations=results,
        src_lang=req.src_lang,
        tgt_lang=req.tgt_lang,
        count=len(results),
    )


@app.get("/languages", tags=["Info"])
def supported_languages():
    """
    Returns all supported NLLB language codes.
    Use these codes as src_lang / tgt_lang in translation requests.
    """
    return {
        "total": 28,
        "languages": [
            {"code": "eng_Latn", "name": "English",                  "script": "Latin"},
            {"code": "hin_Deva", "name": "Hindi",                    "script": "Devanagari"},
            {"code": "rus_Cyrl", "name": "Russian",                  "script": "Cyrillic"},
            {"code": "fra_Latn", "name": "French",                   "script": "Latin"},
            {"code": "deu_Latn", "name": "German",                   "script": "Latin"},
            {"code": "spa_Latn", "name": "Spanish",                  "script": "Latin"},
            {"code": "por_Latn", "name": "Portuguese",               "script": "Latin"},
            {"code": "ita_Latn", "name": "Italian",                  "script": "Latin"},
            {"code": "nld_Latn", "name": "Dutch",                    "script": "Latin"},
            {"code": "pol_Latn", "name": "Polish",                   "script": "Latin"},
            {"code": "tur_Latn", "name": "Turkish",                  "script": "Latin"},
            {"code": "zho_Hans", "name": "Chinese (Simplified)",     "script": "Han"},
            {"code": "zho_Hant", "name": "Chinese (Traditional)",    "script": "Han"},
            {"code": "jpn_Jpan", "name": "Japanese",                 "script": "Japanese"},
            {"code": "kor_Hang", "name": "Korean",                   "script": "Hangul"},
            {"code": "ara_Arab", "name": "Arabic",                   "script": "Arabic"},
            {"code": "fas_Arab", "name": "Persian (Farsi)",          "script": "Arabic"},
            {"code": "urd_Arab", "name": "Urdu",                     "script": "Arabic"},
            {"code": "ben_Beng", "name": "Bengali",                  "script": "Bengali"},
            {"code": "pan_Guru", "name": "Punjabi",                  "script": "Gurmukhi"},
            {"code": "guj_Gujr", "name": "Gujarati",                 "script": "Gujarati"},
            {"code": "mar_Deva", "name": "Marathi",                  "script": "Devanagari"},
            {"code": "tam_Taml", "name": "Tamil",                    "script": "Tamil"},
            {"code": "tel_Telu", "name": "Telugu",                   "script": "Telugu"},
            {"code": "kan_Knda", "name": "Kannada",                  "script": "Kannada"},
            {"code": "mal_Mlym", "name": "Malayalam",                "script": "Malayalam"},
            {"code": "tha_Thai", "name": "Thai",                     "script": "Thai"},
            {"code": "vie_Latn", "name": "Vietnamese",               "script": "Latin"},
        ],
    }