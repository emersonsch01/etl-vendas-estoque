from pathlib import Path
import logging

import numpy as np
import pandas as pd
import holidays


# ==========================================================
# CONFIGURACOES
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = BASE_DIR / "data" / "processed"
GOLD_DIR = BASE_DIR / "data" / "gold"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


# ==========================================================
# LEITURA DOS DADOS SILVER
# ==========================================================

def carregar_silver():

    tabelas = [
        "clientes",
        "produtos",
        "pedidos",
        "itens_pedido",
        "movimentos_estoque"
    ]

    dados = {}

    for tabela in tabelas:

        caminho = PROCESSED_DIR / f"{tabela}.parquet"

        if not caminho.exists():
            raise FileNotFoundError(
                f"Arquivo Silver nao encontrado: {caminho}"
            )

        dados[tabela] = pd.read_parquet(caminho)

        logging.info(
            "%s carregada: %s registros",
            tabela,
            f"{len(dados[tabela]):,}"
        )

    return dados


# ==========================================================
# DIMENSAO CLIENTE
# ==========================================================

def criar_dim_cliente(clientes):

    logging.info("Criando dim_cliente...")

    df = clientes.copy()

    df = df.sort_values("id_cliente").reset_index(drop=True)

    df.insert(
        0,
        "sk_cliente",
        np.arange(1, len(df) + 1)
    )

    return df[[
        "sk_cliente",
        "id_cliente",
        "nome",
        "cidade",
        "uf",
        "segmento",
        "data_cadastro"
    ]]


# ==========================================================
# DIMENSAO PRODUTO
# ==========================================================

def criar_dim_produto(produtos):

    logging.info("Criando dim_produto...")

    df = produtos.copy()

    df = df.sort_values("id_produto").reset_index(drop=True)

    df.insert(
        0,
        "sk_produto",
        np.arange(1, len(df) + 1)
    )

    return df[[
        "sk_produto",
        "id_produto",
        "descricao",
        "categoria",
        "marca",
        "custo",
        "preco_tabela"
    ]]


# ==========================================================
# DIMENSAO VENDEDOR
# ==========================================================

def criar_dim_vendedor(pedidos):

    logging.info("Criando dim_vendedor...")

    df = (
        pedidos[["id_vendedor"]]
        .drop_duplicates()
        .sort_values("id_vendedor")
        .reset_index(drop=True)
    )

    df.insert(
        0,
        "sk_vendedor",
        np.arange(1, len(df) + 1)
    )

    df["nome_vendedor"] = df["id_vendedor"].apply(
        lambda x: f"Vendedor {x:02d}"
    )

    return df[[
        "sk_vendedor",
        "id_vendedor",
        "nome_vendedor"
    ]]


# ==========================================================
# DIMENSAO DATA
# ==========================================================

def criar_dim_data(datas):

    logging.info("Criando dim_data...")

    datas = pd.to_datetime(datas).dropna()

    data_inicio = datas.min().normalize()
    data_fim = datas.max().normalize()

    calendario = pd.DataFrame({
        "data": pd.date_range(
            start=data_inicio,
            end=data_fim,
            freq="D"
        )
    })

    calendario["sk_data"] = (
        calendario["data"].dt.strftime("%Y%m%d").astype("int64")
    )

    calendario["ano"] = calendario["data"].dt.year
    calendario["mes"] = calendario["data"].dt.month
    calendario["nome_mes"] = calendario["data"].dt.month_name(
        locale="pt_BR.UTF-8"
    ) if False else calendario["data"].dt.month.map({
        1: "Janeiro",
        2: "Fevereiro",
        3: "Marco",
        4: "Abril",
        5: "Maio",
        6: "Junho",
        7: "Julho",
        8: "Agosto",
        9: "Setembro",
        10: "Outubro",
        11: "Novembro",
        12: "Dezembro"
    })

    calendario["trimestre"] = (
        calendario["data"].dt.quarter
    )

    calendario["dia"] = calendario["data"].dt.day

    calendario["dia_semana_numero"] = (
        calendario["data"].dt.dayofweek + 1
    )

    calendario["dia_semana"] = (
        calendario["dia_semana_numero"].map({
            1: "Segunda-feira",
            2: "Terca-feira",
            3: "Quarta-feira",
            4: "Quinta-feira",
            5: "Sexta-feira",
            6: "Sabado",
            7: "Domingo"
        })
    )

    calendario["fim_de_semana"] = (
        calendario["dia_semana_numero"] >= 6
    )

    anos = calendario["data"].dt.year.unique()

    feriados = holidays.country_holidays(
        "BR",
        subdiv="RS",
        years=anos
    )

    calendario["nome_feriado"] = (
        calendario["data"].dt.date.map(
            lambda d: feriados.get(d)
        )
    )

    calendario["feriado"] = (
        calendario["nome_feriado"].notna()
    )

    calendario["sk_data"] = calendario["sk_data"].astype("int64")

    return calendario[[
        "sk_data",
        "data",
        "ano",
        "mes",
        "nome_mes",
        "trimestre",
        "dia",
        "dia_semana_numero",
        "dia_semana",
        "fim_de_semana",
        "feriado",
        "nome_feriado"
    ]]


