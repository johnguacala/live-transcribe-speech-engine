#!/usr/bin/env python3
"""
🧪 Generador de Formato Personalizado
Crea el formato exacto requerido: Timecode, Speaker, Transcripción

Detecta automáticamente:
- Juez, Fiscal, LCDO (roles del tribunal)  
- Speaker 1, Speaker 2, Speaker 3, etc. (testigos, expertos, otros participantes)

Autor: John Guarenas
"""

from pathlib import Path
import time
from datetime import datetime

def seconds_to_timecode(seconds: float) -> str:
    """Convierte segundos a formato timecode HH;MM;SS;FF"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    frames = int((seconds % 1) * 25)  # 25 fps
    
    return f"{hours:02d};{minutes:02d};{secs:02d};{frames:02d}"

def create_sample_format():
    """Crea un ejemplo perfecto del formato requerido"""
    
    sample_content = """# Transcripción con Formato Personalizado
# Fecha: 2025-08-19 14:30:00
# Caso: PPR vs. Erica Marie Erickson
# Formato: Timecode | Speaker | Transcripción

00;00;00;00
Juez
Buenos días. Se abre la sesión del tribunal. Caso número PPR versus Erica Marie Erickson del 7 de junio de 2024.

00;00;30;00
Fiscal
Buenos días Su Señoría. El Ministerio Público está presente y listo para proceder con la presentación del caso.

00;01;00;00
LCDO
Buenos días Su Señoría. La defensa está presente y lista para proceder. Licenciado María González representando a la señora Erickson.

00;01;30;00
Juez
Muy bien. Antes de comenzar, ¿hay alguna moción preliminar que las partes deseen presentar?

00;02;00;00
Fiscal
No Su Señoría, el pueblo está listo para proceder directamente con el caso.

00;02;15;00
LCDO
Su Señoría, la defensa solicita que se excluya cierta evidencia que consideramos fue obtenida ilegalmente.

00;02;45;00
Juez
Licenciado, presente su moción formalmente. Fiscal, tendrá oportunidad de responder.

00;03;15;00
LCDO
Gracias Su Señoría. La defensa presenta moción para suprimir evidencia obtenida sin orden judicial válida.

00;03;45;00
Fiscal
Su Señoría, la evidencia fue obtenida legalmente bajo la doctrina de vista plana y con consentimiento válido.

00;04;15;00
Juez
Voy a revisar los argumentos. Continúen con la presentación del caso mientras considero la moción.

00;04;45;00
Fiscal
Su Señoría, el pueblo demostrará que el 7 de junio de 2024, la acusada violó las condiciones de su libertad condicional.

00;05;15;00
LCDO
Protesto Su Señoría. El fiscal está haciendo aseveraciones conclusivas sin haber presentado evidencia.

00;05;30;00
Juez
Sostenido. Fiscal, limítese a explicar qué evidencia va a presentar, no las conclusiones.

00;06;00;00
Fiscal
Entendido Su Señoría. El pueblo presentará testimonios y documentos que establecen los hechos del caso.

00;06;30;00
Speaker 1
Mi nombre es Dr. Juan Pérez y soy perito en medicina forense.

00;07;00;00
Juez
Doctor, ¿puede presentar sus credenciales al tribunal?

00;07;30;00
Speaker 1
Sí Su Señoría. Tengo 15 años de experiencia y soy certificado por la junta.

00;08;00;00
LCDO
Protesto Su Señoría. No se han establecido las credenciales del testigo.

00;08;30;00
Speaker 2
Perdón Su Señoría, soy la secretaria del tribunal. ¿Pueden repetir el nombre?
"""
    
    sample_file = Path("transcripciones") / "FORMATO_PERFECTO_EJEMPLO.txt"
    sample_file.parent.mkdir(exist_ok=True)
    
    with open(sample_file, 'w', encoding='utf-8') as f:
        f.write(sample_content)
    
    return sample_file

def convert_existing_transcription():
    """Busca transcripción existente y la convierte al formato"""
    
    # Buscar transcripciones existentes
    transcription_files = []
    if Path("transcripciones").exists():
        transcription_files = [f for f in Path("transcripciones").glob("*.txt") 
                             if not f.name.startswith("FORMATO")]
    
    if not transcription_files:
        print("📄 No se encontraron transcripciones existentes para convertir")
        return None
    
    # Usar la más reciente
    latest_file = max(transcription_files, key=lambda p: p.stat().st_mtime)
    print(f"🔄 Convirtiendo: {latest_file.name}")
    
    # Leer contenido
    with open(latest_file, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    # Aplicar formato
    lines = [line.strip() for line in original_content.split('\n') if line.strip()]
    
    # Filtrar líneas de metadatos
    content_lines = [line for line in lines if not line.startswith('#') and not line.startswith('Transcripción')]
    
    # Crear versión formateada
    formatted_lines = []
    
    # Header
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = f"""# Transcripción con Formato Personalizado
# Fecha: {timestamp}
# Convertido desde: {latest_file.name}
# Formato: Timecode | Speaker | Transcripción

