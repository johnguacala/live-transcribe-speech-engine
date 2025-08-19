#!/usr/bin/env python3
"""
🔍 Análisis directo del archivo "del 00 al 1-44.mp3"
Intenta procesar directamente con OpenAI Whisper
"""

import openai
from pathlib import Path
import json
from dotenv import load_dotenv
import os

def direct_whisper_analysis():
    """Análisis directo con OpenAI Whisper"""
    
    # Cargar configuración
    load_dotenv()
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    if not openai_api_key:
        print("❌ No se encontró OPENAI_API_KEY")
        return
    
    # Configurar cliente
    client = openai.OpenAI(api_key=openai_api_key)
    
    # Archivo de audio
    audio_path = Path("audios/del 00 al 1-44.mp3")
    
    if not audio_path.exists():
        print(f"❌ No se encontró el archivo: {audio_path}")
        return
    
    print(f"🎵 Procesando directamente: {audio_path}")
    print(f"📊 Tamaño del archivo: {audio_path.stat().st_size / (1024*1024):.1f} MB")
    
    try:
        # Procesar con diferentes configuraciones
        configurations = [
            {
                'name': 'Detección Estándar',
                'prompt': None,
                'temperature': 0
            },
            {
                'name': 'Detección Sensible', 
                'prompt': "Este es un audio de procedimientos legales en español puertorriqueño.",
                'temperature': 0.1
            },
            {
                'name': 'Detección Agresiva',
                'prompt': "Transcribe todo el audio incluyendo ruidos, susurros y conversaciones de fondo.",
                'temperature': 0.3
            }
        ]
        
        results = []
        
        for config in configurations:
            print(f"\n🔍 Probando: {config['name']}")
            
            with open(audio_path, 'rb') as audio_file:
                params = {
                    'file': audio_file,
                    'model': 'whisper-1',
                    'language': 'es',
                    'temperature': config['temperature']
                }
                
                if config['prompt']:
                    params['prompt'] = config['prompt']
                
                try:
                    transcript = client.audio.transcriptions.create(**params)
                    
                    result = {
                        'config': config['name'],
                        'text': transcript.text,
                        'length': len(transcript.text),
                        'has_content': len(transcript.text.strip()) > 50
                    }
                    
                    results.append(result)
                    
                    print(f"   ✅ Transcripción: {len(transcript.text)} caracteres")
                    if result['has_content']:
                        print(f"   📝 Contenido: {transcript.text[:100]}...")
                    else:
                        print(f"   📝 Contenido: {transcript.text}")
                        
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                    results.append({
                        'config': config['name'],
                        'error': str(e),
                        'has_content': False
                    })
        
        # Resumen de resultados
        print(f"\n📊 RESUMEN DE ANÁLISIS:")
        print("=" * 50)
        
        for result in results:
            if 'error' in result:
                print(f"❌ {result['config']}: ERROR - {result['error']}")
            else:
                status = "CON CONTENIDO" if result['has_content'] else "SIN CONTENIDO"
                print(f"✅ {result['config']}: {status} ({result['length']} chars)")
        
        # Determinar mejor resultado
        valid_results = [r for r in results if 'text' in r and r['has_content']]
        
        if valid_results:
            best_result = max(valid_results, key=lambda x: x['length'])
            print(f"\n🏆 MEJOR RESULTADO: {best_result['config']}")
            print(f"📝 Contenido completo:")
            print("-" * 50)
            print(best_result['text'])
            print("-" * 50)
            
            # Guardar mejor resultado
            output_file = Path(f"transcripciones/del_00_al_144_DIRECTO.txt")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# Transcripción directa - {best_result['config']}\n")
                f.write(f"# Archivo: del 00 al 1-44.mp3\n")
                f.write(f"# Caracteres: {best_result['length']}\n\n")
                f.write(best_result['text'])
            
            print(f"✅ Resultado guardado en: {output_file}")
            return output_file
        else:
            print(f"\n⚠️  CONCLUSIÓN: El archivo parece contener solo silencio o ruido")
            print(f"   Posibles causas:")
            print(f"   • Segmento de pausa en la audiencia")
            print(f"   • Audio con muy bajo volumen")
            print(f"   • Ruido técnico sin habla")
            return None
            
    except Exception as e:
        print(f"❌ Error general: {e}")
        return None

if __name__ == "__main__":
    print("🔍 ANÁLISIS DIRECTO CON WHISPER")
    print("=" * 50)
    
    result = direct_whisper_analysis()
    
    if result:
        print(f"\n🎉 ANÁLISIS COMPLETADO CON CONTENIDO")
    else:
        print(f"\n📋 ANÁLISIS COMPLETADO - ARCHIVO SIN CONTENIDO DETECTABLE")
