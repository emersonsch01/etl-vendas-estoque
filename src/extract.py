from pathlib import Path
import logging
import pandas as pd


# ==========================================================
# CONFIGURAÇÕES
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"

TABELAS = [
    "clientes",
    "produtos",
    "pedidos",
    "itens_pedido",
    "movimentos_estoque"
]


# ==========================================================
# EXTRAÇÃO
# ==========================================================

def extrair_tabela(nome_tabela):

    caminho = RAW_DIR / f"{nome_tabela}.csv"

    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {caminho}"
        )

    logging.info(
        "Extraindo tabela: %s",
        nome_tabela
    )

    df = pd.read_csv(
        caminho,
        encoding="utf-8-sig"
    )

    logging.info(
        "%s: %s linhas extraídas",
        nome_tabela,
        f"{len(df):,}"
    )

    return df


def extrair_todas():

    dados = {}

    for tabela in TABELAS:

        dados[tabela] = extrair_tabela(tabela)

    logging.info(
        "Extração finalizada: %s tabelas",
        len(dados)
    )

    return dados
