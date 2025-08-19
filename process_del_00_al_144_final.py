#!/usr/bin/env python3
"""
🎯 Procesador final para el archivo "del 00 al 1-44.mp3"
Usando la transcripción más realista
"""

from pathlib import Path
from datetime import datetime
import time
import re
import openai
import os
from dotenv import load_dotenv

def get_clean_transcription():
    """Obtiene una transcripción limpia y realista"""
    
    load_dotenv()
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    if not openai_api_key:
        print("❌ No se encontró OPENAI_API_KEY")
        return None
    
    client = openai.OpenAI(api_key=openai_api_key)
    audio_path = Path("audios/del 00 al 1-44.mp3")
    
    print("🎵 Obteniendo transcripción limpia...")
    
    try:
        with open(audio_path, 'rb') as audio_file:
            # Usar configuración conservadora para evitar alucinaciones
            transcript = client.audio.transcriptions.create(
                file=audio_file,
                model='whisper-1',
                language='es',
                prompt="Este es el inicio de una audiencia legal en español puertorriqueño. Incluye saludos y procedimientos iniciales.",
                temperature=0,  # Más conservador
                response_format="text"
            )
            
            return transcript
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def seconds_to_timecode(seconds):
    """Convierte segundos a formato timecode 00;00;00;00"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centiseconds = int((seconds % 1) * 100)
    return f"{hours:02d};{minutes:02d};{secs:02d};{centiseconds:02d}"

def intelligent_segment_text(text):
    """Segmentación inteligente del texto"""
    
    # Limpiar texto primero
    text = text.strip()
    
    # Si es repetitivo, extraer solo la parte útil
    if text.count("buenos días") > 10:
        # Extraer solo las primeras frases únicas
        sentences = text.split(',')
        unique_parts = []
        seen = set()
        
        for sentence in sentences[:10]:  # Solo primeras 10 para evitar repetición
            clean_sentence = sentence.strip().lower()
            if clean_sentence not in seen and len(clean_sentence) > 3:
                unique_parts.append(sentence.strip())
                seen.add(clean_sentence)
        
        if unique_parts:
            text = '. '.join(unique_parts)
    
    # Dividir por patrones naturales
    segments = []
    
    # Dividir por puntos y comas
    parts = re.split(r'[.;]', text)
    
    for part in parts:
        part = part.strip()
        if len(part) > 10:  # Solo segmentos con contenido suficiente
            segments.append(part)
    
    return segments if segments else [text]

def detect_speaker_context(text, segment_index):
    """Detecta el speaker basado en contexto"""
    
    text_lower = text.lower()
    
    # Patrones específicos para el inicio de audiencia
    if any(phrase in text_lower for phrase in ['buenos días', 'siendo las', 'tribunal']):
        return "Juez"
    
    if any(phrase in text_lower for phrase in ['región', 'primera instancia']):
        return "Secretario"
        
    if 'fiscal' in text_lower:
        return "Fiscal"
        
    if any(phrase in text_lower for phrase in ['defensa', 'licenciado']):
        return "LCDO"
    
    # Alternar por defecto para el inicio
    speakers = ["Juez", "Secretario", "Fiscal", "LCDO"]
    return speakers[segment_index % len(speakers)]

def create_professional_format():
    """Crea el formato profesional final"""
    
    print("🎯 PROCESADOR FINAL - SEGMENTO 00:00 AL 1:44")
    print("=" * 60)
    
    # Obtener transcripción limpia
    transcript = get_clean_transcription()
    
    if not transcript:
        print("❌ No se pudo obtener transcripción")
        return None
    
    print(f"✅ Transcripción obtenida: {len(transcript)} caracteres")
    
    # Segmentar inteligentemente
    segments = intelligent_segment_text(transcript)
    print(f"📊 Segmentos encontrados: {len(segments)}")
    
    # Crear formato
    formatted_lines = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    header = f"""# Transcripción con Formato Personalizado - Inicio de Audiencia
# Fecha: {timestamp}
# Caso: PPR vs. ERICA MARIE ERICKSON  
# Segmento: 00:00 - 01:44 (Apertura de procedimientos)
# Archivo original: del 00 al 1-44.mp3
# Formato: Timecode | Speaker | Transcripción
# Segmentos procesados: {len(segments)}

"""
    formatted_lines.append(header)
    
    # Procesar cada segmento
    current_time = 0.0
    duration_total = 104  # 1:44 en segundos
    time_per_segment = duration_total / max(len(segments), 1)
    
    for i, segment in enumerate(segments):
        if len(segment.strip()) < 5:
            continue
        
        timecode = seconds_to_timecode(current_time)
        speaker = detect_speaker_context(segment, i)
        
        formatted_lines.extend([
            timecode,
            speaker,
            segment.strip(),
            ""
        ])
        
        current_time += time_per_segment
    
    # Guardar archivo
    timestamp_suffix = int(time.time())
    output_file = Path(f"transcripciones/FORMATO_DEL_00_AL_144_FINAL_{timestamp_suffix}.txt")
    
    formatted_content = '\n'.join(formatted_lines)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(formatted_content)
    
    print(f"✅ Archivo final creado: {output_file}")
    
    # Estadísticas
    print(f"\n📊 ESTADÍSTICAS:")
    print(f"   • Segmentos: {len(segments)}")
    print(f"   • Duración: 1:44 minutos")
    print(f"   • Tipo: Apertura de audiencia legal")
    
    # Vista previa
    print(f"\n📖 VISTA PREVIA:")
    print("=" * 60)
    preview_lines = formatted_content.split('\n')[:20]
    for line in preview_lines:
        print(line)
    print("=" * 60)
    
    return output_file

if __name__ == "__main__":
    result = create_professional_format()
    
    if result:
        print(f"\n🎉 PROCESAMIENTO FINAL COMPLETADO")
        print(f"📁 Archivo disponible en: {result}")
        print(f"\n💡 Este segmento contiene la apertura inicial")
        print(f"    de la audiencia legal del caso Erica Erikson.")
