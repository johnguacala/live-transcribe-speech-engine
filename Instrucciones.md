¡Por supuesto, John! Aquí tenés el documento completo en formato Markdown, listo para copiar, guardar como `.md`, o integrar en tu repositorio de trabajo:

---

````markdown
# 📝 Guía para Transcripción de Audio con la API de OpenAI (Whisper)

Este documento describe cómo configurar y ejecutar un flujo de trabajo en **Visual Studio Code** para transcribir múltiples horas de audio usando la API de OpenAI.

---

## ⚙️ Requisitos Previos

- Python 3.10 o superior
- Cuenta en [OpenAI](https://platform.openai.com/)
- Clave API activa
- Visual Studio Code instalado
- ffmpeg instalado (para dividir audios largos)

---

## 🧰 Instalación del Entorno

1. Crear entorno virtual:
   ```bash
   python -m venv whisper_env
   source whisper_env/bin/activate  # En Windows: .\whisper_env\Scripts\activate
   ```
````

2. Instalar dependencias:

   ```bash
   pip install openai ffmpeg-python python-dotenv tqdm
   ```

3. Crear archivo `.env` en la raíz del proyecto:
   ```
   OPENAI_API_KEY=tu_clave_aqui
   ```

---

## 🎧 Preparación de Audios

- Asegurate de que los archivos estén en formato `.mp3`, `.wav` o `.m4a`.
- Si el archivo supera los **25MB**, dividilo con ffmpeg:
  ```bash
  ffmpeg -i largo.mp3 -f segment -segment_time 600 -c copy partes/output%03d.mp3
  ```

---

## 📤 Script de Transcripción

Guardá este script como `transcribe.py`:

```python
import openai
import os
from dotenv import load_dotenv
from pathlib import Path

# Cargar API Key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Definir carpetas
audio_folder = Path("audios")
output_folder = Path("transcripciones")
output_folder.mkdir(exist_ok=True)

# Procesar cada archivo de audio
for audio_file in audio_folder.glob("*.mp3"):
    print(f"Procesando: {audio_file.name}")
    with open(audio_file, "rb") as f:
        transcript = openai.Audio.transcribe(
            model="whisper-1",
            file=f,
            response_format="text",  # También puede ser "json" o "srt"
            language="es",
            prompt="Transcribe con puntuación correcta y formato claro."
        )
    # Guardar resultado
    output_path = output_folder / f"{audio_file.stem}.txt"
    with open(output_path, "w", encoding="utf-8") as out:
        out.write(transcript)
```

---

## 🧠 Opciones Avanzadas

- `response_format="srt"` → genera subtítulos con timecodes.
- `language="auto"` → Whisper detecta el idioma automáticamente.
- `prompt="..."` → podés personalizar el estilo de transcripción.

---

## ✅ Ejecución

1. Activá el entorno virtual:

   ```bash
   source whisper_env/bin/activate
   ```

2. Ejecutá el script:
   ```bash
   python transcribe.py
   ```

---

## 📁 Estructura Recomendada

```
/mi-proyecto-whisper
│
├── audios/               # Audios originales
├── transcripciones/      # Archivos de texto generados
├── .env                  # Clave API
├── transcribe.py         # Script principal
└── README.md             # Este documento
```

---

## 🧩 Siguientes pasos

- Integrar con WhisperX para alineación por palabra
- Exportar a `.csv` para análisis de contenido
- Automatizar limpieza de audio antes de transcribir
- Crear dashboard para revisión de transcripciones

---

**Autor:** John Guarenas  
**Rol:** AI Audio Consultant  
**Objetivo:** Transcripción precisa y escalable para proyectos de voz y narrativa

```

---

¿Querés que te lo convierta en una plantilla para GitHub con estructura modular y documentación extendida? También puedo ayudarte a agregar funciones como logging, control de errores o exportación en lote.
```
