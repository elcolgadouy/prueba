from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from typing import Iterable

PAGE_SEPARATOR_PATTERN = re.compile(r"(?im)^\s*---\s*p[aá]gina\s+\d+\s*---\s*$")


@dataclass
class ProtocolResult:
    title: str
    start_page: int
    total_pages: int
    repeated_lines: list[str]
    removed_line_count: int
    tts_text: str
    protocol: list[str]


def normalize_line(line: str) -> str:
    return re.sub(r"\s+", " ", line.strip().lower())


def split_pages(raw_text: str) -> list[list[str]]:
    if "\f" in raw_text:
        return [page.splitlines() for page in raw_text.split("\f") if page.strip()]

    chunks = PAGE_SEPARATOR_PATTERN.split(raw_text)
    if len(chunks) > 1:
        return [chunk.splitlines() for chunk in chunks if chunk.strip()]

    return [raw_text.splitlines()]


def detect_repeated_lines(pages: list[list[str]], threshold: float = 0.6) -> set[str]:
    if len(pages) < 2:
        return set()

    counts: Counter[str] = Counter()
    for page in pages:
        unique_lines = {normalize_line(line) for line in page if line.strip()}
        for line in unique_lines:
            if len(line) <= 80:
                counts[line] += 1

    min_count = max(2, int(len(pages) * threshold))
    return {line for line, freq in counts.items() if freq >= min_count}


def is_noise_line(line: str) -> bool:
    stripped = line.strip()
    normalized = normalize_line(line)

    if not stripped:
        return True
    if re.fullmatch(r"\d+", stripped):
        return True
    if re.search(r"isbn|archivo digital|cdd|compilador|autores|coordinaci[oó]n editorial", normalized):
        return True
    if re.search(r"volver al [ií]ndice|ediciones universidad", normalized):
        return True
    return False


def find_title(lines: Iterable[str]) -> str:
    for line in lines:
        if not is_noise_line(line) and len(line.strip()) > 3:
            return line.strip()
    return "Documento sin título"


def find_start_page(pages: list[list[str]], keywords: list[str]) -> int:
    if not keywords:
        return 1

    lowered_keywords = [keyword.lower() for keyword in keywords]
    for index, page in enumerate(pages, start=1):
        page_text = " ".join(page).lower()
        if any(keyword in page_text for keyword in lowered_keywords):
            return index
    return 1


def build_protocol(raw_text: str, keywords: list[str]) -> dict:
    pages = split_pages(raw_text)
    repeated_lines = detect_repeated_lines(pages)
    title = find_title(pages[0])
    start_page = find_start_page(pages, keywords)

    cleaned_lines: list[str] = []
    removed_line_count = 0

    for page_number, page in enumerate(pages, start=1):
        if page_number < start_page:
            removed_line_count += len(page)
            continue

        for line in page:
            normalized = normalize_line(line)
            if normalized in repeated_lines or is_noise_line(line):
                removed_line_count += 1
                continue
            cleaned_lines.append(line.strip())

    tts_text = "\n".join(line for line in cleaned_lines if line)

    protocol = [
        f"1. Detectar título principal: '{title}'.",
        f"2. Saltar páginas preliminares y comenzar lectura desde la página {start_page}.",
        "3. Eliminar encabezados y pies repetidos (ej.: nombre del libro en cada página).",
        "4. Omitir metadatos editoriales, índices y numeración de página aislada.",
        "5. Leer en voz alta únicamente párrafos de contenido principal en orden.",
    ]

    result = ProtocolResult(
        title=title,
        start_page=start_page,
        total_pages=len(pages),
        repeated_lines=sorted(repeated_lines),
        removed_line_count=removed_line_count,
        tts_text=tts_text,
        protocol=protocol,
    )

    return result.__dict__
