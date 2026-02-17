from app.pdf_cleaner import _is_page_number, _normalize_line


def test_normalize_line():
    assert _normalize_line("  Hola   Mundo  ") == "hola mundo"


def test_page_number_detection():
    assert _is_page_number("12")
    assert _is_page_number("Page 1 of 10")
    assert _is_page_number("p. 7")
    assert not _is_page_number("Introducción")
