# Depurador IA de PDF para lectura en voz alta

Aplicación web para:
1. Subir un PDF.
2. Extraer su texto.
3. Depurarlo eliminando encabezados, pies de página, numeración y ruido repetido.
4. Leer el texto limpio en voz alta desde el navegador.

## Stack
- **Backend**: FastAPI
- **Extracción PDF**: pypdf
- **Frontend**: HTML + JavaScript (Web Speech API)

## Requisitos
- Python 3.10+

## Instalación
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Ejecutar
```bash
uvicorn app.main:app --reload
```

Abrir: http://127.0.0.1:8000

## Variables opcionales
- `OPENAI_API_KEY`: si está definida, se puede usar para un refinado adicional de texto con IA.

> Si no hay API key, el sistema usa limpieza heurística local.
