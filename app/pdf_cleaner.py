import io
import re
from collections import Counter
from typing import Iterable, List


def _normalize_line(line: str) -> str:
    return re.sub(r"\s+", " ", line.strip().lower())


def _is_page_number(line: str) -> bool:
    patterns = [
        r"^\d+$",
        r"^p\.?\s*\d+$",
        r"^page\s+\d+(\s+of\s+\d+)?$",
        r"^\d+\s*/\s*\d+$",
    ]
    normalized = _normalize_line(line)
    return any(re.match(p, normalized) for p in patterns)


def _get_repeated_margin_lines(pages_lines: Iterable[List[str]]) -> set[str]:
    first_lines = []
    last_lines = []

    for lines in pages_lines:
        clean = [l.strip() for l in lines if l.strip()]
        if not clean:
            continue
        first_lines.append(_normalize_line(clean[0]))
        last_lines.append(_normalize_line(clean[-1]))

    repeated = set()
    for bucket in (first_lines, last_lines):
        counts = Counter(bucket)
        for line, count in counts.items():
            if line and count >= 2:
                repeated.add(line)

    return repeated


def _basic_cleanup(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _ai_refine_text(text: str, openai_api_key: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=openai_api_key)
    prompt = (
        "Limpia el siguiente texto extraído de PDF para lectura en voz alta. "
        "Elimina encabezados, pies de página, numeración, saltos raros y fragmentos repetidos. "
        "Conserva el contenido semántico y devuelve solo texto limpio en español.\n\n"
        f"TEXTO:\n{text[:12000]}"
    )

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        temperature=0.2,
    )
    return response.output_text.strip()


def clean_pdf_text(raw_pdf: bytes, use_ai: bool = False, openai_api_key: str | None = None) -> str:
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(raw_pdf))
    pages_lines: List[List[str]] = []

    for page in reader.pages:
        extracted = page.extract_text() or ""
        lines = extracted.splitlines()
        pages_lines.append(lines)

    repeated_margin_lines = _get_repeated_margin_lines(pages_lines)

    filtered_lines: List[str] = []
    for lines in pages_lines:
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            normalized = _normalize_line(stripped)
            if normalized in repeated_margin_lines:
                continue

            if _is_page_number(stripped):
                continue

            filtered_lines.append(stripped)

    merged = "\n".join(filtered_lines)
    cleaned = _basic_cleanup(merged)

    if use_ai and openai_api_key and cleaned:
        try:
            return _ai_refine_text(cleaned, openai_api_key)
        except Exception:
            return cleaned

    return cleaned
