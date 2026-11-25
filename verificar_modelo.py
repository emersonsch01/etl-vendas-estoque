from pathlib import Path
import pandas as pd

GOLD = Path("data/gold")


def carregar(nome):

    return pd.read_parquet(
        GOLD / f"{nome}.parquet"
    )


# Dimensoes
dim_cliente = carregar("dim_cliente")
dim_produto = carregar("dim_produto")
dim_data = carregar("dim_data")
dim_vendedor = carregar("dim_vendedor")

# Fatos
fato_vendas = carregar("fato_vendas")
fato_estoque = carregar("fato_estoque_diario")


print("\n========== DIMENSOES ==========")

dimensoes = {
    "dim_cliente": (dim_cliente, "sk_cliente"),
    "dim_produto": (dim_produto, "sk_produto"),
    "dim_data": (dim_data, "sk_data"),
    "dim_vendedor": (dim_vendedor, "sk_vendedor")
}

for nome, (df, chave) in dimensoes.items():

    duplicados = df[chave].duplicated().sum()

    nulos = df[chave].isna().sum()

    print(
        f"{nome}: {len(df):,} registros | "
        f"Duplicados: {duplicados} | "
        f"Nulos: {nulos}"
    )


print("\n========== FATO VENDAS ==========")

print(f"Registros: {len(fato_vendas):,}")

print(
    "Quantidade total vendida:",
    fato_vendas["quantidade"].sum()
)

print(
    "Faturamento liquido:",
    round(fato_vendas["valor_liquido"].sum(), 2)
)

print(
    "Margem total:",
    round(fato_vendas["margem"].sum(), 2)
)


# Integridade referencial
print("\n========== INTEGRIDADE ==========")

print(
    "Clientes inexistentes:",
    (~fato_vendas["sk_cliente"].isin(
        dim_cliente["sk_cliente"]
    )).sum()
)

print(
    "Produtos inexistentes:",
    (~fato_vendas["sk_produto"].isin(
        dim_produto["sk_produto"]
    )).sum()
)

print(
    "Datas inexistentes:",
    (~fato_vendas["sk_data"].isin(
        dim_data["sk_data"]
    )).sum()
)

print(
    "Vendedores inexistentes:",
    (~fato_vendas["sk_vendedor"].isin(
        dim_vendedor["sk_vendedor"]
    )).sum()
)


print("\n========== FATO ESTOQUE ==========")

print(f"Registros: {len(fato_estoque):,}")

print(
    "Saldos negativos:",
    (fato_estoque["saldo_estoque"] < 0).sum()
)

print(
    "Chaves produto/data duplicadas:",
    fato_estoque.duplicated(
        subset=["sk_produto", "sk_data"]
    ).sum()
)

print("\nVALIDACAO FINALIZADA")
