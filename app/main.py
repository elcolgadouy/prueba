import os
from typing import Optional

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.pdf_cleaner import clean_pdf_text

app = FastAPI(title="Depurador IA de PDF")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/clean")
async def clean_pdf(file: UploadFile = File(...), use_ai: Optional[bool] = False):
    if file.content_type not in {"application/pdf", "application/octet-stream"}:
        return JSONResponse({"error": "El archivo debe ser un PDF."}, status_code=400)

    raw_pdf = await file.read()
    if not raw_pdf:
        return JSONResponse({"error": "El archivo está vacío."}, status_code=400)

    cleaned_text = clean_pdf_text(
        raw_pdf,
        use_ai=bool(use_ai),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )

    return {
        "filename": file.filename,
        "chars": len(cleaned_text),
        "cleaned_text": cleaned_text,
    }
