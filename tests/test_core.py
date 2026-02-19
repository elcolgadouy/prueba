import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from core import build_protocol


def test_build_protocol_skips_front_matter_and_repeated_headers():
    text = """China. La superación de la pobreza
Ficha editorial
ISBN 12345
\f
China. La superación de la pobreza
Indice
\f
China. La superación de la pobreza
Prólogo
Este es el inicio del contenido.
\f
China. La superación de la pobreza
Capítulo 1
Contenido real.
"""

    result = build_protocol(text, ["Prólogo", "Capítulo"])

    assert result["title"] == "China. La superación de la pobreza"
    assert result["start_page"] == 3
    assert "China. La superación de la pobreza" not in result["tts_text"]
    assert "Contenido real." in result["tts_text"]
