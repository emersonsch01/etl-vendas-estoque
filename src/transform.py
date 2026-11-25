from pathlib import Path
import logging
import unicodedata

import pandas as pd

from extract import extrair_todas


# ==========================================================
# CONFIGURAÇÕES
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = BASE_DIR / "data" / "processed"
REJECTED_DIR = BASE_DIR / "data" / "rejected"


# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================

def padronizar_texto(valor):

    if pd.isna(valor):
        return None

    texto = str(valor).strip()

    texto = " ".join(texto.split())

    texto = unicodedata.normalize(
        "NFKD",
        texto
    ).encode(
        "ASCII",
        "ignore"
    ).decode("ASCII")

    return texto.title()


def registrar_rejeicoes(
    df,
    tabela,
    motivo,
    rejeicoes
):

    if df.empty:
        return

    resultado = df.copy()

    resultado["_tabela"] = tabela
    resultado["_motivo_rejeicao"] = motivo

    rejeicoes.append(resultado)


def salvar_parquet(df, tabela):

    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    caminho = PROCESSED_DIR / f"{tabela}.parquet"

    df.to_parquet(
        caminho,
        index=False,
        engine="pyarrow"
    )

    logging.info(
        "%s: %s registros aprovados",
        tabela,
        f"{len(df):,}"
    )


def salvar_rejeicoes(rejeicoes, tabela):

    REJECTED_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    if rejeicoes:

        df_rejeitados = pd.concat(
            rejeicoes,
            ignore_index=True
        )

    else:

        df_rejeitados = pd.DataFrame()

    caminho = REJECTED_DIR / f"{tabela}_rejeitados.csv"

    df_rejeitados.to_csv(
        caminho,
        index=False,
        encoding="utf-8-sig"
    )

    logging.info(
        "%s: %s registros rejeitados",
        tabela,
        f"{len(df_rejeitados):,}"
    )

    return df_rejeitados


# ==========================================================
# 1. CLIENTES
# ==========================================================

def transformar_clientes(df):

    logging.info("Transformando clientes...")

    df = df.copy().reset_index(drop=True)

    df["_linha_origem"] = df.index + 2

    rejeicoes = []

    # Conversão da chave
    df["id_cliente"] = pd.to_numeric(
        df["id_cliente"],
        errors="coerce"
    )

    invalidos = (
        df["id_cliente"].isna()
        | (df["id_cliente"] <= 0)
    )

    registrar_rejeicoes(
        df[invalidos],
        "clientes",
        "ID de cliente inválido",
        rejeicoes
    )

    df = df[~invalidos].copy()

    df["id_cliente"] = df["id_cliente"].astype("int64")

    # Padronização de textos
    for coluna in ["nome", "cidade", "segmento"]:

        df[coluna] = df[coluna].apply(
            padronizar_texto
        )

    df["uf"] = (
        df["uf"]
        .astype("string")
        .str.strip()
        .str.upper()
    )

    # Tratamento de datas
    df["data_cadastro"] = pd.to_datetime(
        df["data_cadastro"],
        errors="coerce"
    )

    invalidos = (
        df["data_cadastro"].isna()
        | df["nome"].isna()
        | df["cidade"].isna()
        | df["segmento"].isna()
        | df["uf"].isna()
    )

    registrar_rejeicoes(
        df[invalidos],
        "clientes",
        "Campos obrigatorios invalidos",
        rejeicoes
    )

    df = df[~invalidos].copy()

    # Remoção de duplicidades
    duplicados = df.duplicated(
        subset=["id_cliente"],
        keep="first"
    )

    registrar_rejeicoes(
        df[duplicados],
        "clientes",
        "Cliente duplicado",
        rejeicoes
    )

    df = df[~duplicados].copy()

    # Remoção de colunas técnicas
    df = df.drop(
        columns=["_linha_origem"]
    )

    salvar_rejeicoes(rejeicoes, "clientes")

    return df


# ==========================================================
# 2. PRODUTOS
# ==========================================================

