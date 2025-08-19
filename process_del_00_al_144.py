#!/usr/bin/env python3
"""
🎯 Procesador específico para el archivo "del 00 al 1-44.mp3"
Analiza y formatea el contenido transcrito
"""

from pathlib import Path
from datetime import datetime
import time
import re

def seconds_to_timecode(seconds):
    """Convierte segundos a formato timecode 00;00;00;00"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centiseconds = int((seconds % 1) * 100)
    return f"{hours:02d};{minutes:02d};{secs:02d};{centiseconds:02d}"

def analyze_audio_content(content):
    """Analiza el contenido del audio para determinar tipo"""
    
    # Limpiar contenido
    lines = content.split('\n')
    actual_content = []
    
    for line in lines:
        line = line.strip()
        if (not line.startswith('#') and 
            line and 
            not line.startswith('Mantén el formato')):
            actual_content.append(line)
    
    content_text = ' '.join(actual_content)
    
    # Determinar tipo de contenido
    analysis = {
        'has_real_content': len(content_text) > 50,
        'is_instruction_repeat': 'mantén el formato' in content_text.lower(),
        'content_length': len(content_text),
        'line_count': len(actual_content),
        'audio_type': 'unknown'
    }
    
    if analysis['is_instruction_repeat']:
        analysis['audio_type'] = 'silent_or_noise'
    elif analysis['has_real_content']:
        content_lower = content_text.lower()
        
        if any(word in content_lower for word in ['juez', 'fiscal', 'tribunal', 'su señoría']):
            analysis['audio_type'] = 'legal_proceeding'
        elif any(word in content_lower for word in ['testigo', 'declaro', 'juro']):
            analysis['audio_type'] = 'testimony'
        else:
            analysis['audio_type'] = 'dialogue'
    
    return analysis, content_text

def create_formatted_output(content_text, audio_name, analysis):
    """Crea salida formateada basada en el análisis"""
    
    formatted_lines = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Header personalizado
    header = f"""# Transcripción con Formato Personalizado - Segmento de Audiencia
# Fecha: {timestamp}
# Archivo original: {audio_name}
# Tipo de contenido: {analysis['audio_type']}
# Duración estimada: 1 hora 44 minutos (del 00 al 1-44)
# Formato: Timecode | Speaker | Transcripción

"""
    formatted_lines.append(header)
    
    if analysis['audio_type'] == 'silent_or_noise':
        # Archivo sin contenido de habla detectado
        formatted_lines.extend([
            "# ANÁLISIS: Audio sin contenido de habla detectado",
            "# Posibles causas:",
            "#   - Segmento de silencio o pausa en la audiencia",
            "#   - Audio con ruido de fondo únicamente", 
            "#   - Problema técnico en la grabación",
            "#   - Conversaciones muy bajas o inaudibles",
            "",
            "00;00;00;00",
            "Sistema",
            "[SEGMENTO SIN HABLA DETECTADA]",
            "",
            "00;01;44;00", 
            "Sistema",
            "[FIN DEL SEGMENTO]",
            ""
        ])
    
    elif analysis['has_real_content']:
        # Procesar contenido real
        segments = content_text.split('. ')
        segments = [s.strip() for s in segments if len(s.strip()) > 10]
        
        if not segments:
            segments = [content_text]
        
        current_time = 0.0
        duration_seconds = 104 * 60  # 1h 44m en segundos
        time_per_segment = duration_seconds / max(len(segments), 1)
        
        for i, segment in enumerate(segments):
            if len(segment.strip()) < 5:
                continue
                
            timecode = seconds_to_timecode(current_time)
            
            # Determinar speaker simple
            segment_lower = segment.lower()
            if any(word in segment_lower for word in ['juez', 'su señoría', 'tribunal']):
                speaker = "Juez"
            elif any(word in segment_lower for word in ['fiscal', 'ministerio']):
                speaker = "Fiscal"
            elif any(word in segment_lower for word in ['defensa', 'licenciado']):
                speaker = "LCDO"
            else:
                speaker_num = (i % 3) + 1
                speaker = f"Speaker {speaker_num}"
            
            formatted_lines.extend([
                timecode,
                speaker,
                segment.strip(),
                ""
            ])
            
            current_time += time_per_segment
    
    else:
        # Contenido insuficiente
        formatted_lines.extend([
            "# ANÁLISIS: Contenido insuficiente para procesamiento",
            "",
            "00;00;00;00",
            "Sistema", 
            "[CONTENIDO INSUFICIENTE DETECTADO]",
            ""
        ])
    
    return '\n'.join(formatted_lines)

def process_del_00_al_144():
    """Procesador principal para el archivo del 00 al 1-44"""
    
    base_path = Path(__file__).parent
    input_file = base_path / "transcripciones" / "del 00 al 1-44.txt"
    
    if not input_file.exists():
        print(f"❌ No se encontró el archivo: {input_file}")
        return
    
    print(f"📖 Analizando: {input_file.name}")
    
    # Leer contenido
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Analizar contenido
    analysis, content_text = analyze_audio_content(content)
    
    print(f"🔍 ANÁLISIS DEL CONTENIDO:")
    print(f"   • Tipo de audio: {analysis['audio_type']}")
    print(f"   • Contenido real: {'Sí' if analysis['has_real_content'] else 'No'}")
    print(f"   • Longitud: {analysis['content_length']} caracteres")
    print(f"   • Líneas: {analysis['line_count']}")
    
    # Crear formato
    formatted_content = create_formatted_output(
        content_text, 
        "del 00 al 1-44.mp3", 
        analysis
    )
    
    # Guardar archivo formateado
    timestamp_suffix = int(time.time())
    output_file = base_path / "transcripciones" / f"FORMATO_DEL_00_AL_144_{timestamp_suffix}.txt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(formatted_content)
    
    print(f"✅ Archivo formateado creado: {output_file}")
    
    # Mostrar vista previa
    print(f"\n📖 VISTA PREVIA:")
    print("=" * 60)
    lines = formatted_content.split('\n')[:15]
    for line in lines:
        print(line)
    print("=" * 60)
    
    return output_file

if __name__ == "__main__":
    print("🎯 PROCESADOR DEL SEGMENTO 00:00 AL 1:44")
    print("=" * 60)
    
    result = process_del_00_al_144()
    
    if result:
        print(f"\n🎉 PROCESAMIENTO COMPLETADO")
        print(f"📁 Archivo disponible en: {result}")
        print(f"\n💡 NOTA: Este segmento corresponde a los primeros")
        print(f"    1 hora y 44 minutos de la audiencia legal.")
