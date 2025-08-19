#!/usr/bin/env python3
"""
🎤 Transcriptor con Formato Personalizado
Sistema que genera transcripciones en el formato exacto requerido:
- Timecode (00;00;00;00)
- Speaker
- Transcripción

Autor: John Guarenas
Proyecto: HearingsWhisper
"""

import os
import sys
from pathlib import Path
import time
import json
from datetime import datetime
import argparse

# Importar nuestros módulos existentes
from logger import TranscriptionLogger
from config import Config
from transcribe import WhisperTranscriber
from audio_utils import AudioProcessor

class FormattedTranscriber:
    """Transcriptor que genera formato personalizado con simulación de diarización"""
    
    def __init__(self, logger: TranscriptionLogger):
        self.logger = logger
        self.config = Config.from_env()
        self.whisper_transcriber = WhisperTranscriber(self.config)
        self.audio_processor = AudioProcessor(logger)
    
    def seconds_to_timecode(self, seconds: float) -> str:
        """
        Convierte segundos a formato timecode HH;MM;SS;FF
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        frames = int((seconds % 1) * 25)  # 25 fps
        
        return f"{hours:02d};{minutes:02d};{secs:02d};{frames:02d}"
    
    def detect_speaker_changes(self, text: str, timestamp: float, speaker_assignments: dict, next_speaker_number: list) -> str:
        """
        Algoritmo mejorado para detectar cambios de speaker basado en patrones
        Incluye manejo de speakers adicionales (testigos, expertos, otros participantes)
        """
        # Patrones comunes que indican speaker judicial
        judge_patterns = [
            "su señoría", "el tribunal", "la corte", "se declara", 
            "se ordena", "este tribunal", "la sala", "orden", "honorable"
        ]
        
        # Patrones del fiscal
        fiscal_patterns = [
            "el ministerio público", "fiscal", "la fiscalía", 
            "presentamos", "solicitamos al tribunal", "pueblo", "estado"
        ]
        
        # Patrones del abogado defensor (LCDO)
        defense_patterns = [
            "la defensa", "mi cliente", "solicito", "objection",
            "protesto", "licenciado", "abogado", "representada"
        ]
        
        # Patrones de testigos/otros participantes
        witness_patterns = [
            "testigo", "declaro", "juro", "afirmo", "yo vi", "yo estaba",
            "doctor", "doctora", "señor", "señora", "mi nombre es"
        ]
        
        text_lower = text.lower()
        
        # Determinar speaker basado en contenido
        if any(pattern in text_lower for pattern in judge_patterns):
            return "Juez"
        elif any(pattern in text_lower for pattern in fiscal_patterns):
            return "Fiscal"
        elif any(pattern in text_lower for pattern in defense_patterns):
            return "LCDO"
        elif any(pattern in text_lower for pattern in witness_patterns):
            # Asignar Speaker numerado para testigos/otros
            minute_group = int(timestamp // 120)  # Cada 2 minutos
            witness_key = f"witness_{minute_group}"
            if witness_key not in speaker_assignments:
                speaker_assignments[witness_key] = f"Speaker {next_speaker_number[0]}"
                next_speaker_number[0] += 1
            return speaker_assignments[witness_key]
        else:
            # Para otros casos, usar rotación inteligente
            minute_group = int(timestamp // 180)  # Cada 3 minutos
            
            # Rotación entre roles conocidos y speakers adicionales
            rotation = minute_group % 6
            if rotation == 0:
                return "Juez"
            elif rotation == 1:
                return "Fiscal"
            elif rotation == 2:
                return "LCDO"
            else:
                # Asignar Speaker numerado para otros participantes
                speaker_key = f"rotation_{minute_group}"
                if speaker_key not in speaker_assignments:
                    speaker_assignments[speaker_key] = f"Speaker {next_speaker_number[0]}"
                    next_speaker_number[0] += 1
                return speaker_assignments[speaker_key]
    
    def process_transcription_to_format(self, transcription_text: str, speaker_mapping: dict = None) -> str:
        """
        Convierte transcripción plana a formato con timecodes y speakers
        """
        lines = transcription_text.split('\n')
        formatted_output = []
        
        # Header
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = f"""# Transcripción con Formato Personalizado
# Fecha: {timestamp}
# Sistema: HearingsWhisper v2.0
# Formato: Timecode | Speaker | Transcripción

