# 🔒 GUÍA DE SEGURIDAD Y PRIVACIDAD

## 🚨 ARCHIVOS PROTEGIDOS POR .gitignore

Este proyecto está configurado para **NUNCA** subir información sensible a git. Los siguientes archivos están protegidos:

### 🔑 Credenciales
- `.env` - Tu clave API de OpenAI y configuraciones sensibles
- `*.env` - Cualquier archivo de configuración de entorno
- `config/secrets.json` - Configuraciones secretas
- `credentials.json` - Archivos de credenciales

### 🎵 Archivos de Audio (Contenido Confidencial)
- `audios/` - Tus archivos MP3 originales
- `*.mp3`, `*.wav`, `*.m4a`, etc. - Cualquier archivo de audio
- `chunks/` - Archivos temporales de audio

### 📄 Transcripciones (Contenido Sensible)
- `transcripciones/` - Todas las transcripciones generadas
- `*.txt` - Archivos de texto que pueden contener contenido confidencial

### 📊 Logs y Datos
- `logs/` - Logs que pueden contener información del procesamiento
- `*.log` - Archivos de registro
- `*.csv` - Datos procesados

### 🐍 Entorno de Desarrollo
- `.venv/` - Entorno virtual de Python
- `__pycache__/` - Cache de Python
- `.vscode/` - Configuraciones personales de VS Code

## ✅ CONFIGURACIÓN INICIAL SEGURA

### 1. Configurar Credenciales
```bash
# Copia la plantilla
cp .env.example .env

# Edita .env con tu clave real (NUNCA .env.example)
# OPENAI_API_KEY=sk-tu-clave-real-aqui
```

### 2. Verificar Protección
```bash
# Verificar que .env NO aparece en git
git status
# No deberías ver .env en la lista

# Verificar que .gitignore funciona
git check-ignore .env
# Debería mostrar: .env
```

## 🛡️ MEJORES PRÁCTICAS

### ✅ QUÉ HACER
- ✅ Usar `.env.example` como plantilla pública
- ✅ Mantener credenciales solo en `.env` local
- ✅ Verificar `.gitignore` antes de commits
- ✅ Usar variables de entorno en producción
- ✅ Compartir solo código, nunca datos

### ❌ QUÉ NO HACER
- ❌ NUNCA subir `.env` a git
- ❌ NUNCA hardcodear API keys en código
- ❌ NUNCA compartir archivos de audio originales
- ❌ NUNCA subir transcripciones a repositorios públicos
- ❌ NUNCA ignorar warnings de archivos sensibles

## 🔍 VERIFICACIÓN DE SEGURIDAD

### Comando Rápido de Verificación
```bash
# Verificar que archivos sensibles están protegidos
git ls-files | grep -E "\.(env|log|mp3|wav|txt)$|audios/|transcripciones/"
# No debería mostrar nada
```

### Verificar .gitignore
```bash
# Probar que archivos están ignorados
git check-ignore .env audios/ transcripciones/ logs/
# Todos deberían aparecer como ignorados
```

## 🚨 SI ACCIDENTALMENTE SUBES DATOS SENSIBLES

### 1. Remover del Historial
```bash
# Remover archivo del tracking (mantener local)
git rm --cached archivo_sensible

# Si ya está en commits previos, limpiar historial:
git filter-branch --force --index-filter \
'git rm --cached --ignore-unmatch archivo_sensible' \
--prune-empty --tag-name-filter cat -- --all
```

### 2. Invalidar Credenciales
- **API Keys**: Regenerar inmediatamente en OpenAI
- **Tokens**: Revocar y crear nuevos
- **Passwords**: Cambiar inmediatamente

### 3. Force Push (Solo si es necesario)
```bash
git push origin --force --all
```

## 🎯 ARCHIVOS SEGUROS PARA COMPARTIR

Los siguientes archivos SÍ pueden ser públicos:
- ✅ `README.md`
- ✅ `requirements.txt`
- ✅ `*.py` (código fuente)
- ✅ `.env.example` (plantilla sin credenciales)
- ✅ `.gitignore`
- ✅ Documentación (`*.md`)

## 🔒 CONFIGURACIÓN ADICIONAL

### Variables de Entorno del Sistema (Alternativa más segura)
```bash
# En lugar de .env, usar variables del sistema:
export OPENAI_API_KEY="sk-tu-clave-aqui"
```

### Usar Secrets en GitHub Actions (para CI/CD)
```yaml
# .github/workflows/main.yml
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

## ⚠️ RECORDATORIO IMPORTANTE

**Este proyecto maneja:**
- 🔑 **Credenciales API costosas** (OpenAI)
- 🎵 **Audio confidencial** (audiencias de 4-5 horas)
- 📄 **Transcripciones sensibles** (contenido legal/privado)

**¡La seguridad es CRÍTICA!** 🚨

Siempre verifica que `.gitignore` esté funcionando antes de hacer `git add` o `git commit`.
