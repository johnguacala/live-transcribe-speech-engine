# 🎧 HearingsWhisper - Transcriptor de Audio Profesional

Sistema avanzado de transcripción para archivos de audio largos usando OpenAI Whisper API, optimizado para español de Puerto Rico.

## 🌟 Características Principales

- ✅ **Archivos largos**: Maneja audios de 4-5 horas automáticamente
- ✅ **División inteligente**: Chunks de 10 minutos con overlap para continuidad
- ✅ **Español de Puerto Rico**: Prompts optimizados para el dialecto local
- ✅ **Estimación de costos**: Calcula gastos antes de procesar
- ✅ **Logging detallado**: Seguimiento completo del proceso
- ✅ **Recuperación de errores**: Continúa aunque falle un chunk
- ✅ **Limpieza automática**: Remueve archivos temporales

## 📁 Estructura del Proyecto

```
HearingsWhisper/
├── audios/              # 📂 Coloca aquí tus archivos MP3
├── transcripciones/     # 📄 Transcripciones generadas
├── chunks/              # 🔧 Archivos temporales (auto-limpieza)
├── logs/                # 📊 Logs detallados de cada sesión
├── transcribe.py        # 🚀 Script principal
├── config.py            # ⚙️ Configuración centralizada
├── logger.py            # 📝 Sistema de logging
├── audio_utils.py       # 🎵 Utilidades de audio
├── .env                 # 🔑 Variables de entorno
├── requirements.txt     # 📦 Dependencias Python
├── INSTALACION.md       # 🛠️ Guía de instalación detallada
└── README.md            # 📖 Este archivo
```

## 🚀 Instalación Rápida

1. **Clona o descarga este proyecto**

2. **Sigue la guía de instalación:**

   ```bash
   # Ver instrucciones detalladas
   cat INSTALACION.md
   ```

3. **Configuración básica:**

   ```bash
   # Crear entorno virtual
   python -m venv whisper_env
   .\whisper_env\Scripts\activate

   # Instalar dependencias
   pip install -r requirements.txt

   # Configurar API key en .env
   # OPENAI_API_KEY=tu_clave_aqui
   ```

## 🎯 Uso

### Proceso Simple

```bash
# Activar entorno
.\whisper_env\Scripts\activate

# Colocar archivos MP3 en carpeta audios/

# Ejecutar transcripción
python transcribe.py
```

### Características del Proceso

1. **Estimación automática**: Te muestra duración total y costo estimado
2. **Confirmación**: Puedes cancelar antes de gastar dinero
3. **Progreso en tiempo real**: Seguimiento detallado en consola y logs
4. **División automática**: Archivos grandes se procesan en chunks
5. **Transcripciones con metadata**: Incluye fecha, modelo usado, etc.

## 💰 Costos de OpenAI

| Duración | Costo Aproximado |
| -------- | ---------------- |
| 1 hora   | $0.36 USD        |
| 4 horas  | $1.44 USD        |
| 5 horas  | $1.80 USD        |
| 10 horas | $3.60 USD        |

**Precio:** $0.006 por minuto de audio

## 📊 Ejemplo de Salida

```
🎵 Iniciando procesamiento de archivos de audio
📊 Archivos encontrados: 2
⏱️  Duración total: 8.3 horas
💰 Estimación de costo: 498.0 minutos × $0.006 = $2.99

🎧 Procesando 1/2: audiencia_parte1.mp3
🔧 Dividiendo audiencia_parte1.mp3 (247.5 min) en chunks de 10 min
✅ Creados 25 chunks para audiencia_parte1.mp3
📊 Progreso: 25/25 chunks (100.0%)
✅ Completado: audiencia_parte1.mp3 (247.5 min, ~$1.49)

🎉 Procesamiento completado: 2/2 archivos exitosos
⏱️  Tiempo total: 18.2 minutos
```

## 🔧 Configuración Avanzada

### Variables de Entorno (.env)

```bash
# API Configuration
OPENAI_API_KEY=tu_clave_aqui

# Audio Processing Settings
CHUNK_DURATION_MINUTES=10    # Duración de cada chunk
MAX_FILE_SIZE_MB=24          # Límite antes de dividir
LANGUAGE=es                  # Idioma principal
REGION=puerto_rico           # Región específica

# Paths (opcionales)
AUDIO_FOLDER=audios
CHUNKS_FOLDER=chunks
TRANSCRIPTIONS_FOLDER=transcripciones
LOGS_FOLDER=logs
```

### Personalización de Prompts

En `config.py` puedes modificar el prompt para mejor precisión:

```python
prompt_template: str = (
    "Este es un audio en español de Puerto Rico. "
    "Transcribe con puntuación correcta, incluyendo nombres propios "
    "y palabras en inglés que puedan aparecer. "
    "Mantén el formato natural del habla puertorriqueña."
)
```

## 🚨 Troubleshooting

### Problemas Comunes

1. **"ffmpeg: command not found"**

   - Instala ffmpeg siguiendo `INSTALACION.md`
   - Verifica con: `ffmpeg -version`

2. **"OPENAI_API_KEY no está configurada"**

   - Edita el archivo `.env` con tu clave real
   - No dejes espacios extra

3. **Error de importación OpenAI**
   - Activa el entorno virtual: `.\whisper_env\Scripts\activate`
   - Reinstala: `pip install -r requirements.txt`

### Logs Detallados

Todos los procesos se registran en `logs/`. Revisa estos archivos para:

- Errores específicos
- Progreso detallado
- Información de costos

## 🔄 Funciones Pendientes

Las siguientes características están planificadas pero no implementadas:

- [ ] **WhisperX Integration**: Alineación por palabra
- [ ] **CSV Export**: Análisis de contenido estructurado
- [ ] **Audio Cleanup**: Pre-procesamiento automático de audio
- [ ] **Dashboard Web**: Interfaz visual para revisión
- [ ] **Batch Processing**: Cola de trabajos
- [ ] **Speaker Diarization**: Identificación de hablantes
- [ ] **Custom Vocabulary**: Diccionarios especializados

## 👨‍💻 Autor

**John Guarenas**  
_AI Audio Consultant_  
_Especialista en transcripción automatizada para proyectos de voz y narrativa_

## 📄 Licencia

Este proyecto está disponible bajo licencia MIT. Ver archivo LICENSE para detalles.

---

¿Preguntas? ¿Mejoras? ¡Abre un issue o contacta al autor! 🚀
