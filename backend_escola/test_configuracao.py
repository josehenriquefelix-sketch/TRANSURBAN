from pathlib import Path
import pytest
from dotenv import dotenv_values
from auditar_supabase import preparar_url, salvar_env
import auditar_supabase

def test_configuracao_preserva_variaveis_e_backup_privado(tmp_path):
    path = tmp_path / ".env"
    original = "DATABASE_URL=sqlite:///anterior.db\nCSV_PATH=data/fonte.csv\n"
    path.write_text(original)
    url = preparar_url("postgresql://usuario:senha%40exemplo@db.example.com:5432/postgres")
    salvar_env(path, url)
    config = dotenv_values(path)
    assert config["CSV_PATH"] == "data/fonte.csv"
    assert preparar_url(config["DATABASE_URL"]).password == "senha@exemplo"
    assert preparar_url(config["DATABASE_URL"]).query["sslmode"] == "require"
    assert (path.stat().st_mode & 0o777) == 0o600
    backups = list((tmp_path / ".env-backups").iterdir())
    assert len(backups) == 1
    assert backups[0].read_text() == original
    assert (backups[0].stat().st_mode & 0o777) == 0o600

@pytest.mark.parametrize("uri", ["", "sqlite:///local.db", "texto inválido", "postgresql://u:p@host/db?sslmode=disable", "postgresql://u:p@host/db?pgbouncer=true", "postgresql://u:p@host/db\nOUTRA=valor"])
def test_configuracoes_inseguras_ou_invalidas_rejeitadas(uri):
    with pytest.raises(ValueError):
        preparar_url(uri)

def test_verificacao_tls_mais_forte_e_preservada():
    url = preparar_url("postgresql://u:p@host/db?sslmode=verify-full&sslrootcert=/tmp/ca.crt")
    assert url.query["sslmode"] == "verify-full"
    assert url.query["sslrootcert"] == "/tmp/ca.crt"

def test_arquivo_privado_por_symlink_nao_e_alterado(tmp_path):
    target = tmp_path / "privado"
    target.write_text("preservar")
    path = tmp_path / ".env"
    path.symlink_to(target)
    with pytest.raises(ValueError):
        salvar_env(path, preparar_url("postgresql://u:p@host/db"))
    assert target.read_text() == "preservar"

@pytest.mark.parametrize("falha", ["conexao", "esquema"])
def test_auditoria_reprovada_nao_altera_configuracao_nem_expoe_uri(tmp_path, monkeypatch, capsys, falha):
    path = tmp_path / ".env"
    original = "DATABASE_URL=sqlite:///preservar.db\n"
    path.write_text(original)
    monkeypatch.setattr(auditar_supabase, "ROOT", tmp_path)
    monkeypatch.setattr("sys.argv", ["auditar_supabase.py", "--configurar"])
    monkeypatch.setattr(auditar_supabase, "getpass", lambda _: "postgresql://u:sentinela-secreta@host/postgres")
    def verificar(_):
        if falha == "conexao":
            raise RuntimeError("postgresql://u:sentinela-secreta@host/postgres")
        return ["Tabela ausente: cidade"]
    monkeypatch.setattr(auditar_supabase, "verificar", verificar)
    assert auditar_supabase.main() == 1
    assert path.read_text() == original
    assert "sentinela-secreta" not in capsys.readouterr().out
