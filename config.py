import os
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Config:
    """Configuración centralizada del proyecto"""
    
    # API Settings
    openai_api_key: str
    model: str = "whisper-1"
    language: str = "es"
    response_format: str = "text"
    
    # Audio Processing
    chunk_duration_minutes: int = 10  # Chunks de 10 minutos
    max_file_size_mb: int = 24        # Límite de OpenAI es 25MB
    overlap_seconds: int = 30         # Overlap entre chunks para continuidad
    
    # Paths
    audio_folder: Path
    chunks_folder: Path
    transcriptions_folder: Path
    logs_folder: Path
    
    # Prompts específicos para Puerto Rico
    prompt_template: str = (
        "Este es un audio en español de Puerto Rico. "
        "Transcribe con puntuación correcta, incluyendo nombres propios "
        "y palabras en inglés que puedan aparecer. "
        "Mantén el formato natural del habla puertorriqueña."
    )
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Carga configuración desde variables de entorno"""
        from dotenv import load_dotenv
        load_dotenv()
        
        base_path = Path.cwd()
        
        return cls(
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            chunk_duration_minutes=int(os.getenv("CHUNK_DURATION_MINUTES", 10)),
            max_file_size_mb=int(os.getenv("MAX_FILE_SIZE_MB", 24)),
            audio_folder=base_path / os.getenv("AUDIO_FOLDER", "audios"),
            chunks_folder=base_path / os.getenv("CHUNKS_FOLDER", "chunks"),
            transcriptions_folder=base_path / os.getenv("TRANSCRIPTIONS_FOLDER", "transcripciones"),
            logs_folder=base_path / os.getenv("LOGS_FOLDER", "logs")
        )
