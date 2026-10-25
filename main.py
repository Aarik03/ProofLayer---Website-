from __future__ import annotations

import os
import sqlite3
from contextlib import asynccontextmanager
from io import BytesIO

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image, UnidentifiedImageError

from database import (
    db_health,
    get_dashboard_stats,
    get_verification_by_id,
    init_db,
    insert_verification,
)
from models import (
    HFServiceError,
    compute_sha256,
    generate_verification_id,
    hf_image_score,
    hf_text_score,
    risk_level_from_score,
    utc_now_iso,
)

load_dotenv()

IMAGE_MODEL_ENDPOINT = os.getenv(
    "HF_IMAGE_MODEL_ENDPOINT",
    "https://api-inference.huggingface.co/models/umm-maybe/AI-image-detector",
)
TEXT_MODEL_ENDPOINT = os.getenv(
    "HF_TEXT_MODEL_ENDPOINT",
    "https://api-inference.huggingface.co/models/roberta-base-openai-detector",
)
MAX_IMAGE_BYTES = 10 * 1024 * 1024
MAX_TEXT_CHARS = 20000


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="ProofLayer API", version="0.4.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(_request, _exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again."},
    )


def _insert_with_unique_id(
    *,
    content_type: str,
    score: float,
    risk_level: str,
    content_hash: str,
    timestamp: str,
    metadata: dict,
) -> str:
    for _ in range(7):
        verification_id = generate_verification_id()
        try:
            insert_verification(
                verification_id=verification_id,
                content_type=content_type,
                score=score,
                risk_level=risk_level,
                content_hash=content_hash,
                timestamp=timestamp,
                metadata=metadata,
            )
            return verification_id
        except sqlite3.IntegrityError:
            continue

    raise HTTPException(status_code=500, detail="Could not generate a unique verification ID.")


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "ProofLayer API running"}


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "database": db_health(),
        "has_hf_token": bool(os.getenv("HF_TOKEN")),
        "image_endpoint": IMAGE_MODEL_ENDPOINT,
        "text_endpoint": TEXT_MODEL_ENDPOINT,
    }


@app.post("/verify-image")
async def verify_image(file: UploadFile = File(...)) -> dict:
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        raise HTTPException(status_code=500, detail="HF_TOKEN is not configured.")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(file_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=400, detail="Image too large. Max size is 10MB.")

    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed.")

    try:
        with Image.open(BytesIO(file_bytes)) as img:
            width, height = img.size
            image_format = img.format
    except UnidentifiedImageError as exc:
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid image.") from exc

    try:
        model_result = hf_image_score(file_bytes, hf_token, IMAGE_MODEL_ENDPOINT)
    except HFServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    score = float(model_result["ai_probability"])
    risk_level = risk_level_from_score(score)
    content_hash = compute_sha256(file_bytes)
    timestamp = utc_now_iso()

    metadata = {
        "filename": file.filename,
        "content_type": file.content_type,
        "image_width": width,
        "image_height": height,
        "image_format": image_format,
        "hf_model_endpoint": IMAGE_MODEL_ENDPOINT,
        "hf_raw_response": model_result["raw_response"],
    }

    verification_id = _insert_with_unique_id(
        content_type="image",
        score=score,
        risk_level=risk_level,
        content_hash=content_hash,
        timestamp=timestamp,
        metadata=metadata,
    )

    return {
        "verification_id": verification_id,
        "type": "image",
        "score": round(score, 4),
        "risk_level": risk_level,
        "hash": content_hash,
        "timestamp": timestamp,
        "metadata": {
            "filename": file.filename,
            "image_width": width,
            "image_height": height,
            "image_format": image_format,
        },
    }


@app.post("/verify-text")
def verify_text(text: str = Form(...)) -> dict:
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        raise HTTPException(status_code=500, detail="HF_TOKEN is not configured.")

    normalized = text.strip()
    if not normalized:
        raise HTTPException(status_code=400, detail="Text input cannot be empty.")
    if len(normalized) > MAX_TEXT_CHARS:
        raise HTTPException(status_code=400, detail="Text input is too long (max 20,000 chars).")

    try:
        model_result = hf_text_score(normalized, hf_token, TEXT_MODEL_ENDPOINT)
    except HFServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    score = float(model_result["ai_probability"])
    risk_level = risk_level_from_score(score)
    content_hash = compute_sha256(normalized.encode("utf-8"))
    timestamp = utc_now_iso()

    metadata = {
        "text_length": len(normalized),
        "hf_model_endpoint": TEXT_MODEL_ENDPOINT,
        "hf_raw_response": model_result["raw_response"],
    }

    verification_id = _insert_with_unique_id(
        content_type="text",
        score=score,
        risk_level=risk_level,
        content_hash=content_hash,
        timestamp=timestamp,
        metadata=metadata,
    )

    return {
        "verification_id": verification_id,
        "type": "text",
        "score": round(score, 4),
        "risk_level": risk_level,
        "hash": content_hash,
        "timestamp": timestamp,
        "metadata": {
            "text_length": len(normalized),
            "human_likelihood": round(1 - score, 4),
            "perplexity_proxy": round(score * 100, 2),
        },
    }


@app.get("/report/{verification_id}")
def get_report(verification_id: str) -> dict:
    record = get_verification_by_id(verification_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Verification ID not found.")
    return record


@app.get("/dashboard-stats")
def dashboard_stats() -> dict:
    return get_dashboard_stats()
