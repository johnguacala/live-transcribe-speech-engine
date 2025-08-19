#!/usr/bin/env python3
"""
🧪 Script de Prueba - Transcripción con Diarización
Prueba rápida del nuevo sistema con el audio de ejemplo

Autor: John Guarenas
"""

import os
import sys
from pathlib import Path
import time

# Agregar directorio actual al path
sys.path.append(str(Path(__file__).parent))

from logger import TranscriptionLogger
from diarization import WhisperXDiarizer

def test_diarization():
    """Prueba básica del sistema de diarización"""
    
    # Buscar archivo de audio de prueba
    test_files = [
        "audios/MAY_SALA201_PPR VS. ERICA MARIE ERICKSON_20240607_094257.mp3",
        "audios/chunk_000.mp3",
        "audios/test_audio.mp3"
    ]
    
    audio_path = None
    for file_path in test_files:
        if Path(file_path).exists():
            audio_path = Path(file_path)
            break
    
    if not audio_path:
        print("❌ No se encontró archivo de audio para prueba")
        print("📁 Archivos buscados:")
        for file_path in test_files:
            print(f"   - {file_path}")
        return
    
    print(f"🎤 Probando con archivo: {audio_path.name}")
    print(f"📊 Tamaño: {audio_path.stat().st_size / (1024*1024):.1f} MB")
    
    # Inicializar componentes
    logger = TranscriptionLogger()
    diarizer = WhisperXDiarizer(logger)
    
    try:
        print("\n🚀 Iniciando prueba de diarización...")
        start_time = time.time()
        
        # Transcribir con diarización (solo primeros 60 segundos para prueba)
        print("📝 Transcribiendo y detectando speakers...")
        result = diarizer.transcribe_with_diarization(audio_path, language="es")
        
        # Obtener resumen de speakers
        speakers = diarizer.get_speakers_summary(result)
        
        print(f"\n👥 Speakers detectados: {len(speakers)}")
        for speaker, info in speakers.items():
            duration_mins = info['total_duration'] / 60
            print(f"   {speaker}: {duration_mins:.1f}min ({info['segment_count']} segmentos)")
        
        # Crear mapeo de ejemplo
        speaker_mapping = {}
        speaker_names = ["Juez", "Fiscal", "LCDO", "Testigo", "Otro"]
        for i, speaker in enumerate(speakers.keys()):
            if i < len(speaker_names):
                speaker_mapping[speaker] = speaker_names[i]
            else:
                speaker_mapping[speaker] = f"Speaker_{i+1}"
        
        print(f"\n📝 Mapeo de ejemplo:")
        for original, mapped in speaker_mapping.items():
            print(f"   {original} → {mapped}")
        
        # Generar texto formateado
        output_path = Path("transcripciones") / f"test_diarization_{int(time.time())}.txt"
        output_path.parent.mkdir(exist_ok=True)
        
        final_file = diarizer.save_transcription(result, output_path, speaker_mapping)
        
        processing_time = time.time() - start_time
        
        print(f"\n✅ Prueba completada en {processing_time:.1f} segundos")
        print(f"📄 Archivo generado: {final_file}")
        
        # Mostrar primeras líneas del resultado
        with open(final_file, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            preview_lines = lines[:20]  # Primeras 20 líneas
        
        print(f"\n📖 Vista previa del archivo:")
        print("=" * 50)
        for line in preview_lines:
            print(line)
        if len(lines) > 20:
            print(f"... ({len(lines) - 20} líneas más)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 PRUEBA DE DIARIZACIÓN - HearingsWhisper")
    print("=" * 50)
    
    success = test_diarization()
    
    if success:
        print("\n🎉 ¡Prueba exitosa!")
        print("\n💡 Para usar el sistema completo:")
        print("   python transcribe_with_diarization.py audio_file.mp3")
    else:
        print("\n💥 La prueba falló. Revisa los errores arriba.")
