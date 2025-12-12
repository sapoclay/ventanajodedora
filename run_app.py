import os
import sys
import platform
import subprocess
import venv
from pathlib import Path
import hashlib

from mensaje_salida import imprimir_mensaje_salida

def is_venv_exists():
    venv_dir = 'venv'
    return os.path.exists(venv_dir) and os.path.isdir(venv_dir)

def create_venv():
    print("Creando el entorno virtual...")
    venv.create('venv', with_pip=True)

    # Mejora: dejar el venv listo (pip/setuptools/wheel) una sola vez.
    pip_exe = get_pip_executable()
    subprocess.run([pip_exe, 'install', '--upgrade', 'pip', 'setuptools', 'wheel'], check=True)

def get_python_executable():
    if platform.system().lower() == 'windows':
        return os.path.join('venv', 'Scripts', 'python.exe')
    return os.path.join('venv', 'bin', 'python')

def get_pip_executable():
    if platform.system().lower() == 'windows':
        return os.path.join('venv', 'Scripts', 'pip.exe')
    return os.path.join('venv', 'bin', 'pip')

def install_requirements():
    pip_exe = get_pip_executable()
    requirements_file = 'requirements.txt'

    if not os.path.exists(requirements_file):
        print(f"Error: {requirements_file} not found")
        sys.exit(1)

    # Evitar reinstalaciones innecesarias si requirements.txt no cambió.
    req_path = Path(requirements_file)
    stamp_path = Path('venv') / '.requirements.sha256'
    req_hash = hashlib.sha256(req_path.read_bytes()).hexdigest()
    if stamp_path.exists() and stamp_path.read_text(encoding='utf-8').strip() == req_hash:
        print("Dependencias ya instaladas (sin cambios en requirements.txt).")
        return

    print("Instalando dependencias desde requirements.txt...")
    subprocess.run([pip_exe, 'install', '-r', requirements_file], check=True)
    stamp_path.write_text(req_hash, encoding='utf-8')

def run_main_app():
    python_exe = get_python_executable()
    main_file = 'main.py'
    
    if not os.path.exists(main_file):
        print(f"Error: {main_file} not found")
        sys.exit(1)
    
    print("Iniciando la aplicación...")
    subprocess.run([python_exe, main_file], check=True)

def main():
    # Cambiar al directorio que contenga este script
    os.chdir(Path(__file__).parent)

    try:
        if not is_venv_exists():
            create_venv()
        install_requirements()
        run_main_app()
    except KeyboardInterrupt:
        imprimir_mensaje_salida()
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        # Ignorar si el proceso fue interrumpido por señal (código 130 = SIGINT)
        if e.returncode == 130 or e.returncode == -2:
            imprimir_mensaje_salida()
            sys.exit(0)
        print(f"Error ocurrido: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error inesperado: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()