def transformar_produtos(df):

    logging.info("Transformando produtos...")

    df = df.copy().reset_index(drop=True)

    df["_linha_origem"] = df.index + 2

    rejeicoes = []

    df["id_produto"] = pd.to_numeric(
        df["id_produto"],
        errors="coerce"
    )

    df["custo"] = pd.to_numeric(
        df["custo"],
        errors="coerce"
    )

    df["preco_tabela"] = pd.to_numeric(
        df["preco_tabela"],
        errors="coerce"
    )

    invalidos = (
        df["id_produto"].isna()
        | (df["id_produto"] <= 0)
        | df["custo"].isna()
        | (df["custo"] <= 0)
        | df["preco_tabela"].isna()
        | (df["preco_tabela"] <= 0)
    )

    registrar_rejeicoes(
        df[invalidos],
        "produtos",
        "ID ou valores financeiros invalidos",
        rejeicoes
    )

    df = df[~invalidos].copy()

    df["id_produto"] = df["id_produto"].astype("int64")

    for coluna in ["descricao", "categoria", "marca"]:

        df[coluna] = df[coluna].apply(
            padronizar_texto
        )

    invalidos = (
        df["descricao"].isna()
        | df["categoria"].isna()
        | df["marca"].isna()
    )

    registrar_rejeicoes(
        df[invalidos],
        "produtos",
        "Descricao, categoria ou marca ausente",
        rejeicoes
    )

    df = df[~invalidos].copy()

    duplicados = df.duplicated(
        subset=["id_produto"],
        keep="first"
    )

    registrar_rejeicoes(
        df[duplicados],
        "produtos",
        "Produto duplicado",
        rejeicoes
    )

    df = df[~duplicados].copy()

    df["custo"] = df["custo"].round(2)
    df["preco_tabela"] = df["preco_tabela"].round(2)

    df = df.drop(
        columns=["_linha_origem"]
    )

    salvar_rejeicoes(rejeicoes, "produtos")

    return df


# ==========================================================
# 3. PEDIDOS
# ==========================================================

def transformar_pedidos(df, clientes):

    logging.info("Transformando pedidos...")

    df = df.copy().reset_index(drop=True)

    df["_linha_origem"] = df.index + 2

    rejeicoes = []

    for coluna in [
        "id_pedido",
        "id_cliente",
        "id_vendedor"
    ]:

        df[coluna] = pd.to_numeric(
            df[coluna],
            errors="coerce"
        )

    df["data_pedido"] = pd.to_datetime(
        df["data_pedido"],
        errors="coerce"
    )

    df["status"] = df["status"].apply(
        padronizar_texto
    )

    invalidos = (
        df["id_pedido"].isna()
        | (df["id_pedido"] <= 0)
        | df["id_cliente"].isna()
        | df["id_vendedor"].isna()
        | df["data_pedido"].isna()
        | df["status"].isna()
    )

    registrar_rejeicoes(
        df[invalidos],
        "pedidos",
        "Pedido com campos invalidos",
        rejeicoes
    )

    df = df[~invalidos].copy()

    for coluna in [
        "id_pedido",
        "id_cliente",
        "id_vendedor"
    ]:

        df[coluna] = df[coluna].astype("int64")

    # Verificação da existência do cliente
    clientes_validos = set(
        clientes["id_cliente"]
    )

    invalidos = ~df["id_cliente"].isin(
        clientes_validos
    )

    registrar_rejeicoes(
        df[invalidos],
        "pedidos",
        "Cliente inexistente",
        rejeicoes
    )

    df = df[~invalidos].copy()

    # Verificação do vendedor
    invalidos = ~df["id_vendedor"].between(1, 20)

    registrar_rejeicoes(
        df[invalidos],
        "pedidos",
        "Vendedor inexistente",
        rejeicoes
    )

    df = df[~invalidos].copy()

    # Remoção de pedidos duplicados
    duplicados = df.duplicated(
        subset=["id_pedido"],
        keep="first"
    )

    registrar_rejeicoes(
        df[duplicados],
        "pedidos",
        "Pedido duplicado",
        rejeicoes
    )

    df = df[~duplicados].copy()

    df = df.drop(
        columns=["_linha_origem"]
    )

    salvar_rejeicoes(rejeicoes, "pedidos")

    return df


# ==========================================================
# 4. ITENS DOS PEDIDOS
# ==========================================================

def transformar_itens(
    df,
    pedidos,
    produtos
):

    logging.info("Transformando itens dos pedidos...")

    df = df.copy().reset_index(drop=True)

    df["_linha_origem"] = df.index + 2

    rejeicoes = []

    for coluna in [
        "id_pedido",
        "id_produto",
        "quantidade"
    ]:

        df[coluna] = pd.to_numeric(
            df[coluna],
            errors="coerce"
        )

    for coluna in [
        "preco_praticado",
        "desconto_percentual"
    ]:

        df[coluna] = pd.to_numeric(
            df[coluna],
            errors="coerce"
        )

    # Validação de valores obrigatórios
    invalidos = (
        df["id_pedido"].isna()
        | df["id_produto"].isna()
        | df["quantidade"].isna()
        | df["preco_praticado"].isna()
        | df["desconto_percentual"].isna()
        | (df["quantidade"] <= 0)
        | (df["preco_praticado"] <= 0)
        | (~df["desconto_percentual"].between(0, 100))
    )

    registrar_rejeicoes(
        df[invalidos],
        "itens_pedido",
        "Quantidade, preco ou desconto invalido",
        rejeicoes
    )

    df = df[~invalidos].copy()

    for coluna in [
        "id_pedido",
        "id_produto",
        "quantidade"
    ]:

        df[coluna] = df[coluna].astype("int64")

    df["preco_praticado"] = (
        df["preco_praticado"].round(2)
    )

    df["desconto_percentual"] = (
        df["desconto_percentual"].round(2)
    )

    # Integridade referencial: pedido
    pedidos_validos = set(
        pedidos["id_pedido"]
    )

    invalidos = ~df["id_pedido"].isin(
        pedidos_validos
    )

    registrar_rejeicoes(
        df[invalidos],
        "itens_pedido",
        "Pedido inexistente ou rejeitado",
        rejeicoes
    )

    df = df[~invalidos].copy()

    # Integridade referencial: produto
    produtos_validos = set(
        produtos["id_produto"]
    )

    invalidos = ~df["id_produto"].isin(
        produtos_validos
    )

    registrar_rejeicoes(
        df[invalidos],
        "itens_pedido",
        "Produto inexistente",
        rejeicoes
    )

    df = df[~invalidos].copy()

    df = df.drop(
        columns=["_linha_origem"]
    )

    salvar_rejeicoes(rejeicoes, "itens_pedido")

    return df


