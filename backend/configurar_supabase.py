"""Execute no terminal local. Não envie sua senha no chat."""
from getpass import getpass
from argparse import ArgumentParser
from pathlib import Path
from dotenv import set_key
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

def main():
    parser = ArgumentParser(description="Configura a conexão privada sem mostrar a senha.")
    parser.add_argument("--transurban", action="store_true", help="Usa os parâmetros públicos do projeto TRANSURBAN já conferidos no painel.")
    args = parser.parse_args()
    if args.transurban:
        host = "aws-0-us-east-2.pooler.supabase.com"
        usuario = "postgres.lsnpvokfnvyjkvqzkvof"
        porta = 5432
        banco = "postgres"
        print("Projeto TRANSURBAN selecionado. Informe a senha do banco, não a senha do GitHub.")
    else:
        host = input("Host (painel Connect): ").strip()
        usuario = input("Usuário (painel Connect): ").strip()
        porta = int(input("Porta [5432]: ").strip() or "5432")
        banco = input("Banco [postgres]: ").strip() or "postgres"
    senha = getpass("Senha do banco (não será exibida): ")
    if not host or not usuario or not senha:
        raise SystemExit("Campos obrigatórios não preenchidos. .env não foi alterado.")
    url = URL.create("postgresql+psycopg2", username=usuario, password=senha,
                     host=host, port=porta, database=banco, query={"sslmode": "require"})
    engine = create_engine(url, hide_parameters=True, connect_args={"connect_timeout": 10})
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1")).scalar_one()
            connection.execute(text("SELECT id_cidade, nome FROM cidade LIMIT 1"))
            connection.execute(text("SELECT id_linha, id_cidade, codigo, nome FROM linha_onibus LIMIT 1"))
    except Exception:
        raise SystemExit("Conexão não confirmada. Confira os parâmetros no painel. .env não foi alterado.")
    finally:
        engine.dispose()
    target = Path(__file__).with_name(".env")
    set_key(target, "DATABASE_URL", url.render_as_string(hide_password=False))
    print("Conexão verificada e DATABASE_URL salva no .env local. Reinicie a API. Nenhuma tabela foi modificada.")

if __name__ == "__main__":
    main()
