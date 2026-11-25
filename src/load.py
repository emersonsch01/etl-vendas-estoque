from pathlib import Path
import os
import logging

import pandas as pd
from google.cloud import bigquery


# =====================================================
# CONFIGURAÇÕES
# =====================================================

BASE_DIR = Path(__file__).resolve().parents[1]

GOLD_DIR = BASE_DIR / "data" / "gold"

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
DATASET_ID = "vendas_estoque"

TABELAS = [
    "dim_cliente",
    "dim_produto",
    "dim_vendedor",
    "dim_data",
    "fato_vendas",
    "fato_estoque_diario",
]


# =====================================================
# LOGGING
# =====================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# =====================================================
# CLIENTE BIGQUERY
# =====================================================

def criar_cliente():

    if not PROJECT_ID:
        raise ValueError(
            "Defina a variável de ambiente GCP_PROJECT_ID."
        )

    return bigquery.Client(project=PROJECT_ID)


# =====================================================
# CARGA DAS TABELAS
# =====================================================

def carregar_tabela(client, nome_tabela):

    caminho = GOLD_DIR / f"{nome_tabela}.parquet"

    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {caminho}"
        )

    logging.info(f"Lendo arquivo: {nome_tabela}")

    df = pd.read_parquet(caminho)

    tabela_destino = (
        f"{PROJECT_ID}.{DATASET_ID}.{nome_tabela}"
    )

    configuracao = bigquery.LoadJobConfig(
        autodetect=True,
        write_disposition="WRITE_TRUNCATE"
    )

    logging.info(
        f"Iniciando carga no BigQuery: {tabela_destino}"
    )

    job = client.load_table_from_dataframe(
        df,
        tabela_destino,
        job_config=configuracao
    )

    job.result()

    tabela = client.get_table(tabela_destino)

    logging.info(
        f"Tabela {nome_tabela} carregada com "
        f"{tabela.num_rows} registros."
    )

    return tabela.num_rows


# =====================================================
# EXECUÇÃO DA CARGA COMPLETA
# =====================================================

def executar_carga():

    client = criar_cliente()

    resultados = {}

    for nome_tabela in TABELAS:

        quantidade = carregar_tabela(
            client,
            nome_tabela
        )

        resultados[nome_tabela] = quantidade

    logging.info("Carga finalizada com sucesso!")

    print("\nRESUMO DA CARGA")

    for tabela, quantidade in resultados.items():

        print(
            f"{tabela}: {quantidade:,} registros"
        )


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":
    executar_carga()
