# 🚀 Guía de Instalación - Windows

Esta guía te llevará paso a paso para configurar el entorno de transcripción.

## 📋 Prerrequisitos

1. **Python 3.10 o superior**

   - Descargá desde: https://www.python.org/downloads/
   - ✅ Marcá "Add Python to PATH" durante la instalación

2. **Git para Windows** (opcional pero recomendado)
   - Descargá desde: https://git-scm.windows.com/

## 🔧 Instalación de ffmpeg

ffmpeg es **OBLIGATORIO** para procesar archivos de audio largos (4-5 horas).

### Opción 1: Usando Chocolatey (Recomendado)

1. Instalá Chocolatey siguiendo: https://chocolatey.org/install
2. Abrí PowerShell como Administrador
3. Ejecutá:
   ```powershell
   choco install ffmpeg
   ```

### Opción 2: Descarga Manual

1. Descargá ffmpeg desde: https://ffmpeg.org/download.html#build-windows
2. Extraé el contenido a `C:\ffmpeg`
3. Agregá `C:\ffmpeg\bin` a tu PATH:
   - Windows Key + R, escribí `sysdm.cpl`
   - Propiedades del Sistema → Variables de Entorno
   - En Variables del Sistema, buscá `Path` y editala
   - Agregá nueva entrada: `C:\ffmpeg\bin`
   - Reiniciá la terminal

### Verificar Instalación

Abrí una nueva terminal y ejecutá:

```bash
ffmpeg -version
```

Deberías ver información sobre la versión de ffmpeg.

## 🐍 Configuración del Entorno Python

1. **Abrí terminal en la carpeta del proyecto:**

   ```bash
   cd "d:\_UPWORK\Erica Erikson\HearingsWhisper"
   ```

2. **Creá el entorno virtual:**

   ```bash
   python -m venv whisper_env
   ```

3. **Activá el entorno:**

   ```bash
   .\whisper_env\Scripts\activate
   ```

   💡 **Importante:** Verás `(whisper_env)` al inicio de tu prompt cuando esté activado.

4. **Actualizá pip:**

   ```bash
   python -m pip install --upgrade pip
   ```

5. **Instalá las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

## 🔑 Configuración de OpenAI API

1. **Conseguí tu API Key:**

   - Visitá: https://platform.openai.com/api-keys
   - Creá una nueva clave si no tenés una

2. **Configurá el archivo .env:**
   - Abrí el archivo `.env` en VS Code
   - Reemplazá `tu_clave_aqui` con tu API key real:
     ```
     OPENAI_API_KEY=sk-tu-clave-real-aqui
     ```

## 📁 Preparación de Archivos

1. **Colocá tus archivos MP3** en la carpeta `audios/`
2. Los archivos pueden ser de cualquier duración (4-5 horas está perfecto)
3. Formatos soportados: `.mp3`, `.wav`, `.m4a`, `.flac`, `.ogg`

## ✅ Verificación de la Instalación

Ejecutá este comando para verificar que todo esté configurado:

```bash
python transcribe.py
```

Si todo está bien, deberías ver:

- Estimación de costos de tus archivos
- Opción para continuar o cancelar

## 🚨 Solución de Problemas Comunes

### Error: "ffmpeg: command not found"

- Verificá que ffmpeg esté instalado y en el PATH
- Reiniciá la terminal después de instalar
- Probá el comando `ffmpeg -version`

### Error: "OPENAI_API_KEY no está configurada"

- Verificá que el archivo `.env` tiene tu clave real
- Asegurate de que no hay espacios extra en la clave

### Error: "Import openai could not be resolved"

- Verificá que el entorno virtual esté activado: `(whisper_env)`
- Reinstalá las dependencias: `pip install -r requirements.txt`

### Archivos de audio no se encuentran

- Verificá que los archivos estén en la carpeta `audios/`
- Verificá que tengan extensiones soportadas

## 💰 Estimación de Costos

**Precio de OpenAI Whisper:** $0.006 por minuto

Ejemplos:

- 1 hora de audio = $0.36 USD
- 4 horas de audio = $1.44 USD
- 5 horas de audio = $1.80 USD

El script te mostrará una estimación exacta antes de procesar.

## 🎯 Próximos Pasos

Una vez que todo funcione:

1. Ejecutá `python transcribe.py`
2. Revisá las estimaciones de costo
3. Confirmá el procesamiento
4. Las transcripciones aparecerán en `transcripciones/`
5. Los logs se guardan en `logs/`

¡Listo para transcribir! 🎉
