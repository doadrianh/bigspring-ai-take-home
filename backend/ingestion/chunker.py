import json
from pathlib import Path
from typing import Any


def chunk_pdf_asset(data: list[dict], asset_id: str, company_id: str, file_name: str) -> list[dict]:
    chunks = []
    for page in data:
        page_num = page.get("page", 0)
        # Full page text as a chunk
        if page.get("text"):
            chunks.append({
                "text": page["text"],
                "metadata": {
                    "asset_id": asset_id, "company_id": company_id,
                    "source_file": file_name, "page": page_num,
                    "chunk_type": "page_text",
                },
            })
        # Each table as a separate chunk for precise retrieval
        for table in page.get("tables", []):
            table_text = format_table(table)
            chunks.append({
                "text": table_text,
                "metadata": {
                    "asset_id": asset_id, "company_id": company_id,
                    "source_file": file_name, "page": page_num,
                    "chunk_type": "table", "table_id": table.get("id", ""),
                    "table_title": table.get("title", ""),
                },
            })
    return chunks


def format_table(table: dict) -> str:
    title = table.get("title", "")
    headers = table.get("headers", [])
    rows = table.get("rows", [])
    lines = [f"Table: {title}"]
    if headers:
        lines.append(" | ".join(headers))
        lines.append("-" * 40)
    for row in rows:
        lines.append(" | ".join(str(c) for c in row))
    return "\n".join(lines)


def chunk_video_asset(data: dict, asset_id: str, company_id: str, file_name: str) -> list[dict]:
    chunks = []
    # Full transcript as one chunk
    if data.get("full_transcript"):
        chunks.append({
            "text": data["full_transcript"],
            "metadata": {
                "asset_id": asset_id, "company_id": company_id,
                "source_file": file_name, "chunk_type": "full_transcript",
            },
        })
    # Each segment as a chunk
    for seg in data.get("segments", []):
        chunks.append({
            "text": seg["text"],
            "metadata": {
                "asset_id": asset_id, "company_id": company_id,
                "source_file": file_name, "chunk_type": "segment",
                "start": seg.get("start", ""), "end": seg.get("end", ""),
                "speaker": seg.get("speaker", ""),
            },
        })
    return chunks


def chunk_image_asset(data: dict, asset_id: str, company_id: str, file_name: str) -> list[dict]:
    parts = []
    if data.get("alt_text"):
        parts.append(data["alt_text"])
    if data.get("ocr_text"):
        parts.append(data["ocr_text"])
    for elem in data.get("visual_elements", []):
        parts.append(f"{elem.get('label', '')}: {elem.get('description', '')}")
    text = "\n".join(parts)
    return [{
        "text": text,
        "metadata": {
            "asset_id": asset_id, "company_id": company_id,
            "source_file": file_name, "chunk_type": "image_description",
        },
    }] if text.strip() else []


def chunk_submission_asset(data: dict, asset_id: str, company_id: str, user_id: str,
                           submission_id: str, file_name: str) -> list[dict]:
    chunks = []
    if data.get("full_transcript"):
        chunks.append({
            "text": data["full_transcript"],
            "metadata": {
                "asset_id": asset_id, "company_id": company_id,
                "user_id": user_id, "submission_id": submission_id,
                "source_file": file_name, "chunk_type": "submission_transcript",
            },
        })
    for seg in data.get("segments", []):
        chunks.append({
            "text": seg["text"],
            "metadata": {
                "asset_id": asset_id, "company_id": company_id,
                "user_id": user_id, "submission_id": submission_id,
                "source_file": file_name, "chunk_type": "submission_segment",
                "start": seg.get("start", ""), "end": seg.get("end", ""),
                "speaker": seg.get("speaker", ""),
            },
        })
    return chunks


def chunk_asset(asset_type: str, data: Any, asset_id: str, company_id: str,
                file_name: str, user_id: str = "", submission_id: str = "") -> list[dict]:
    if user_id:
        return chunk_submission_asset(data, asset_id, company_id, user_id, submission_id, file_name)
    if asset_type == "pdf":
        return chunk_pdf_asset(data, asset_id, company_id, file_name)
    elif asset_type in ("video", "audio"):
        return chunk_video_asset(data, asset_id, company_id, file_name)
    elif asset_type == "image":
        return chunk_image_asset(data, asset_id, company_id, file_name)
    # Text submissions without user_id context - treat as video/audio
    return chunk_video_asset(data, asset_id, company_id, file_name)