# ==========================================================
# 5. MOVIMENTAÇÕES DE ESTOQUE
# ==========================================================

def transformar_estoque(df, produtos):

    logging.info("Transformando movimentos de estoque...")

    df = df.copy().reset_index(drop=True)

    df["_linha_origem"] = df.index + 2

    rejeicoes = []

    df["id_produto"] = pd.to_numeric(
        df["id_produto"],
        errors="coerce"
    )

    df["quantidade"] = pd.to_numeric(
        df["quantidade"],
        errors="coerce"
    )

    df["data_movimento"] = pd.to_datetime(
        df["data_movimento"],
        errors="coerce"
    )

    df["tipo"] = df["tipo"].apply(
        padronizar_texto
    )

    invalidos = (
        df["id_produto"].isna()
        | df["quantidade"].isna()
        | df["data_movimento"].isna()
        | df["tipo"].isna()
    )

    registrar_rejeicoes(
        df[invalidos],
        "movimentos_estoque",
        "Campos obrigatorios invalidos",
        rejeicoes
    )

    df = df[~invalidos].copy()

    df["id_produto"] = df["id_produto"].astype("int64")

    # Tipos de movimentação permitidos
    tipos_validos = [
        "Entrada",
        "Saida",
        "Ajuste"
    ]

    invalidos = ~df["tipo"].isin(
        tipos_validos
    )

    registrar_rejeicoes(
        df[invalidos],
        "movimentos_estoque",
        "Tipo de movimentacao invalido",
        rejeicoes
    )

    df = df[~invalidos].copy()

    # Entrada e saída devem ser positivas
    invalidos = (
        df["tipo"].isin(["Entrada", "Saida"])
        & (df["quantidade"] <= 0)
    )

    registrar_rejeicoes(
        df[invalidos],
        "movimentos_estoque",
        "Quantidade invalida para entrada ou saida",
        rejeicoes
    )

    df = df[~invalidos].copy()

    # Ajustes precisam alterar o saldo
    invalidos = (
        (df["tipo"] == "Ajuste")
        & (df["quantidade"] == 0)
    )

    registrar_rejeicoes(
        df[invalidos],
        "movimentos_estoque",
        "Ajuste sem alteracao de saldo",
        rejeicoes
    )

    df = df[~invalidos].copy()

    produtos_validos = set(
        produtos["id_produto"]
    )

    invalidos = ~df["id_produto"].isin(
        produtos_validos
    )

    registrar_rejeicoes(
        df[invalidos],
        "movimentos_estoque",
        "Produto inexistente",
        rejeicoes
    )

    df = df[~invalidos].copy()

    df["quantidade"] = df["quantidade"].astype("int64")

    df = df.drop(
        columns=["_linha_origem"]
    )

    salvar_rejeicoes(
        rejeicoes,
        "movimentos_estoque"
    )

    return df


# ==========================================================
# ORQUESTRADOR DA TRANSFORMACAO
# ==========================================================

def transformar_todos(dados):

    logging.info("=" * 60)
    logging.info("INICIANDO TRANSFORMACOES")
    logging.info("=" * 60)

    clientes = transformar_clientes(
        dados["clientes"]
    )

    produtos = transformar_produtos(
        dados["produtos"]
    )

    pedidos = transformar_pedidos(
        dados["pedidos"],
        clientes
    )

    itens = transformar_itens(
        dados["itens_pedido"],
        pedidos,
        produtos
    )

    estoque = transformar_estoque(
        dados["movimentos_estoque"],
        produtos
    )

    processados = {
        "clientes": clientes,
        "produtos": produtos,
        "pedidos": pedidos,
        "itens_pedido": itens,
        "movimentos_estoque": estoque
    }

    for nome, df in processados.items():

        salvar_parquet(df, nome)

    logging.info("=" * 60)
    logging.info("TRANSFORMACOES FINALIZADAS")
    logging.info("=" * 60)

    return processados


# ==========================================================
# EXECUCAO INDEPENDENTE
# ==========================================================

def main():

    dados = extrair_todas()

    transformar_todos(dados)


if __name__ == "__main__":

    main()
