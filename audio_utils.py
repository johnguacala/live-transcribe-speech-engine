import subprocess
import os
from pathlib import Path
from typing import List, Tuple
import json
from logger import TranscriptionLogger

class AudioProcessor:
    """Maneja el procesamiento y división de archivos de audio"""
    
    def __init__(self, logger: TranscriptionLogger):
        self.logger = logger
    
    def check_ffmpeg(self) -> bool:
        """Verifica si ffmpeg está disponible"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, check=False)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def get_audio_duration(self, audio_path: Path) -> float:
        """Obtiene la duración del audio en minutos usando ffprobe"""
        if not self.check_ffmpeg():
            raise RuntimeError("ffmpeg no está instalado. Ver instrucciones de instalación.")
        
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                '-of', 'csv=p=0', str(audio_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            duration_seconds = float(result.stdout.strip())
            return duration_seconds / 60  # Convertir a minutos
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error al obtener duración de {audio_path.name}", e)
            raise
    
    def get_file_size_mb(self, file_path: Path) -> float:
        """Obtiene el tamaño del archivo en MB"""
        size_bytes = file_path.stat().st_size
        return size_bytes / (1024 * 1024)
    
    def split_audio(self, input_path: Path, output_folder: Path, 
                   chunk_duration_minutes: int = 10, overlap_seconds: int = 30) -> List[Path]:
        """
        Divide un archivo de audio en chunks más pequeños
        
        Args:
            input_path: Archivo de audio original
            output_folder: Carpeta donde guardar los chunks
            chunk_duration_minutes: Duración de cada chunk en minutos
            overlap_seconds: Segundos de overlap entre chunks
        
        Returns:
            Lista de paths de los chunks creados
        """
        if not self.check_ffmpeg():
            raise RuntimeError("ffmpeg no está instalado. Ver instrucciones de instalación.")
        
        output_folder.mkdir(exist_ok=True)
        chunk_folder = output_folder / input_path.stem
        chunk_folder.mkdir(exist_ok=True)
        
        # Obtener duración total
        total_duration = self.get_audio_duration(input_path)
        chunk_duration_seconds = chunk_duration_minutes * 60
        
        self.logger.info(f"🔧 Dividiendo {input_path.name} ({total_duration:.1f} min) en chunks de {chunk_duration_minutes} min")
        
        chunk_paths = []
        start_time = 0
        chunk_number = 1
        
        while start_time < (total_duration * 60):
            chunk_name = f"{input_path.stem}_chunk_{chunk_number:03d}.mp3"
            chunk_path = chunk_folder / chunk_name
            
            # Comando ffmpeg para extraer chunk
            cmd = [
                'ffmpeg', '-i', str(input_path),
                '-ss', str(start_time),
                '-t', str(chunk_duration_seconds),
                '-c', 'copy',  # No re-encodear para mayor velocidad
                '-y',  # Sobreescribir si existe
                str(chunk_path)
            ]
            
            try:
                self.logger.debug(f"Creando chunk {chunk_number}: {chunk_name}")
                subprocess.run(cmd, capture_output=True, text=True, check=True)
                chunk_paths.append(chunk_path)
                
                # Avanzar al siguiente chunk con overlap
                start_time += chunk_duration_seconds - overlap_seconds
                chunk_number += 1
                
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Error creando chunk {chunk_number}", e)
                break
        
        self.logger.info(f"✅ Creados {len(chunk_paths)} chunks para {input_path.name}")
        return chunk_paths
    
    def needs_splitting(self, file_path: Path, max_size_mb: int = 24) -> bool:
        """Determina si un archivo necesita ser dividido"""
        size_mb = self.get_file_size_mb(file_path)
        return size_mb > max_size_mb
    
    def estimate_processing_time(self, audio_duration_minutes: float) -> str:
        """Estima el tiempo de procesamiento basado en la duración del audio"""
        # Whisper procesa aproximadamente 1 minuto de audio en 6-10 segundos
        estimated_seconds = audio_duration_minutes * 8  # Promedio conservador
        
        if estimated_seconds < 60:
            return f"{estimated_seconds:.0f} segundos"
        elif estimated_seconds < 3600:
            return f"{estimated_seconds/60:.1f} minutos"
        else:
            return f"{estimated_seconds/3600:.1f} horas"
