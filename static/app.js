function normalizeLine(line) {
  return line.trim().toLowerCase().replace(/\s+/g, " ");
}

function splitPages(rawText) {
  if (rawText.includes("\f")) {
    return rawText.split("\f").filter((p) => p.trim()).map((p) => p.split(/\r?\n/));
  }

  const chunks = rawText.split(/^\s*---\s*p[aá]gina\s+\d+\s*---\s*$/gim).filter((c) => c.trim());
  if (chunks.length > 1) {
    return chunks.map((c) => c.split(/\r?\n/));
  }

  return [rawText.split(/\r?\n/)];
}

function isNoiseLine(line) {
  const normalized = normalizeLine(line);
  if (!normalized) return true;
  if (/^\d+$/.test(normalized)) return true;
  if (/(isbn|archivo digital|cdd|compilador|autores|coordinaci[oó]n editorial)/.test(normalized)) return true;
  if (/(volver al [ií]ndice|ediciones universidad)/.test(normalized)) return true;
  return false;
}

function detectRepeatedLines(pages, threshold = 0.6) {
  if (pages.length < 2) return new Set();
  const counts = new Map();

  pages.forEach((page) => {
    const unique = new Set(page.map(normalizeLine).filter((l) => l && l.length <= 80));
    unique.forEach((line) => counts.set(line, (counts.get(line) || 0) + 1));
  });

  const minCount = Math.max(2, Math.floor(pages.length * threshold));
  return new Set(Array.from(counts.entries()).filter(([, freq]) => freq >= minCount).map(([line]) => line));
}

function findTitle(firstPage) {
  for (const line of firstPage) {
    if (!isNoiseLine(line) && line.trim().length > 3) return line.trim();
  }
  return "Documento sin título";
}

function findStartPage(pages, keywords) {
  const lower = keywords.map((k) => k.toLowerCase());
  for (let i = 0; i < pages.length; i += 1) {
    const pageText = pages[i].join(" ").toLowerCase();
    if (lower.some((k) => pageText.includes(k))) return i + 1;
  }
  return 1;
}

function buildProtocol(rawText, keywords) {
  const pages = splitPages(rawText);
  const repeated = detectRepeatedLines(pages);
  const startPage = findStartPage(pages, keywords);
  const title = findTitle(pages[0]);

  let removedCount = 0;
  const cleaned = [];

  pages.forEach((page, idx) => {
    if (idx + 1 < startPage) {
      removedCount += page.length;
      return;
    }

    page.forEach((line) => {
      const normalized = normalizeLine(line);
      if (repeated.has(normalized) || isNoiseLine(line)) {
        removedCount += 1;
        return;
      }
      cleaned.push(line.trim());
    });
  });

  return {
    title,
    startPage,
    totalPages: pages.length,
    removedCount,
    repeatedLines: Array.from(repeated).sort(),
    ttsText: cleaned.filter(Boolean).join("\n"),
    protocol: [
      `1. Detectar título principal: '${title}'.`,
      `2. Saltar páginas preliminares y comenzar lectura desde la página ${startPage}.`,
      "3. Eliminar encabezados y pies repetidos (ej.: nombre del libro en cada página).",
      "4. Omitir metadatos editoriales, índices y numeración de página aislada.",
      "5. Leer en voz alta únicamente párrafos de contenido principal en orden.",
    ],
  };
}

async function extractTextFromPdf(file) {
  if (!window.pdfjsLib) {
    throw new Error("No se pudo cargar PDF.js. Revisa la conexión a internet.");
  }

  window.pdfjsLib.GlobalWorkerOptions.workerSrc =
    "https://cdn.jsdelivr.net/npm/pdfjs-dist@4.5.136/legacy/build/pdf.worker.min.js";

  const buffer = await file.arrayBuffer();
  const document = await window.pdfjsLib.getDocument({ data: new Uint8Array(buffer) }).promise;

  const pages = [];

  for (let pageNumber = 1; pageNumber <= document.numPages; pageNumber += 1) {
    const page = await document.getPage(pageNumber);
    const content = await page.getTextContent();
    const lines = content.items
      .map((item) => (typeof item.str === "string" ? item.str.trim() : ""))
      .filter(Boolean);

    pages.push(`--- Página ${pageNumber} ---\n${lines.join("\n")}`);
  }

  return pages.join("\n\n");
}

const fileInput = document.getElementById("file");
const fileStatus = document.getElementById("fileStatus");
const sourceInput = document.getElementById("source");
const runBtn = document.getElementById("run");
const output = document.getElementById("output");
const protocolNode = document.getElementById("protocol");
const ttsNode = document.getElementById("tts");

fileInput.addEventListener("change", async (event) => {
  const [file] = event.target.files;
  if (!file) return;

  fileStatus.textContent = "Procesando archivo...";

  try {
    if (file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf")) {
      const text = await extractTextFromPdf(file);
      sourceInput.value = text;
      fileStatus.textContent = `PDF cargado: ${file.name} (${text.length} caracteres extraídos).`;
      return;
    }

    const text = await file.text();
    sourceInput.value = text;
    fileStatus.textContent = `TXT cargado: ${file.name} (${text.length} caracteres).`;
  } catch (error) {
    fileStatus.textContent = `No se pudo procesar el archivo: ${error.message}`;
  }
});

runBtn.addEventListener("click", () => {
  const text = sourceInput.value;
  if (!text.trim()) {
    alert("Debes pegar o subir un texto para procesar.");
    return;
  }

  const keywords = document
    .getElementById("keywords")
    .value.split(",")
    .map((k) => k.trim())
    .filter(Boolean);

  const result = buildProtocol(text, keywords);
  protocolNode.textContent = [
    `Título detectado: ${result.title}`,
    `Inicio sugerido: página ${result.startPage} de ${result.totalPages}`,
    `Líneas eliminadas: ${result.removedCount}`,
    "",
    ...result.protocol,
    "",
    "Encabezados/Pies detectados como repetidos:",
    ...(result.repeatedLines.length ? result.repeatedLines : ["(No detectados)"]),
  ].join("\n");

  ttsNode.value = result.ttsText;
  output.hidden = false;
});
