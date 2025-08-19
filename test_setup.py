#!/usr/bin/env python3
"""
🧪 Script de Prueba Rápida
Verifica que todo esté configurado correctamente antes del procesamiento principal
"""

import sys
from pathlib import Path

def test_imports():
    """Prueba que todas las dependencias estén instaladas"""
    print("🔍 Verificando imports...")
    
    try:
        import openai
        print("  ✅ OpenAI instalado")
    except ImportError:
        print("  ❌ OpenAI no instalado. Ejecuta: pip install openai")
        return False
    
    try:
        import ffmpeg
        print("  ✅ ffmpeg-python instalado")
    except ImportError:
        print("  ❌ ffmpeg-python no instalado. Ejecuta: pip install ffmpeg-python")
        return False
    
    try:
        from dotenv import load_dotenv
        print("  ✅ python-dotenv instalado")
    except ImportError:
        print("  ❌ python-dotenv no instalado. Ejecuta: pip install python-dotenv")
        return False
    
    return True

def test_ffmpeg():
    """Prueba que ffmpeg esté disponible en el sistema"""
    print("\n🔧 Verificando ffmpeg...")
    
    import subprocess
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, check=False)
        if result.returncode == 0:
            print("  ✅ ffmpeg está instalado y disponible")
            return True
        else:
            print("  ❌ ffmpeg no funciona correctamente")
            return False
    except FileNotFoundError:
        print("  ❌ ffmpeg no está instalado")
        print("     📖 Ver INSTALACION.md para instrucciones")
        return False

def test_config():
    """Prueba la configuración"""
    print("\n⚙️ Verificando configuración...")
    
    try:
        from config import Config
        config = Config.from_env()
        
        if not config.openai_api_key or config.openai_api_key == "tu_clave_aqui":
            print("  ❌ OPENAI_API_KEY no está configurada en .env")
            print("     📝 Edita el archivo .env con tu clave real")
            return False
        else:
            print("  ✅ API Key configurada")
        
        # Verificar carpetas
        for folder_name, folder_path in [
            ("audios", config.audio_folder),
            ("transcripciones", config.transcriptions_folder),
            ("chunks", config.chunks_folder),
            ("logs", config.logs_folder)
        ]:
            if folder_path.exists():
                print(f"  ✅ Carpeta {folder_name}/ existe")
            else:
                print(f"  ⚠️  Carpeta {folder_name}/ no existe (se creará automáticamente)")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error en configuración: {e}")
        return False

def test_audio_files():
    """Verifica si hay archivos de audio para procesar"""
    print("\n🎵 Verificando archivos de audio...")
    
    try:
        from config import Config
        config = Config.from_env()
        
        audio_extensions = {'.mp3', '.wav', '.m4a', '.flac', '.ogg'}
        audio_files = []
        
        if not config.audio_folder.exists():
            print(f"  ⚠️  Carpeta {config.audio_folder} no existe")
            print(f"     📁 Crea la carpeta y coloca tus archivos MP3 ahí")
            return True  # No es un error crítico
        
        for ext in audio_extensions:
            audio_files.extend(config.audio_folder.glob(f'*{ext}'))
        
        if audio_files:
            print(f"  ✅ Encontrados {len(audio_files)} archivo(s) de audio:")
            for audio_file in audio_files[:5]:  # Mostrar máximo 5
                size_mb = audio_file.stat().st_size / (1024 * 1024)
                print(f"     • {audio_file.name} ({size_mb:.1f} MB)")
            
            if len(audio_files) > 5:
                print(f"     ... y {len(audio_files) - 5} más")
        else:
            print(f"  ⚠️  No se encontraron archivos de audio en {config.audio_folder}")
            print(f"     📁 Coloca tus archivos MP3 en la carpeta audios/")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error verificando archivos: {e}")
        return False

def test_openai_connection():
    """Prueba conexión con OpenAI (sin gastar créditos)"""
    print("\n🌐 Verificando conexión con OpenAI...")
    
    try:
        import openai
        from config import Config
        
        config = Config.from_env()
        openai.api_key = config.openai_api_key
        
        # Solo verificar que la clave sea válida (sin hacer transcripción)
        try:
            # Este endpoint es gratuito para verificar la clave
            models = openai.Model.list()
            print("  ✅ Conexión con OpenAI exitosa")
            print("  ✅ API Key válida")
            return True
            
        except openai.error.AuthenticationError:
            print("  ❌ API Key inválida")
            print("     🔑 Verifica tu clave en .env")
            return False
        except Exception as e:
            print(f"  ⚠️  No se pudo verificar conexión: {e}")
            print("     🌐 Verifica tu conexión a internet")
            return True  # No bloquear por problemas de red
    
    except Exception as e:
        print(f"  ❌ Error verificando OpenAI: {e}")
        return False

def main():
    """Ejecuta todas las pruebas"""
    print("🧪 HearingsWhisper - Verificación del Sistema\n")
    
    tests = [
        ("Imports de Python", test_imports),
        ("ffmpeg", test_ffmpeg),
        ("Configuración", test_config),
        ("Archivos de audio", test_audio_files),
        ("Conexión OpenAI", test_openai_connection),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  💥 Error inesperado en {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen
    print("\n" + "="*50)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{len(results)} pruebas exitosas")
    
    if passed == len(results):
        print("\n🎉 ¡Todo listo! Puedes ejecutar:")
        print("   python transcribe.py")
    else:
        print("\n🔧 Hay problemas que resolver antes de continuar.")
        print("   📖 Consulta INSTALACION.md para ayuda")
        
        # Verificar si al menos lo básico funciona
        critical_tests = ["Imports de Python", "Configuración"]
        critical_passed = sum(1 for name, result in results 
                            if name in critical_tests and result)
        
        if critical_passed == len(critical_tests):
            print("\n💡 Las funciones básicas están OK.")
            print("   Puedes intentar ejecutar transcribe.py para más detalles.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Verificación cancelada por el usuario.")
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        sys.exit(1)