"""
        formatted_output.append(header)
        
        current_time = 0.0
        chunk_duration = 30.0  # Cambiar speaker cada 30 segundos aproximadamente
        speaker_assignments = {}  # Para rastrear speakers adicionales
        next_speaker_number = [1]  # Lista para pasar por referencia
        
        # Procesar cada línea de transcripción
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Generar timecode
            timecode = self.seconds_to_timecode(current_time)
            
            # Detectar speaker (usando mapeo si existe, sino algoritmo mejorado)
            if speaker_mapping:
                # Si hay mapeo personalizado, usarlo
                speaker_key = f"segment_{len(formatted_output)}"
                speaker = speaker_mapping.get(speaker_key, 
                    self.detect_speaker_changes(line, current_time, speaker_assignments, next_speaker_number))
            else:
                # Usar detección automática mejorada
                speaker = self.detect_speaker_changes(line, current_time, speaker_assignments, next_speaker_number)
            
            # Agregar al formato
            formatted_output.append(f"{timecode}")
            formatted_output.append(f"{speaker}")
            formatted_output.append(f"{line}")
            formatted_output.append("")  # Línea en blanco
            
            # Avanzar tiempo
            current_time += chunk_duration
        
        return '\n'.join(formatted_output)
    
    def transcribe_and_format(self, audio_path: Path, language: str = "es", chunk_size: int = 300) -> str:
        """
        Transcribe audio y aplica formato personalizado
        """
        self.logger.info(f"🎤 Transcribiendo con formato personalizado: {audio_path.name}")
        
        # Usar el transcriptor existente
        transcription = self.whisper_transcriber.transcribe_large_file(audio_path, language, chunk_size)
        
        # Aplicar formato personalizado
        formatted_text = self.process_transcription_to_format(transcription)
        
        return formatted_text
    
    def save_formatted_transcription(self, formatted_text: str, output_path: Path) -> Path:
        """Guarda la transcripción formateada"""
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(formatted_text)
        
        self.logger.info(f"💾 Transcripción formateada guardada: {output_path}")
        return output_path

def create_speaker_mapping_interface():
    """Crea interfaz para mapeo manual de speakers"""
    print("\n" + "="*60)
    print("🎭 CONFIGURACIÓN DE SPEAKERS")
    print("="*60)
    print("\nEste sistema puede detectar automáticamente cambios de speaker")
    print("o puedes crear un mapeo personalizado.")
    print("\n📝 Speakers detectados automáticamente:")
    print("   • Juez (detecta: 'Su Señoría', 'tribunal', 'honorable')")
    print("   • Fiscal (detecta: 'Ministerio Público', 'pueblo', 'fiscalía')")  
    print("   • LCDO (detecta: 'defensa', 'licenciado', 'mi cliente')")
    print("   • Speaker 1, 2, 3, etc. (testigos, expertos, otros participantes)")
    
    use_auto = input("\n¿Usar detección automática de speakers? (s/n): ").lower().strip()
    
    if use_auto == 'n':
        print("\n📋 Crear mapeo manual:")
        print("(Presiona Enter para terminar)")
        
        mapping = {}
        segment_num = 0
        
        while True:
            speaker = input(f"Speaker para segmento {segment_num + 1}: ").strip()
            if not speaker:
                break
            mapping[f"segment_{segment_num}"] = speaker
            segment_num += 1
        
        if mapping:
            mapping_file = Path("speaker_mapping_custom.json")
            with open(mapping_file, 'w', encoding='utf-8') as f:
                json.dump(mapping, f, indent=2, ensure_ascii=False)
            print(f"✅ Mapeo guardado en: {mapping_file}")
            return mapping
    
    print("🤖 Usando detección automática de speakers")
    print("   → Juez, Fiscal, LCDO + Speaker 1, 2, 3, etc.")
    return None

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Transcriptor con formato personalizado')
    parser.add_argument('audio_file', help='Archivo de audio a transcribir')
    parser.add_argument('--language', '-l', default='es', help='Idioma (default: es)')
    parser.add_argument('--output', '-o', help='Archivo de salida')
    parser.add_argument('--chunk-size', '-c', type=int, default=300, help='Tamaño de chunks en segundos')
    parser.add_argument('--auto-speakers', action='store_true', help='Usar detección automática sin preguntar')
    
    args = parser.parse_args()
    
    # Verificar archivo
    audio_path = Path(args.audio_file)
    if not audio_path.exists():
        print(f"❌ No se encontró el archivo: {audio_path}")
        sys.exit(1)
    
    # Inicializar
    logs_folder = Path("logs")
    logger = TranscriptionLogger(logs_folder)
    transcriber = FormattedTranscriber(logger)
    
    try:
        print("🚀 TRANSCRIPTOR CON FORMATO PERSONALIZADO")
        print("=" * 50)
        print(f"📁 Archivo: {audio_path.name}")
        print(f"📊 Tamaño: {audio_path.stat().st_size / (1024*1024):.1f} MB")
        
        # Configurar speakers
        speaker_mapping = None
        if not args.auto_speakers:
            speaker_mapping = create_speaker_mapping_interface()
        
        # Transcribir
        start_time = time.time()
        
        formatted_text = transcriber.transcribe_and_format(
            audio_path, 
            args.language, 
            args.chunk_size
        )
        
        # Determinar archivo de salida
        if args.output:
            output_path = Path(args.output)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = Path("transcripciones") / f"{audio_path.stem}_formatted_{timestamp}.txt"
        
        # Guardar
        final_file = transcriber.save_formatted_transcription(formatted_text, output_path)
        
        # Estadísticas
        processing_time = time.time() - start_time
        lines = len(formatted_text.split('\n'))
        
        print(f"\n✅ TRANSCRIPCIÓN COMPLETADA")
        print(f"📄 Archivo: {final_file}")
        print(f"📝 Líneas generadas: {lines}")
        print(f"⏱️ Tiempo: {processing_time/60:.1f} minutos")
        
        # Mostrar vista previa
        print(f"\n📖 VISTA PREVIA:")
        print("-" * 40)
        with open(final_file, 'r', encoding='utf-8') as f:
            preview = f.read().split('\n')[:15]
        
        for line in preview:
            print(line)
        
        if len(formatted_text.split('\n')) > 15:
            print("...")
        
        print(f"\n🎉 Listo! Tu transcripción está en: {final_file}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