# ==========================================================
# FATO DE VENDAS
# ==========================================================

def criar_fato_vendas(
    itens,
    pedidos,
    dim_cliente,
    dim_produto,
    dim_data,
    dim_vendedor
):

    logging.info("Criando fato_vendas...")

    # Consideramos somente vendas efetivamente faturadas
    # ou entregues. Pedidos cancelados e em separacao
    # nao representam faturamento realizado.

    pedidos_validos = pedidos[
        pedidos["status"].isin([
            "Faturado",
            "Entregue"
        ])
    ].copy()

    df = itens.merge(
        pedidos_validos[[
            "id_pedido",
            "id_cliente",
            "data_pedido",
            "id_vendedor"
        ]],
        on="id_pedido",
        how="inner",
        validate="many_to_one"
    )

    # Relacionamento com produto
    df = df.merge(
        dim_produto[[
            "sk_produto",
            "id_produto",
            "custo",
            "preco_tabela"
        ]],
        on="id_produto",
        how="inner",
        validate="many_to_one"
    )

    # Relacionamento com cliente
    df = df.merge(
        dim_cliente[[
            "sk_cliente",
            "id_cliente"
        ]],
        on="id_cliente",
        how="inner",
        validate="many_to_one"
    )

    # Relacionamento com vendedor
    df = df.merge(
        dim_vendedor[[
            "sk_vendedor",
            "id_vendedor"
        ]],
        on="id_vendedor",
        how="inner",
        validate="many_to_one"
    )

    # Chave da dimensao data
    df["sk_data"] = (
        pd.to_datetime(df["data_pedido"])
        .dt.strftime("%Y%m%d")
        .astype("int64")
    )

    # Valor bruto
    df["valor_bruto"] = (
        df["quantidade"] * df["preco_tabela"]
    )

    # Valor liquido efetivamente praticado
    df["valor_liquido"] = (
        df["quantidade"] * df["preco_praticado"]
    )

    # Desconto financeiro
    df["valor_desconto"] = (
        df["valor_bruto"] - df["valor_liquido"]
    )

    # Custo total
    df["custo_total"] = (
        df["quantidade"] * df["custo"]
    )

    # Margem em valor
    df["margem"] = (
        df["valor_liquido"] - df["custo_total"]
    )

    # Identificador tecnico do item
    # A ordem de origem e preservada pelo processamento.
    df = df.reset_index(drop=True)

    df.insert(
        0,
        "id_item_pedido",
        np.arange(1, len(df) + 1)
    )

    # Arredondamento financeiro
    colunas_financeiras = [
        "valor_bruto",
        "valor_liquido",
        "valor_desconto",
        "custo_total",
        "margem"
    ]

    df[colunas_financeiras] = (
        df[colunas_financeiras].round(2)
    )

    fato = df[[
        "id_item_pedido",
        "id_pedido",
        "sk_cliente",
        "sk_produto",
        "sk_data",
        "sk_vendedor",
        "quantidade",
        "valor_bruto",
        "valor_desconto",
        "valor_liquido",
        "custo_total",
        "margem"
    ]].copy()

    logging.info(
        "Fato vendas criada: %s registros",
        f"{len(fato):,}"
    )

    return fato


# ==========================================================
# FATO DE ESTOQUE DIARIO
# ==========================================================

