import pandas as pd

df = pd.read_parquet(
    "data/processed/movimentos_estoque.parquet"
)

df["data_movimento"] = pd.to_datetime(
    df["data_movimento"]
)

resultado = (
    df.groupby("tipo")
    .agg(
        quantidade_registros=("id_produto", "count"),
        produtos=("id_produto", "nunique"),
        primeira_data=("data_movimento", "min"),
        ultima_data=("data_movimento", "max"),
        quantidade_total=("quantidade", "sum")
    )
    .reset_index()
)

print(resultado.to_string(index=False))