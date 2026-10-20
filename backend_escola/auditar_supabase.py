"""Audita PostgreSQL por leitura; configura .env somente após auditoria aprovada."""
import argparse
from datetime import datetime, timezone
from getpass import getpass
import os
from pathlib import Path
import tempfile

from dotenv import dotenv_values
from sqlalchemy import Integer, String, create_engine, inspect, text
from sqlalchemy.engine import make_url

ROOT = Path(__file__).resolve().parent

def preparar_url(valor):
    if not valor or any(c in valor for c in "\r\n"):
        raise ValueError("Informe a URI PostgreSQL do painel Connect, sem quebras de linha.")
    if valor.startswith("postgres://"):
        valor = valor.replace("postgres://", "postgresql://", 1)
    try:
        url = make_url(valor)
    except Exception:
        raise ValueError("URI inválida. Confira o formato e a codificação da senha.") from None
    if url.get_backend_name() != "postgresql" or not url.host or not url.database:
        raise ValueError("É necessária uma URI PostgreSQL com host e banco; SQLite não comprova Supabase.")
    if url.drivername not in ("postgresql", "postgresql+psycopg2"):
        raise ValueError("Use o driver postgresql+psycopg2 deste projeto.")
    mode = url.query.get("sslmode", "require")
    if mode not in ("require", "verify-ca", "verify-full"):
        raise ValueError("Mantenha TLS: sslmode=require, verify-ca ou verify-full.")
    if "pgbouncer" in url.query:
        raise ValueError("Remova pgbouncer da URI: não é um parâmetro do psycopg2.")
    return url.set(drivername="postgresql+psycopg2").update_query_dict({"sslmode": mode})

def verificar(url):
    engine = create_engine(url, connect_args={"connect_timeout": 8}, hide_parameters=True)
    try:
        with engine.connect() as conn, conn.begin():
            conn.execute(text("SET TRANSACTION READ ONLY"))
            conn.execute(text("SELECT 1"))
            inspector = inspect(conn)
            missing = []
            for table, expected, pk in [
                ("cidade", {"id_cidade", "nome"}, "id_cidade"),
                ("linha_onibus", {"id_linha", "id_cidade", "codigo", "nome"}, "id_linha"),
            ]:
                if not inspector.has_table(table, schema="public"):
                    missing.append("Tabela ausente: " + table)
                    continue
                columns = {c["name"]: c for c in inspector.get_columns(table, schema="public")}
                missing.extend("Campo ausente: " + table + "." + name for name in sorted(expected - columns.keys()))
                for name in sorted(expected & columns.keys()):
                    col = columns[name]
                    expected_type = Integer if name.startswith("id_") else String
                    if not isinstance(col["type"], expected_type):
                        missing.append("Tipo incompatível: " + table + "." + name)
                    if col.get("nullable"):
                        missing.append("Campo deveria ser obrigatório: " + table + "." + name)
                    required_length = (100 if table == "cidade" else 150) if name == "nome" else 20
                    length = getattr(col["type"], "length", None)
                    if not name.startswith("id_") and length is not None and length < required_length:
                        missing.append("Tamanho insuficiente: " + table + "." + name)
                if inspector.get_pk_constraint(table, schema="public").get("constrained_columns") != [pk]:
                    missing.append("PK incompatível: " + table)
                col = columns.get(pk, {})
                if not col.get("identity") and "nextval(" not in str(col.get("default") or ""):
                    missing.append("ID sem geração automática: " + table + "." + pk)
                for name in columns.keys() - expected:
                    col = columns[name]
                    if not col.get("nullable") and not col.get("default") and not col.get("identity"):
                        missing.append("Campo extra obrigatório sem padrão: " + table + "." + name)
                if table == "linha_onibus":
                    refs = inspector.get_foreign_keys(table, schema="public")
                    if not any(f.get("constrained_columns") == ["id_cidade"] and
                               f.get("referred_table") == "cidade" and
                               f.get("referred_columns") == ["id_cidade"] and
                               f.get("referred_schema") in (None, "public") for f in refs):
                        missing.append("FK linha_onibus.id_cidade → cidade.id_cidade ausente.")
            return missing
    finally:
        engine.dispose()

def salvar_env(path, url):
    if path.is_symlink():
        raise ValueError("O .env é um link simbólico; configuração preservada, sem alteração.")
    lines = path.read_text().splitlines() if path.exists() else []
    kept = [line for line in lines if not line.strip().startswith(("DATABASE_URL=", "export DATABASE_URL="))]
    value = url.render_as_string(hide_password=False)
    # Aspas simples de dotenv preservam $, # e caracteres codificados da URI.
    quoted = value.replace("\\", "\\\\").replace("'", "\\'")
    content = "\n".join(kept + ["DATABASE_URL='" + quoted + "'"]) + "\n"
    if path.exists():
        backup_dir = path.parent / ".env-backups"
        backup_dir.mkdir(mode=0o700, exist_ok=True)
        if backup_dir.is_symlink():
            raise ValueError("Pasta de backup é um link; configuração preservada.")
        os.chmod(backup_dir, 0o700)
        backup = backup_dir / ("env-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f"))
        with backup.open("x") as handle:
            os.chmod(backup, 0o600)
            handle.write(path.read_text())
    fd, temporary = tempfile.mkstemp(prefix=".config-", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as handle:
            handle.write(content)
        os.replace(temporary, path)
    finally:
        if Path(temporary).exists():
            Path(temporary).unlink()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--configurar", action="store_true", help="Solicita URI em entrada oculta e salva somente após auditoria aprovada.")
    args = parser.parse_args()
    config = dotenv_values(ROOT / ".env")
    value = getpass("URI PostgreSQL do Supabase (entrada oculta): ") if args.configurar else os.getenv("DATABASE_URL") or config.get("DATABASE_URL")
    try:
        url = preparar_url(value)
    except ValueError as error:
        print(error)
        return 1
    try:
        issues = verificar(url)
    except Exception:
        print("Conexão ou auditoria não concluída. Confira URI, codificação da senha, rede, TLS e permissões. Nenhuma configuração foi alterada; dados de conexão foram omitidos.")
        return 1
    if issues:
        print("Conexão estabelecida, mas o esquema requer revisão. Nenhuma migração foi executada e o .env foi preservado.")
        for issue in issues:
            print("- " + issue)
        return 1
    if args.configurar:
        try:
            salvar_env(ROOT / ".env", url)
        except (OSError, ValueError) as error:
            print("Auditoria aprovada, mas a configuração não foi salva. Confira permissões e links do .env.")
            return 1
        print("Auditoria aprovada. .env atualizado; configuração anterior preservada em backup privado. Reinicie a API.")
        if os.getenv("DATABASE_URL"):
            print("Existe DATABASE_URL exportada no terminal; ela tem prioridade sobre .env. Atualize essa configuração privada antes de reiniciar.")
    else:
        print("Conexão PostgreSQL e estrutura esperada verificadas por leitura.")
    print("Ainda falta demonstrar POST/GET no banco remoto autorizado. Esta auditoria não criou registros.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
