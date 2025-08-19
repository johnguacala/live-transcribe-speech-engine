#!/usr/bin/env python3
"""
🎤 Módulo de Diarización con WhisperX
Sistema avanzado para transcripción con identificación de speakers

Autor: John Guarenas
Proyecto: HearingsWhisper
"""

import whisperx
import torch
from pathlib import Path
import time
from typing import List, Dict, Tuple
import json
from datetime import datetime, timedelta
import re

from logger import TranscriptionLogger

class WhisperXDiarizer:
    """Transcriptor con diarización usando WhisperX"""
    
    def __init__(self, logger: TranscriptionLogger):
        self.logger = logger
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.compute_type = "float16" if torch.cuda.is_available() else "int8"
        
        self.logger.info(f"🔧 Inicializando WhisperX en dispositivo: {self.device}")
        
        # Modelos que se cargarán bajo demanda
        self.asr_model = None
        self.diarize_model = None
        self.align_model = None
        self.metadata = None
    
    def load_models(self):
        """Carga todos los modelos necesarios"""
        try:
            self.logger.info("📥 Cargando modelo ASR (Whisper)...")
            self.asr_model = whisperx.load_model("large-v2", self.device, compute_type=self.compute_type)
            
            self.logger.info("📥 Cargando modelo de diarización...")
            self.diarize_model = whisperx.DiarizationPipeline(use_auth_token=None, device=self.device)
            
            self.logger.info("✅ Modelos cargados exitosamente")
            
        except Exception as e:
            self.logger.error(f"Error cargando modelos WhisperX: {e}")
            raise
    
    def transcribe_with_diarization(self, audio_path: Path, language: str = "es") -> Dict:
        """
        Transcribe audio con diarización completa
        
        Args:
            audio_path: Path al archivo de audio
            language: Idioma del audio
        
        Returns:
            Diccionario con transcripción y información de speakers
        """
        if not self.asr_model:
            self.load_models()
        
        self.logger.info(f"🎤 Iniciando transcripción con diarización: {audio_path.name}")
        
        try:
            # 1. Transcripción inicial
            self.logger.info("📝 Paso 1: Transcribiendo audio...")
            audio = whisperx.load_audio(str(audio_path))
            result = self.asr_model.transcribe(audio, batch_size=16)
            
            # 2. Alineación (mejora la precisión de los timestamps)
            self.logger.info("⏱️ Paso 2: Alineando timestamps...")
            model_a, metadata = whisperx.load_align_model(language_code=language, device=self.device)
            result = whisperx.align(result["segments"], model_a, metadata, audio, self.device, return_char_alignments=False)
            
            # 3. Diarización (identificación de speakers)
            self.logger.info("👥 Paso 3: Identificando speakers...")
            diarize_segments = self.diarize_model(audio)
            result = whisperx.assign_word_speakers(diarize_segments, result)
            
            self.logger.info(f"✅ Transcripción completada con {len(result['segments'])} segmentos")
            
            return {
                'segments': result['segments'],
                'language': language,
                'audio_path': str(audio_path),
                'processing_time': time.time(),
                'device_used': self.device
            }
            
        except Exception as e:
            self.logger.error(f"Error en transcripción con diarización: {e}")
            raise
    
    def format_timecode(self, seconds: float) -> str:
        """
        Convierte segundos a formato timecode HH;MM;SS;FF
        
        Args:
            seconds: Tiempo en segundos
            
        Returns:
            String en formato 00;00;00;00
        """
        # Convertir a horas, minutos, segundos y frames (asumiendo 25 fps)
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        frames = int((seconds % 1) * 25)  # 25 frames por segundo
        
        return f"{hours:02d};{minutes:02d};{secs:02d};{frames:02d}"
    
    def process_segments_to_formatted_text(self, transcription_result: Dict, speaker_mapping: Dict = None) -> str:
        """
        Convierte los segmentos a formato de texto personalizado
        
        Args:
            transcription_result: Resultado de la transcripción
            speaker_mapping: Mapeo de speakers (ej: {"SPEAKER_00": "Juez", "SPEAKER_01": "Fiscal"})
            
        Returns:
            Texto formateado con timecodes y speakers
        """
        segments = transcription_result['segments']
        formatted_lines = []
        
        # Header con información del archivo
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        audio_path = Path(transcription_result['audio_path']).name
        
        header = f"""# Transcripción con Diarización - {audio_path}
# Fecha: {timestamp}
# Modelo: WhisperX large-v2
# Idioma: {transcription_result['language']}
# Dispositivo: {transcription_result['device_used']}

"""
        formatted_lines.append(header)
        
        current_speaker = None
        current_text_parts = []
        current_start_time = None
        
        for segment in segments:
            speaker = segment.get('speaker', 'SPEAKER_UNKNOWN')
            text = segment.get('text', '').strip()
            start_time = segment.get('start', 0)
            
            # Aplicar mapeo de speakers si existe
            if speaker_mapping and speaker in speaker_mapping:
                display_speaker = speaker_mapping[speaker]
            else:
                display_speaker = speaker
            
            # Si cambia el speaker o es el primer segmento
            if speaker != current_speaker:
                # Guardar el segmento anterior si existe
                if current_speaker is not None and current_text_parts:
                    timecode = self.format_timecode(current_start_time)
                    combined_text = ' '.join(current_text_parts).strip()
                    
                    formatted_lines.append(f"{timecode}")
                    formatted_lines.append(f"{current_display_speaker}")
                    formatted_lines.append(f"{combined_text}")
                    formatted_lines.append("")  # Línea en blanco
                
                # Iniciar nuevo segmento
                current_speaker = speaker
                current_display_speaker = display_speaker
                current_text_parts = [text] if text else []
                current_start_time = start_time
            else:
                # Continuar con el mismo speaker
                if text:
                    current_text_parts.append(text)
        
        # Agregar el último segmento
        if current_speaker is not None and current_text_parts:
            timecode = self.format_timecode(current_start_time)
            combined_text = ' '.join(current_text_parts).strip()
            
            formatted_lines.append(f"{timecode}")
            formatted_lines.append(f"{current_display_speaker}")
            formatted_lines.append(f"{combined_text}")
        
        return '\n'.join(formatted_lines)
    
    def get_speakers_summary(self, transcription_result: Dict) -> Dict:
        """
        Obtiene un resumen de los speakers detectados
        
        Args:
            transcription_result: Resultado de la transcripción
            
        Returns:
            Diccionario con información de speakers
        """
        segments = transcription_result['segments']
        speakers = {}
        
        for segment in segments:
            speaker = segment.get('speaker', 'SPEAKER_UNKNOWN')
            text = segment.get('text', '').strip()
            duration = segment.get('end', 0) - segment.get('start', 0)
            
            if speaker not in speakers:
                speakers[speaker] = {
                    'total_duration': 0,
                    'segment_count': 0,
                    'first_words': text[:50] if text else '',
                    'total_words': 0
                }
            
            speakers[speaker]['total_duration'] += duration
            speakers[speaker]['segment_count'] += 1
            speakers[speaker]['total_words'] += len(text.split()) if text else 0
        
        return speakers
    
    def create_speaker_mapping_prompt(self, speakers_summary: Dict) -> str:
        """
        Crea un prompt para que el usuario asigne nombres a los speakers
        
        Args:
            speakers_summary: Resumen de speakers detectados
            
        Returns:
            String con información para asignar nombres
        """
        prompt_lines = [
            "🎤 SPEAKERS DETECTADOS:",
            "=" * 50,
            ""
        ]
        
        for speaker, info in speakers_summary.items():
            duration_mins = info['total_duration'] / 60
            prompt_lines.extend([
                f"Speaker: {speaker}",
                f"  • Duración total: {duration_mins:.1f} minutos",
                f"  • Segmentos: {info['segment_count']}",
                f"  • Palabras totales: {info['total_words']}",
                f"  • Primeras palabras: \"{info['first_words']}...\"",
                ""
            ])
        
        prompt_lines.extend([
            "📝 ASIGNACIÓN DE NOMBRES:",
            "Para asignar nombres reales a los speakers, crea un archivo llamado",
            "'speaker_mapping.json' con el siguiente formato:",
            "",
            "{",
            '  "SPEAKER_00": "Juez",',
            '  "SPEAKER_01": "Fiscal",', 
            '  "SPEAKER_02": "LCDO"',
            "}",
            "",
            "El sistema aplicará automáticamente estos nombres en la transcripción final."
        ])
        
        return '\n'.join(prompt_lines)
    
    def save_transcription(self, transcription_result: Dict, output_path: Path, speaker_mapping: Dict = None) -> Path:
        """
        Guarda la transcripción en formato de texto personalizado
        
        Args:
            transcription_result: Resultado de la transcripción
            output_path: Path donde guardar el archivo
            speaker_mapping: Mapeo opcional de speakers
            
        Returns:
            Path del archivo guardado
        """
        formatted_text = self.process_segments_to_formatted_text(transcription_result, speaker_mapping)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(formatted_text)
        
        self.logger.info(f"💾 Transcripción guardada en: {output_path}")
        return output_path
