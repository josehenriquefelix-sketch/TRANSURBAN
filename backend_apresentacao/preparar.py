"""Cria um ambiente novo em Windows ou Linux. Executar com Python 3.11+."""
import os
import importlib.util
from pathlib import Path
import subprocess
import sys
import venv

ROOT = Path(__file__).resolve().parent
def main():
    if sys.version_info < (3,11):
        raise SystemExit('Instale Python 3.11 ou mais recente (3.13 recomendado).')
    python = ROOT / '.venv' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    temp = ROOT / '.temp_instalacao'
    temp.mkdir(exist_ok=True)
    os.environ['TEMP'] = os.environ['TMP'] = str(temp)
    if not python.exists():
        try:
            venv.EnvBuilder(with_pip=True).create(ROOT / '.venv')
        except Exception:
            # Algumas instalações Windows têm ensurepip indisponível; usa o pip do Python base.
            venv.EnvBuilder(with_pip=False).create(ROOT / '.venv')
    instalador = sys.executable if importlib.util.find_spec('pip') else getattr(sys, '_base_executable', sys.executable)
    requisitos = 'requirements-test.txt' if '--testes' in sys.argv else 'requirements.txt'
    subprocess.run([instalador,'-m','pip','--python',str(python),'install','-r',str(ROOT/requisitos)],check=True,cwd=ROOT)
    print('Preparação concluída. Execute iniciar.cmd (Windows) ou bash iniciar.sh (Linux).')
if __name__ == '__main__':
    main()
