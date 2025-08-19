#!/usr/bin/env python3
"""
🎧 Transcriptor de Audio con OpenAI Whisper
Optimizado para archivos largos de español de Puerto Rico

Autor: John Guarenas
Proyecto: HearingsWhisper
"""

import openai
from pathlib import Path
import time
from typing import List, Dict
import json
from datetime import datetime

from config import Config
from logger import TranscriptionLogger
from audio_utils import AudioProcessor

class WhisperTranscriber:
    """Transcriptor principal usando OpenAI Whisper API"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = TranscriptionLogger(config.logs_folder)
        self.audio_processor = AudioProcessor(self.logger)
        
        # Configurar OpenAI
        openai.api_key = config.openai_api_key
        
        # Verificar que las carpetas existan
        self._ensure_directories()
        
        # Verificar ffmpeg
        if not self.audio_processor.check_ffmpeg():
            self.logger.warning("⚠️  ffmpeg no está instalado. Archivos grandes no podrán ser procesados automáticamente.")
    
    def _ensure_directories(self):
        """Crea las carpetas necesarias si no existen"""
        for folder in [self.config.audio_folder, self.config.chunks_folder, 
                      self.config.transcriptions_folder, self.config.logs_folder]:
            folder.mkdir(exist_ok=True)
    
    def get_audio_files(self) -> List[Path]:
        """Obtiene lista de archivos de audio para procesar"""
        audio_extensions = {'.mp3', '.wav', '.m4a', '.flac', '.ogg'}
        audio_files = []
        
        for ext in audio_extensions:
            audio_files.extend(self.config.audio_folder.glob(f'*{ext}'))
        
        return sorted(audio_files)
    
    def transcribe_file(self, audio_path: Path, prompt: str = None) -> str:
        """
        Transcribe un archivo de audio individual
        
        Args:
            audio_path: Path al archivo de audio
            prompt: Prompt personalizado (opcional)
        
        Returns:
            Texto transcrito
        """
        if prompt is None:
            prompt = self.config.prompt_template
        
        try:
            with open(audio_path, "rb") as audio_file:
                self.logger.debug(f"Enviando {audio_path.name} a OpenAI...")
                
                response = openai.Audio.transcribe(
                    model=self.config.model,
                    file=audio_file,
                    response_format=self.config.response_format,
                    language=self.config.language,
                    prompt=prompt
                )
                
                return response if isinstance(response, str) else response.text
                
        except Exception as e:
            self.logger.error(f"Error transcribiendo {audio_path.name}", e)
            raise
    
    def process_large_file(self, audio_path: Path) -> str:
        """
        Procesa un archivo grande dividiéndolo en chunks
        
        Args:
            audio_path: Path al archivo de audio grande
        
        Returns:
            Transcripción completa concatenada
        """
        self.logger.info(f"📂 Procesando archivo grande: {audio_path.name}")
        
        # Dividir en chunks
        chunks = self.audio_processor.split_audio(
            audio_path, 
            self.config.chunks_folder,
            self.config.chunk_duration_minutes,
            self.config.overlap_seconds
        )
        
        transcriptions = []
        total_chunks = len(chunks)
        
        for i, chunk_path in enumerate(chunks, 1):
            try:
                self.logger.progress(i, total_chunks, "chunks")
                
                # Transcribir chunk
                chunk_text = self.transcribe_file(chunk_path)
                transcriptions.append(chunk_text)
                
                # Pequeña pausa para no saturar la API
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error procesando chunk {i}/{total_chunks}: {chunk_path.name}", e)
                # Continuar con el siguiente chunk
                transcriptions.append(f"[ERROR EN CHUNK {i}]")
        
        # Concatenar transcripciones
        full_transcription = self._merge_transcriptions(transcriptions)
        
        # Limpiar chunks temporales (opcional)
        self._cleanup_chunks(chunks)
        
        return full_transcription
    
    def _merge_transcriptions(self, transcriptions: List[str]) -> str:
        """Une las transcripciones de los chunks de manera inteligente"""
        if not transcriptions:
            return ""
        
        # Simplemente unir con espacios por ahora
        # TODO: Implementar lógica más sofisticada para detectar cortes de oraciones
        merged = " ".join(text.strip() for text in transcriptions if text.strip())
        
        # Limpiar espacios múltiples
        merged = " ".join(merged.split())
        
        return merged
    
    def _cleanup_chunks(self, chunk_paths: List[Path]):
        """Limpia los archivos de chunks temporales"""
        try:
            for chunk_path in chunk_paths:
                if chunk_path.exists():
                    chunk_path.unlink()
            
            # Remover carpeta de chunks si está vacía
            if chunk_paths and chunk_paths[0].parent.exists():
                try:
                    chunk_paths[0].parent.rmdir()
                except OSError:
                    pass  # Carpeta no vacía
                    
        except Exception as e:
            self.logger.warning(f"No se pudieron limpiar algunos chunks temporales: {e}")
    
    def save_transcription(self, text: str, original_audio_path: Path) -> Path:
        """Guarda la transcripción en un archivo de texto"""
        output_path = self.config.transcriptions_folder / f"{original_audio_path.stem}.txt"
        
        # Agregar metadata al inicio
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = f"""# Transcripción de {original_audio_path.name}
# Fecha: {timestamp}
# Modelo: {self.config.model}
# Idioma: {self.config.language}

