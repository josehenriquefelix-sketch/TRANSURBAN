"""Gera ZIP reduzido com API, site e falas, a partir de arquivos versionados."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "TRANSURBAN_APRESENTACAO/"


def gerar(destino):
    selected = subprocess.check_output([
        "git", "ls-files", "-z", "backend_escola", "apresentacoes/api-sem-slides",
        "apresentacoes/ROTEIRO_API_SEM_SLIDES_20_10.md", "apresentacoes/GUIA_LIDER_API_SITE.md"
    ], cwd=ROOT).decode().split("\0")
    contents = {}
    for name in sorted(filter(None, selected)):
        path = Path(name)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError("Caminho inválido no pacote")
        if any(part.startswith(".venv") or part in {"__pycache__", "node_modules", ".git"} for part in path.parts):
            raise ValueError("Ambiente local não deve ser transportado no ZIP")
        if path.name == ".env" or path.suffix.lower() in {".db", ".sqlite", ".sqlite3", ".pyc", ".zip"}:
            raise ValueError("Arquivo privado ou gerado não permitido: " + name)
        file = ROOT / path
        if file.is_symlink():
            raise ValueError("Links simbólicos não são incluídos: " + name)
        contents[name] = file.read_bytes()
    contents["LEIA_PRIMEIRO.txt"] = """TRANSURBAN — apresentação de 20/10/2026, sem slides

1. EXTRAIA o ZIP inteiro. Não execute de dentro do arquivo compactado.
2. Abra a pasta backend_escola no VS Code.
3. Requer Python 3.12. A primeira instalação precisa de internet.

WINDOWS: abra PREPARAR-WINDOWS.cmd. Quando concluir, abra APRESENTAR-WINDOWS.cmd.
LINUX: no terminal dentro de backend_escola:
  python3 iniciar_apresentacao.py --preparar
  python3 iniciar_apresentacao.py --testar
  python3 iniciar_apresentacao.py --diagnostico
  python3 iniciar_apresentacao.py

Após Application startup complete, no navegador DESSE computador:
  API: http://127.0.0.1:8000/docs
  SITE: http://127.0.0.1:8000/app/
Mantenha o terminal aberto. Ctrl+C encerra. Se 8000 estiver ocupada, use
iniciar_apresentacao.py --port 8002 e troque 8000 por 8002 nos endereços.

Use janela normal para passageiro e anônima para motorista (ou vice-versa).
Cadastros e dados pessoais de outro computador NÃO estão neste ZIP.
O inicializador usa SQLite LOCAL: não exige .env e não conecta ao Supabase.
Não copie ambientes virtuais Windows para Linux. Recrie no destino.

Leia backend_escola/SITE_FUNCIONAL.md e apresentacoes/GUIA_LIDER_API_SITE.md.
As falas estão em apresentacoes/api-sem-slides/FALAS_PARA_TREINAR.txt.
O PDF é roteiro de leitura, não slides. A apresentação mostra API e testes.

Mapa, clima e cálculo de vias exigem internet. GPS exige permissão e sinal.
Percursos escolhidos não são itinerários oficiais de ônibus. Não há integração
à frota, pagamentos, bilhetes reais ou depósitos de VT. Carteira é demonstração.
Tarifa integral urbana de Maringá: R$ 5,80, fonte oficial e datas em
backend_escola/data/site/tarifa.json. Não aplicar automaticamente a Sarandi.
IA: programação histórica de Curitiba, não atrasos reais de Maringá.

Ensaie no notebook e no projetor. Um pendrive transporta arquivos; não instala
Python nem transmite vídeo. Confira HDMI/saída de vídeo e o adaptador.
""".encode("utf-8")
    manifest = {
        "codigo_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip(),
        "gerado_em_utc": datetime.now(timezone.utc).isoformat(),
        "arquivos_sha256": {name: hashlib.sha256(data).hexdigest() for name, data in contents.items()},
        "privacidade": "Sem .env, banco de contas, cookies ou ambientes virtuais.",
    }
    contents["MANIFESTO_SHA256.json"] = json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8")
    destino.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destino, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in contents.items():
            archive.writestr(PREFIX + name, data)
    with zipfile.ZipFile(destino) as archive:
        if archive.testzip() is not None:
            raise ValueError("ZIP não passou na verificação de integridade")
    digest = hashlib.sha256(destino.read_bytes()).hexdigest()
    destino.with_suffix(destino.suffix + ".sha256").write_text(digest + "  " + destino.name + "\n")
    print(f"ZIP verificado: {len(contents)} arquivos, {destino.stat().st_size / 1024**2:.2f} MiB")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destino", type=Path, help="Novo arquivo .zip; não sobrescreve existente.")
    gerar(parser.parse_args().destino)