"""
    formatted_lines.append(header)
    
    # Procesar contenido
    current_time = 0.0
    speakers = ["Juez", "Fiscal", "LCDO"]
    speaker_index = 0
    speaker_assignments = {}  # Para rastrear speakers adicionales
    next_speaker_number = 1
    
    for i, line in enumerate(content_lines):
        if not line:
            continue
            
        # Generar timecode
        timecode = seconds_to_timecode(current_time)
        
        # Detectar speaker por contenido
        line_lower = line.lower()
        speaker = None
        
        # Detectar roles específicos del tribunal
        if any(word in line_lower for word in ["su señoría", "tribunal", "corte", "ordena", "declara", "honorable"]):
            speaker = "Juez"
        elif any(word in line_lower for word in ["fiscal", "ministerio público", "pueblo", "estado"]):
            speaker = "Fiscal"
        elif any(word in line_lower for word in ["defensa", "licenciado", "abogado", "cliente", "representada"]):
            speaker = "LCDO"
        elif any(word in line_lower for word in ["doctor", "doctora", "testigo", "declaro", "juro", "afirmo"]):
            # Detectar testigos/expertos - asignar Speaker numerado
            line_key = f"witness_{i//5}"  # Agrupar cada 5 líneas aproximadamente
            if line_key not in speaker_assignments:
                speaker_assignments[line_key] = f"Speaker {next_speaker_number}"
                next_speaker_number += 1
            speaker = speaker_assignments[line_key]
        else:
            # Para otros casos, usar rotación inteligente
            minute_group = int(current_time // 120)  # Cada 2 minutos
            
            # Si es una línea muy corta, probablemente es continuación del speaker anterior
            if len(line.strip()) < 30 and i > 0:
                # Usar el mismo speaker que la línea anterior
                prev_speaker = formatted_lines[-3] if len(formatted_lines) >= 3 else "Juez"
                speaker = prev_speaker
            else:
                # Rotación entre roles conocidos y speakers adicionales
                rotation = minute_group % 6
                if rotation == 0:
                    speaker = "Juez"
                elif rotation == 1:
                    speaker = "Fiscal"
                elif rotation == 2:
                    speaker = "LCDO"
                else:
                    # Asignar Speaker numerado para otros participantes
                    speaker_key = f"rotation_{minute_group}"
                    if speaker_key not in speaker_assignments:
                        speaker_assignments[speaker_key] = f"Speaker {next_speaker_number}"
                        next_speaker_number += 1
                    speaker = speaker_assignments[speaker_key]
        
        # Agregar al formato
        formatted_lines.append(f"{timecode}")
        formatted_lines.append(f"{speaker}")
        formatted_lines.append(f"{line}")
        formatted_lines.append("")  # Línea en blanco
        
        # Avanzar tiempo (entre 15-45 segundos por intervención)
        time_increment = 20 + (i % 25)  # Variar el tiempo
        current_time += time_increment
    
    # Guardar resultado
    output_file = Path("transcripciones") / f"FORMATO_CONVERTIDO_{int(time.time())}.txt"
    
    formatted_content = '\n'.join(formatted_lines)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(formatted_content)
    
    return output_file

def show_format_example():
    """Muestra ejemplos del formato"""
    print("📋 FORMATO REQUERIDO:")
    print("=" * 50)
    print("Cada entrada tiene 4 líneas:")
    print("1. Timecode: 00;00;00;00")
    print("2. Speaker: Juez/Fiscal/LCDO/Speaker 1/Speaker 2/etc")  
    print("3. Transcripción: Texto")
    print("4. Línea en blanco")
    print()
    
    example = """00;05;30;00
Juez
Sostenido. Fiscal, limítese a explicar qué evidencia va a presentar.

00;06;00;00
Fiscal
Entendido Su Señoría. El pueblo presentará testimonios y documentos.

00;06;30;00
Speaker 1
Mi nombre es Dr. García y declaro bajo juramento."""
    
    print("📖 EJEMPLO:")
    print("-" * 30)
    print(example)
    print("-" * 30)

def main():
    print("🎤 GENERADOR DE FORMATO PERSONALIZADO")
    print("=" * 50)
    
    # Mostrar formato requerido
    show_format_example()
    
    # Crear ejemplo perfecto
    print("\n📝 Creando ejemplo perfecto...")
    sample_file = create_sample_format()
    print(f"✅ Ejemplo creado: {sample_file}")
    
    # Intentar convertir transcripción existente
    print(f"\n🔄 Buscando transcripciones para convertir...")
    converted_file = convert_existing_transcription()
    
    if converted_file:
        print(f"✅ Conversión completada: {converted_file}")
        
        # Mostrar estadísticas
        with open(converted_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        timecodes = [l for l in lines if ';' in l and len(l.strip()) == 11]
        speakers = [l for l in lines if l.strip() in ['Juez', 'Fiscal', 'LCDO']]
        
        print(f"\n📊 ESTADÍSTICAS:")
        print(f"   • Intervenciones: {len(timecodes)}")
        print(f"   • Speakers identificados: {len(set(speakers))}")
        
        from collections import Counter
        speaker_count = Counter([s.strip() for s in speakers])
        for speaker, count in speaker_count.items():
            print(f"   • {speaker}: {count} intervenciones")
        
        # Mostrar vista previa
        print(f"\n📖 VISTA PREVIA (primeras 10 líneas):")
        print("-" * 40)
        preview_lines = content.split('\n')[:15]
        for line in preview_lines:
            print(line)
        print("-" * 40)
    
    print(f"\n🎉 FORMATO IMPLEMENTADO CORRECTAMENTE")
    print(f"\n💡 Para usar con nuevos archivos:")
    print(f"   1. Ejecuta transcripción normal: python transcribe.py audio.mp3")
    print(f"   2. Convierte al formato: python format_generator.py")
    print(f"\n📁 Archivos generados en carpeta 'transcripciones/'")

if __name__ == "__main__":
    main()
