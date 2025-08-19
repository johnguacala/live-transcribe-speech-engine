#!/usr/bin/env python3
"""
🎤 Transcriptor Avanzado con Diarización
Sistema completo para transcripción de audiencias legales con identificación de speakers

Autor: John Guarenas  
Proyecto: HearingsWhisper
Fecha: Agosto 2025
"""

import os
import sys
from pathlib import Path
import argparse
import json
from datetime import datetime
import time

# Importar nuestros módulos
from logger import TranscriptionLogger
from config import Config
from audio_utils import AudioProcessor
from diarization import WhisperXDiarizer

def load_speaker_mapping(mapping_file: Path) -> dict:
    """Carga el mapeo de speakers desde archivo JSON"""
    if mapping_file.exists():
        try:
            with open(mapping_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Error cargando mapeo de speakers: {e}")
    return {}

def create_output_filename(audio_path: Path, suffix: str = "diarized") -> Path:
    """Crea el nombre del archivo de salida"""
    base_name = audio_path.stem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return Path("transcripciones") / f"{base_name}_{suffix}_{timestamp}.txt"

def main():
    """Función principal del transcriptor con diarización"""
    
    # Configurar argumentos de línea de comandos
    parser = argparse.ArgumentParser(description='Transcriptor con identificación de speakers')
    parser.add_argument('audio_file', help='Archivo de audio a transcribir')
    parser.add_argument('--language', '-l', default='es', help='Idioma del audio (default: es)')
    parser.add_argument('--speaker-mapping', '-s', help='Archivo JSON con mapeo de speakers')
    parser.add_argument('--output', '-o', help='Archivo de salida (opcional)')
    parser.add_argument('--chunk-size', '-c', type=int, default=300, help='Tamaño de chunks en segundos')
    
    args = parser.parse_args()
    
    # Verificar archivo de entrada
    audio_path = Path(args.audio_file)
    if not audio_path.exists():
        print(f"❌ Error: No se encontró el archivo {audio_path}")
        sys.exit(1)
    
    # Inicializar componentes
    config = Config()
    logger = TranscriptionLogger()
    audio_processor = AudioProcessor(logger)
    diarizer = WhisperXDiarizer(logger)
    
    # Crear directorio de salida
    output_dir = Path("transcripciones")
    output_dir.mkdir(exist_ok=True)
    
    try:
        logger.info("🚀 INICIANDO TRANSCRIPCIÓN CON DIARIZACIÓN")
        logger.info(f"📁 Archivo: {audio_path.name}")
        logger.info(f"🌍 Idioma: {args.language}")
        logger.info(f"⚙️ Chunks: {args.chunk_size}s")
        
        start_time = time.time()
        
        # Cargar mapeo de speakers si existe
        speaker_mapping = {}
        if args.speaker_mapping:
            mapping_path = Path(args.speaker_mapping)
            speaker_mapping = load_speaker_mapping(mapping_path)
            logger.info(f"👥 Mapeo de speakers cargado: {len(speaker_mapping)} speakers")
        
        # Verificar tamaño del archivo
        file_size_mb = audio_path.stat().st_size / (1024 * 1024)
        duration_info = audio_processor.get_audio_duration(audio_path)
        
        logger.info(f"📊 Tamaño del archivo: {file_size_mb:.1f} MB")
        logger.info(f"⏱️ Duración estimada: {duration_info['duration']:.1f} segundos ({duration_info['duration']/60:.1f} minutos)")
        
        # Procesar archivo grande con chunks o archivo completo
        if duration_info['duration'] > args.chunk_size:
            logger.info(f"📦 Archivo largo detectado, procesando por chunks de {args.chunk_size}s")
            
            # Dividir en chunks
            chunks = audio_processor.split_audio_into_chunks(audio_path, args.chunk_size)
            logger.info(f"🔀 Archivo dividido en {len(chunks)} chunks")
            
            # Procesar cada chunk
            all_segments = []
            total_duration_offset = 0
            
            for i, chunk_path in enumerate(chunks, 1):
                logger.info(f"🎯 Procesando chunk {i}/{len(chunks)}: {chunk_path.name}")
                
                # Transcribir chunk
                chunk_result = diarizer.transcribe_with_diarization(chunk_path, args.language)
                
                # Ajustar timestamps con offset acumulado
                for segment in chunk_result['segments']:
                    segment['start'] += total_duration_offset
                    segment['end'] += total_duration_offset
                
                all_segments.extend(chunk_result['segments'])
                total_duration_offset += args.chunk_size
                
                # Limpiar chunk temporal
                chunk_path.unlink()
                
                logger.info(f"✅ Chunk {i} completado ({len(chunk_result['segments'])} segmentos)")
            
            # Crear resultado final
            final_result = {
                'segments': all_segments,
                'language': args.language,
                'audio_path': str(audio_path),
                'processing_time': time.time() - start_time,
                'device_used': diarizer.device,
                'chunks_processed': len(chunks)
            }
            
        else:
            logger.info("📝 Archivo pequeño, procesando completo")
            final_result = diarizer.transcribe_with_diarization(audio_path, args.language)
        
        # Generar resumen de speakers
        speakers_summary = diarizer.get_speakers_summary(final_result)
        logger.info(f"👥 Speakers detectados: {len(speakers_summary)}")
        
        # Si no hay mapeo de speakers, mostrar información para crear uno
        if not speaker_mapping and speakers_summary:
            speaker_prompt = diarizer.create_speaker_mapping_prompt(speakers_summary)
            print("\n" + speaker_prompt + "\n")
            
            # Crear archivo de ejemplo de mapeo
            example_mapping = {}
            for i, speaker in enumerate(speakers_summary.keys()):
                example_mapping[speaker] = f"Speaker_{i+1}"
            
            example_path = output_dir / "speaker_mapping_example.json"
            with open(example_path, 'w', encoding='utf-8') as f:
                json.dump(example_mapping, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📝 Ejemplo de mapeo creado en: {example_path}")
        
        # Determinar archivo de salida
        if args.output:
            output_path = Path(args.output)
        else:
            output_path = create_output_filename(audio_path)
        
        # Guardar transcripción formateada
        final_output = diarizer.save_transcription(final_result, output_path, speaker_mapping)
        
        # Estadísticas finales
        processing_time = time.time() - start_time
        total_segments = len(final_result['segments'])
        
        logger.info("🎉 TRANSCRIPCIÓN COMPLETADA")
        logger.info(f"📄 Archivo generado: {final_output}")
        logger.info(f"📊 Segmentos totales: {total_segments}")
        logger.info(f"⏱️ Tiempo de procesamiento: {processing_time/60:.1f} minutos")
        logger.info(f"👥 Speakers detectados: {len(speakers_summary)}")
        
        # Mostrar estadísticas de speakers
        print("\n📈 RESUMEN DE SPEAKERS:")
        print("=" * 40)
        for speaker, info in speakers_summary.items():
            mapped_name = speaker_mapping.get(speaker, speaker)
            duration_mins = info['total_duration'] / 60
            print(f"{mapped_name}: {duration_mins:.1f}min ({info['segment_count']} segmentos)")
        
        print(f"\n✅ Transcripción guardada en: {final_output}")
        
        if not speaker_mapping:
            print("\n💡 Para personalizar los nombres de speakers, edita 'speaker_mapping_example.json' y úsalo con --speaker-mapping")
            
    except KeyboardInterrupt:
        logger.info("❌ Transcripción cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error durante la transcripción: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
