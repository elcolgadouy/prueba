# Generador de protocolo de lectura (TXT/PDF)

Esta app te permite:
- cargar un archivo `.txt` o `.pdf`,
- limpiar encabezados/pies repetidos y metadatos,
- sugerir desde qué página iniciar la lectura (por ejemplo desde "Prólogo"),
- obtener un texto limpio para usar en TTS (texto a voz).

## Requisitos
- Python 3.10+
- Navegador web moderno
- Conexión a internet para cargar PDF.js desde CDN (solo necesaria cuando subes PDF)

## Cómo ejecutar la app

1. Entra a la carpeta del proyecto:

```bash
cd /workspace/prueba
```

2. (Opcional) Ejecuta tests rápidos:

```bash
pytest -q
```

3. Levanta el servidor:

```bash
python app.py
```

4. Abre la app en tu navegador:

```text
http://localhost:8000
```

## Uso rápido
1. Sube un archivo `.txt` o `.pdf` (o pega el texto en el textarea).
2. Ajusta las palabras clave de inicio (ej.: `Prólogo, Introducción, Capítulo`).
3. Haz clic en **Generar protocolo**.
4. Copia el texto limpio del bloque **Texto limpio para TTS**.

## Solución de problemas
- Si no carga PDF:
  - revisa internet (PDF.js se carga desde CDN),
  - prueba abrir la consola del navegador para ver errores.
- Si el puerto 8000 está ocupado:
  - cierra el proceso que lo use o adapta `app.py` a otro puerto.
