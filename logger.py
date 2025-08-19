import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

class TranscriptionLogger:
    """Sistema de logging para el proceso de transcripción"""
    
    def __init__(self, logs_folder: Path, log_level: int = logging.INFO):
        self.logs_folder = logs_folder
        self.logs_folder.mkdir(exist_ok=True)
        
        # Crear logger principal
        self.logger = logging.getLogger("whisper_transcription")
        self.logger.setLevel(log_level)
        
        # Evitar duplicar handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Configura los handlers de logging"""
        
        # Handler para archivo de log
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.logs_folder / f"transcription_{timestamp}.log"
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Handler para consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Formateo
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.logger.info(f"🚀 Iniciando sesión de transcripción. Log guardado en: {log_file}")
    
    def info(self, message: str):
        """Log de información"""
        self.logger.info(message)
    
    def error(self, message: str, exception: Optional[Exception] = None):
        """Log de errores"""
        if exception:
            self.logger.error(f"{message}: {str(exception)}", exc_info=True)
        else:
            self.logger.error(message)
    
    def warning(self, message: str):
        """Log de advertencias"""
        self.logger.warning(message)
    
    def debug(self, message: str):
        """Log de debug"""
        self.logger.debug(message)
    
    def progress(self, current: int, total: int, item_name: str = "archivos"):
        """Log de progreso"""
        percentage = (current / total) * 100
        self.info(f"📊 Progreso: {current}/{total} {item_name} ({percentage:.1f}%)")
    
    def cost_estimate(self, total_minutes: float, cost_per_minute: float = 0.006):
        """Calcula y registra estimación de costos"""
        total_cost = total_minutes * cost_per_minute
        self.info(f"💰 Estimación de costo: {total_minutes:.1f} minutos × ${cost_per_minute} = ${total_cost:.2f}")
        
        if total_cost > 10:
            self.warning(f"⚠️  El costo estimado (${total_cost:.2f}) es considerable. Verificá antes de continuar.")
    
    def transcription_completed(self, file_name: str, duration_minutes: float, cost: float):
        """Log de transcripción completada"""
        self.info(f"✅ Completado: {file_name} ({duration_minutes:.1f} min, ~${cost:.2f})")