"""
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(header + text)
        
        return output_path
    
    def calculate_cost_estimate(self, audio_files: List[Path]) -> Dict:
        """Calcula estimación de costos antes de procesar"""
        total_duration = 0
        file_info = []
        
        for audio_file in audio_files:
            try:
                duration = self.audio_processor.get_audio_duration(audio_file)
                size_mb = self.audio_processor.get_file_size_mb(audio_file)
                needs_split = self.audio_processor.needs_splitting(audio_file, self.config.max_file_size_mb)
                
                file_info.append({
                    'name': audio_file.name,
                    'duration_minutes': duration,
                    'size_mb': size_mb,
                    'needs_splitting': needs_split
                })
                
                total_duration += duration
                
            except Exception as e:
                self.logger.warning(f"No se pudo obtener información de {audio_file.name}: {e}")
        
        # Costo de OpenAI: $0.006 por minuto
        estimated_cost = total_duration * 0.006
        
        return {
            'total_files': len(audio_files),
            'total_duration_minutes': total_duration,
            'total_duration_hours': total_duration / 60,
            'estimated_cost_usd': estimated_cost,
            'files': file_info
        }
    
    def process_all_files(self, dry_run: bool = False) -> Dict:
        """
        Procesa todos los archivos de audio en la carpeta
        
        Args:
            dry_run: Si es True, solo calcula costos sin procesar
        
        Returns:
            Resumen del procesamiento
        """
        self.logger.info("🎵 Iniciando procesamiento de archivos de audio")
        
        audio_files = self.get_audio_files()
        
        if not audio_files:
            self.logger.warning(f"No se encontraron archivos de audio en {self.config.audio_folder}")
            return {'error': 'No audio files found'}
        
        # Calcular estimación de costos
        cost_info = self.calculate_cost_estimate(audio_files)
        
        self.logger.info(f"📊 Archivos encontrados: {cost_info['total_files']}")
        self.logger.info(f"⏱️  Duración total: {cost_info['total_duration_hours']:.1f} horas")
        self.logger.cost_estimate(cost_info['total_duration_minutes'])
        
        if dry_run:
            self.logger.info("🔍 Modo dry-run: solo mostrando estimaciones")
            return cost_info
        
        # Procesar archivos
        results = []
        start_time = time.time()
        
        for i, audio_file in enumerate(audio_files, 1):
            try:
                self.logger.info(f"🎧 Procesando {i}/{len(audio_files)}: {audio_file.name}")
                
                # Determinar si necesita división
                if self.audio_processor.needs_splitting(audio_file, self.config.max_file_size_mb):
                    transcription = self.process_large_file(audio_file)
                else:
                    transcription = self.transcribe_file(audio_file)
                
                # Guardar transcripción
                output_path = self.save_transcription(transcription, audio_file)
                
                # Calcular costo aproximado
                duration = next((f['duration_minutes'] for f in cost_info['files'] 
                               if f['name'] == audio_file.name), 0)
                cost = duration * 0.006
                
                self.logger.transcription_completed(audio_file.name, duration, cost)
                
                results.append({
                    'file': audio_file.name,
                    'status': 'success',
                    'output_path': str(output_path),
                    'duration_minutes': duration,
                    'estimated_cost': cost
                })
                
            except Exception as e:
                self.logger.error(f"Error procesando {audio_file.name}", e)
                results.append({
                    'file': audio_file.name,
                    'status': 'error',
                    'error': str(e)
                })
        
        total_time = time.time() - start_time
        successful = len([r for r in results if r['status'] == 'success'])
        
        self.logger.info(f"🎉 Procesamiento completado: {successful}/{len(audio_files)} archivos exitosos")
        self.logger.info(f"⏱️  Tiempo total: {total_time/60:.1f} minutos")
        
        return {
            'summary': cost_info,
            'results': results,
            'processing_time_minutes': total_time / 60,
            'success_rate': successful / len(audio_files) if audio_files else 0
        }


def main():
    """Función principal"""
    try:
        # Cargar configuración
        config = Config.from_env()
        
        if not config.openai_api_key:
            print("❌ Error: OPENAI_API_KEY no está configurada en el archivo .env")
            print("Por favor, editá el archivo .env y agregá tu clave API.")
            return
        
        # Crear transcriptor
        transcriber = WhisperTranscriber(config)
        
        # Preguntar si hacer dry-run primero
        print("\n🤔 ¿Querés hacer una estimación de costos primero? (y/n): ", end="")
        response = input().lower().strip()
        
        if response in ['y', 'yes', 'sí', 'si', 's']:
            print("\n🔍 Calculando estimación de costos...")
            cost_info = transcriber.process_all_files(dry_run=True)
            
            if 'error' in cost_info:
                print(f"❌ {cost_info['error']}")
                return
            
            print(f"\n📊 Estimación de costos:")
            print(f"   • Archivos: {cost_info['total_files']}")
            print(f"   • Duración total: {cost_info['total_duration_hours']:.1f} horas")
            print(f"   • Costo estimado: ${cost_info['estimated_cost_usd']:.2f} USD")
            
            print(f"\n🤔 ¿Continuar con el procesamiento? (y/n): ", end="")
            confirm = input().lower().strip()
            
            if confirm not in ['y', 'yes', 'sí', 'si', 's']:
                print("🛑 Procesamiento cancelado.")
                return
        
        # Procesar archivos
        print("\n🚀 Iniciando procesamiento...")
        results = transcriber.process_all_files(dry_run=False)
        
        # Mostrar resumen final
        if 'error' not in results:
            print(f"\n✅ Procesamiento completado!")
            print(f"   • Archivos procesados: {len(results['results'])}")
            print(f"   • Tasa de éxito: {results['success_rate']*100:.1f}%")
            print(f"   • Tiempo total: {results['processing_time_minutes']:.1f} minutos")
            print(f"   • Transcripciones guardadas en: transcripciones/")
        
    except KeyboardInterrupt:
        print("\n🛑 Procesamiento interrumpido por el usuario.")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")


if __name__ == "__main__":
    main()
