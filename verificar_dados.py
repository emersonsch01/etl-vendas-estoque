
import pandas as pd
from pathlib import Path

pasta = Path("data/raw")

for arquivo in pasta.glob("*.csv"):
    df = pd.read_csv(arquivo)

    print("\n" + "=" * 50)
    print(f"ARQUIVO: {arquivo.name}")
    print(f"LINHAS: {len(df):,}")
    print(f"COLUNAS: {len(df.columns)}")
    print("\nTIPOS:")
    print(df.dtypes)
    print("\nVALORES NULOS:")
    print(df.isnull().sum())
    print("\nPRIMEIRAS LINHAS:")
    print(df.head(3))
