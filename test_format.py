#!/usr/bin/env python3
"""
🧪 Prueba Rápida del Formato Personalizado
Genera una muestra del formato requerido usando el audio existente

Autor: John Guarenas
"""

import sys
from pathlib import Path
import time

# Agregar directorio actual
sys.path.append(str(Path(__file__).parent))

from logger import TranscriptionLogger
from transcribe_formatted import FormattedTranscriber

def quick_format_test():
    """Prueba rápida del formato personalizado"""
    
    # Buscar archivo de transcripción existente
    transcription_files = list(Path("transcripciones").glob("*.txt"))
    
    if not transcription_files:
        print("❌ No se encontraron transcripciones existentes")
        print("💡 Ejecuta primero una transcripción normal con:")
        print("   python transcribe.py audio_file.mp3")
        return False
    
    # Usar la transcripción más reciente
    latest_file = max(transcription_files, key=lambda p: p.stat().st_mtime)
    print(f"📄 Usando transcripción: {latest_file.name}")
    
    # Leer contenido
    with open(latest_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Inicializar transcriptor formateado
    logger = TranscriptionLogger(Path("logs"))
    transcriber = FormattedTranscriber(logger)
    
    print("🔄 Convirtiendo a formato personalizado...")
    
    # Aplicar formato personalizado
    formatted_text = transcriber.process_transcription_to_format(content)
    
    # Guardar resultado
    output_file = Path("transcripciones") / f"FORMAT_TEST_{int(time.time())}.txt"
    transcriber.save_formatted_transcription(formatted_text, output_file)
    
    print(f"✅ Formato aplicado exitosamente")
    print(f"📁 Archivo generado: {output_file}")
    
    # Mostrar vista previa del formato
    lines = formatted_text.split('\n')
    preview_lines = []
    count = 0
    
    for line in lines:
        preview_lines.append(line)
        if line.strip() == "" and len(preview_lines) > 10:
            count += 1
            if count >= 3:  # Mostrar 3 entradas completas
                break
    
    print(f"\n📖 VISTA PREVIA DEL FORMATO:")
    print("=" * 60)
    for line in preview_lines:
        print(line)
    print("=" * 60)
    
    print(f"\n📊 ESTADÍSTICAS:")
    all_lines = formatted_text.split('\n')
    timecode_lines = [l for l in all_lines if ';' in l and len(l) == 11]
    speaker_lines = [l for l in all_lines if l.strip() in ['Juez', 'Fiscal', 'LCDO', 'Testigo']]
    
    print(f"   • Total líneas: {len(all_lines)}")
    print(f"   • Timecodes: {len(timecode_lines)}")
    print(f"   • Intervenciones de speakers: {len(speaker_lines)}")
    
    # Contar speakers
    from collections import Counter
    speaker_count = Counter([l.strip() for l in all_lines if l.strip() in ['Juez', 'Fiscal', 'LCDO', 'Testigo']])
    
    if speaker_count:
        print(f"   • Distribución de speakers:")
        for speaker, count in speaker_count.items():
            print(f"     - {speaker}: {count} intervenciones")
    
    return True

def create_sample_format():
    """Crea un ejemplo del formato esperado"""
    
    sample_content = """# Transcripción con Formato Personalizado
# Fecha: 2025-08-19 14:30:00
# Sistema: HearingsWhisper v2.0
# Formato: Timecode | Speaker | Transcripción

00;00;00;00
Juez
Buenos días. Se abre la sesión del tribunal. Caso número PPR versus Erica Marie Erickson.

00;00;30;00
Fiscal
Buenos días Su Señoría. El Ministerio Público está listo para proceder con la presentación del caso.

00;01;00;00
LCDO
Buenos días Su Señoría. La defensa está presente y lista para proceder.

00;01;30;00
Juez
Muy bien. Fiscal, puede comenzar con su alegato de apertura.

00;02;00;00
Fiscal
Gracias Su Señoría. El pueblo demostrará que la acusada...

00;02;45;00
LCDO
Protesto Su Señoría. El fiscal está haciendo aseveraciones que no están en evidencia.

00;03;00;00
Juez
Sostenido. Fiscal, limítese a los hechos que va a probar.

00;03;30;00
Fiscal
Entendido Su Señoría. El pueblo presentará evidencia que muestra...
"""
    
    sample_file = Path("transcripciones") / "FORMATO_EJEMPLO.txt"
    sample_file.parent.mkdir(exist_ok=True)
    
    with open(sample_file, 'w', encoding='utf-8') as f:
        f.write(sample_content)
    
    print(f"📝 Ejemplo de formato creado en: {sample_file}")
    return sample_file

if __name__ == "__main__":
    print("🧪 PRUEBA DE FORMATO PERSONALIZADO")
    print("=" * 50)
    
    # Crear ejemplo del formato
    sample_file = create_sample_format()
    
    print(f"\n📋 FORMATO REQUERIDO:")
    print("   1. Timecode: 00;00;00;00 (horas;minutos;segundos;frames)")
    print("   2. Speaker: Juez / Fiscal / LCDO / Testigo")
    print("   3. Transcripción: Texto de lo que dijo")
    print("   4. Línea en blanco")
    
    # Intentar prueba con transcripción existente
    print(f"\n🔄 Probando conversión con archivo existente...")
    success = quick_format_test()
    
    if success:
        print(f"\n🎉 ¡Formato implementado correctamente!")
        print(f"\n💡 Para usar con nuevos archivos:")
        print(f"   python transcribe_formatted.py audio_file.mp3")
    else:
        print(f"\n📝 Se creó un ejemplo del formato en: {sample_file}")
        print(f"   Revisa este archivo para ver exactamente cómo se ve el formato.")
    
    print(f"\n✨ El sistema está listo para generar transcripciones en tu formato personalizado!")