def criar_fato_estoque(
    movimentos,
    produtos,
    dim_produto,
    dim_data
):

    logging.info("Criando fato_estoque_diario...")

    df = movimentos.copy()

    df["data_movimento"] = pd.to_datetime(
        df["data_movimento"]
    )

    # Separacao das movimentacoes
    entradas = (
        df[df["tipo"] == "Entrada"]
        .groupby(["id_produto", "data_movimento"])
        ["quantidade"]
        .sum()
        .rename("quantidade_entrada")
    )

    saidas = (
        df[df["tipo"] == "Saida"]
        .groupby(["id_produto", "data_movimento"])
        ["quantidade"]
        .sum()
        .rename("quantidade_saida")
    )

    ajustes = (
        df[df["tipo"] == "Ajuste"]
        .groupby(["id_produto", "data_movimento"])
        ["quantidade"]
        .sum()
        .rename("quantidade_ajuste")
    )

    # Base diaria completa: todos os produtos x todas as datas
    datas = pd.to_datetime(dim_data["data"])

    produtos_ids = produtos["id_produto"].to_numpy()

    indice = pd.MultiIndex.from_product(
        [
            produtos_ids,
            datas
        ],
        names=[
            "id_produto",
            "data_movimento"
        ]
    )

    diario = pd.DataFrame(
        index=indice
    ).reset_index()

    # Aplicacao das movimentacoes diarias
    for movimento in [entradas, saidas, ajustes]:

        diario = diario.merge(
            movimento.reset_index(),
            on=["id_produto", "data_movimento"],
            how="left"
        )

    colunas_movimento = [
        "quantidade_entrada",
        "quantidade_saida",
        "quantidade_ajuste"
    ]

    diario[colunas_movimento] = (
        diario[colunas_movimento]
        .fillna(0)
    )

    # Variacao liquida do estoque
    diario["variacao_estoque"] = (
        diario["quantidade_entrada"]
        - diario["quantidade_saida"]
        + diario["quantidade_ajuste"]
    )

    # Saldo acumulado por produto
    diario = diario.sort_values(
        ["id_produto", "data_movimento"]
    )

    diario["saldo_estoque"] = (
        diario.groupby("id_produto")["variacao_estoque"]
        .cumsum()
    )

    # Relacionamento com a dimensao produto
    diario = diario.merge(
        dim_produto[[
            "sk_produto",
            "id_produto"
        ]],
        on="id_produto",
        how="inner",
        validate="many_to_one"
    )

    # Relacionamento com a dimensao data
    diario["sk_data"] = (
        diario["data_movimento"]
        .dt.strftime("%Y%m%d")
        .astype("int64")
    )

    fato = diario[[
        "sk_data",
        "sk_produto",
        "quantidade_entrada",
        "quantidade_saida",
        "quantidade_ajuste",
        "saldo_estoque"
    ]].copy()

    fato = fato.sort_values(
        ["sk_produto", "sk_data"]
    ).reset_index(drop=True)

    logging.info(
        "Fato estoque criada: %s registros",
        f"{len(fato):,}"
    )

    return fato


# ==========================================================
# SALVAMENTO DAS TABELAS GOLD
# ==========================================================

def salvar_gold(tabelas):

    GOLD_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    for nome, df in tabelas.items():

        caminho = GOLD_DIR / f"{nome}.parquet"

        df.to_parquet(
            caminho,
            index=False,
            engine="pyarrow"
        )

        logging.info(
            "%s salva: %s registros",
            nome,
            f"{len(df):,}"
        )


# ==========================================================
# EXECUCAO PRINCIPAL
# ==========================================================

def main():

    logging.info("=" * 60)
    logging.info("INICIANDO MODELAGEM DIMENSIONAL")
    logging.info("=" * 60)

    dados = carregar_silver()

    # Dimensoes
    dim_cliente = criar_dim_cliente(
        dados["clientes"]
    )

    dim_produto = criar_dim_produto(
        dados["produtos"]
    )

    dim_vendedor = criar_dim_vendedor(
        dados["pedidos"]
    )

    # Calendario considera vendas e estoque
    datas = pd.concat([
        dados["pedidos"]["data_pedido"],
        dados["movimentos_estoque"]["data_movimento"]
    ])

    dim_data = criar_dim_data(datas)

    # Fatos
    fato_vendas = criar_fato_vendas(
        dados["itens_pedido"],
        dados["pedidos"],
        dim_cliente,
        dim_produto,
        dim_data,
        dim_vendedor
    )

    fato_estoque = criar_fato_estoque(
        dados["movimentos_estoque"],
        dados["produtos"],
        dim_produto,
        dim_data
    )

    tabelas = {
        "dim_cliente": dim_cliente,
        "dim_produto": dim_produto,
        "dim_vendedor": dim_vendedor,
        "dim_data": dim_data,
        "fato_vendas": fato_vendas,
        "fato_estoque_diario": fato_estoque
    }

    salvar_gold(tabelas)

    logging.info("=" * 60)
    logging.info("MODELAGEM DIMENSIONAL FINALIZADA")
    logging.info("=" * 60)


if __name__ == "__main__":
    main()
