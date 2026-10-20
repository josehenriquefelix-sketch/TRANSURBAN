from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data" / "atrasos_analise.csv"
OUT = BASE / "ia" / "resultados"
OUT.mkdir(exist_ok=True)

df = pd.read_csv(DATA, parse_dates=["data_registro"])

# Qualidade
qualidade = pd.DataFrame({
    "indicador": [
        "registros", "colunas", "nulos", "duplicados",
        "atrasos_negativos", "data_inicial", "data_final"
    ],
    "valor": [
        len(df), df.shape[1], int(df.isna().sum().sum()),
        int(df.duplicated().sum()),
        int((df["minutos_atraso"] < 0).sum()),
        df["data_registro"].min().date(),
        df["data_registro"].max().date()
    ]
})
qualidade.to_csv(OUT / "01_qualidade.csv", index=False)

# 1. Cidade
por_cidade = (df.groupby("cidade", as_index=False)["minutos_atraso"]
              .agg(["count","mean","max"]).reset_index()
              .rename(columns={"count":"registros","mean":"atraso_medio","max":"maior_atraso"}))
por_cidade["atraso_medio"] = por_cidade["atraso_medio"].round(2)
por_cidade.to_csv(OUT / "02_por_cidade.csv", index=False)

# 2. Período
por_periodo = (df.groupby("periodo", as_index=False)["minutos_atraso"]
               .agg(["count","mean"]).reset_index()
               .rename(columns={"count":"registros","mean":"atraso_medio"}))
por_periodo["atraso_medio"] = por_periodo["atraso_medio"].round(2)
por_periodo.to_csv(OUT / "03_por_periodo.csv", index=False)

# 3. Trânsito
por_transito = (df.groupby("condicao_transito", as_index=False)["minutos_atraso"]
                .agg(["count","mean"]).reset_index()
                .rename(columns={"count":"registros","mean":"atraso_medio"}))
por_transito["atraso_medio"] = por_transito["atraso_medio"].round(2)
por_transito.to_csv(OUT / "04_por_transito.csv", index=False)

# 4. Clima
por_clima = (df.groupby("clima", as_index=False)["minutos_atraso"]
             .agg(["count","mean"]).reset_index()
             .rename(columns={"count":"registros","mean":"atraso_medio"}))
por_clima["atraso_medio"] = por_clima["atraso_medio"].round(2)
por_clima.to_csv(OUT / "05_por_clima.csv", index=False)

# 5. Linha
por_linha = (df.groupby(["codigo_linha","nome_linha"], as_index=False)["minutos_atraso"]
             .agg(["count","mean","max"]).reset_index()
             .rename(columns={"count":"registros","mean":"atraso_medio","max":"maior_atraso"}))
por_linha["atraso_medio"] = por_linha["atraso_medio"].round(2)
por_linha.to_csv(OUT / "06_por_linha.csv", index=False)

# 6. Evolução temporal
temporal = (df.groupby("data_registro", as_index=False)["minutos_atraso"]
            .mean().rename(columns={"minutos_atraso":"atraso_medio"}))
temporal["atraso_medio"] = temporal["atraso_medio"].round(2)
temporal.to_csv(OUT / "07_temporal.csv", index=False)

# Classificação de severidade
def classificar(x):
    if x <= 5: return "Baixo"
    if x <= 10: return "Moderado"
    if x <= 15: return "Alto"
    return "Muito alto"

df["classificacao_atraso"] = df["minutos_atraso"].apply(classificar)
classif = (df["classificacao_atraso"].value_counts()
           .rename_axis("classificacao").reset_index(name="registros"))
classif.to_csv(OUT / "08_classificacao.csv", index=False)

# Gráficos
plt.figure(figsize=(8,5))
plt.bar(por_cidade["cidade"], por_cidade["atraso_medio"])
plt.title("Atraso médio por cidade — massa de teste")
plt.xlabel("Cidade"); plt.ylabel("Minutos")
plt.tight_layout(); plt.savefig(OUT/"grafico_01_cidade.png", dpi=160); plt.close()

plt.figure(figsize=(8,5))
plt.bar(por_transito["condicao_transito"], por_transito["atraso_medio"])
plt.title("Atraso médio por condição de trânsito — massa de teste")
plt.xlabel("Condição"); plt.ylabel("Minutos")
plt.tight_layout(); plt.savefig(OUT/"grafico_02_transito.png", dpi=160); plt.close()

plt.figure(figsize=(9,5))
plt.plot(temporal["data_registro"], temporal["atraso_medio"], marker="o")
plt.title("Evolução diária do atraso médio — massa de teste")
plt.xlabel("Data"); plt.ylabel("Minutos")
plt.xticks(rotation=45)
plt.tight_layout(); plt.savefig(OUT/"grafico_03_temporal.png", dpi=160); plt.close()

plt.figure(figsize=(8,5))
plt.bar(classif["classificacao"], classif["registros"])
plt.title("Classificação dos registros por severidade")
plt.xlabel("Classificação"); plt.ylabel("Quantidade de registros")
plt.tight_layout(); plt.savefig(OUT/"grafico_04_classificacao.png", dpi=160); plt.close()

print("Análise concluída.")
print(f"Registros: {len(df)}")
print(f"Atraso médio: {df['minutos_atraso'].mean():.2f} min")
print("Arquivos gerados em:", OUT)
