from pathlib import Path
from datetime import date
import logging

import numpy as np
import pandas as pd
from faker import Faker


# ==========================================================
# CONFIGURAÇÕES
# ==========================================================

SEED = 42

DATA_INICIAL = "2024-01-01"
DATA_FINAL = date.today().isoformat()

QTD_CLIENTES = 2_000
QTD_PRODUTOS = 500
QTD_VENDEDORES = 20
QTD_PEDIDOS = 50_000

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"

rng = np.random.default_rng(SEED)
fake = Faker("pt_BR")
Faker.seed(SEED)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# Categorias comerciais
CATEGORIAS = [
    "Ferramentas Manuais",
    "Discos de Corte",
    "Discos de Desbaste",
    "Discos Flap",
    "Brocas",
    "Abrasivos",
    "Acessórios"
]

MARCAS = [
    "Industrial Pro",
    "MaxForce",
    "UltraTools",
    "Fortex",
    "MasterCut",
    "ProSteel",
    "PowerFix"
]

SEGMENTOS = [
    "Ferragem",
    "Industria",
    "Marmoraria",
    "Serralheria",
    "Construcao Civil",
    "Distribuidor"
]

VENDEDORES = [
    f"Vendedor {i:02d}" for i in range(1, QTD_VENDEDORES + 1)
]

CIDADES_RS = [
    "Porto Alegre",
    "Canoas",
    "Gravatai",
    "Cachoeirinha",
    "Guaiba",
    "Esteio",
    "Sapucaia do Sul",
    "Sao Leopoldo",
    "Novo Hamburgo",
    "Caxias do Sul",
    "Pelotas",
    "Santa Maria",
    "Passo Fundo",
    "Rio Grande",
    "Lajeado",
    "Camaqua"
]


# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================

def gerar_datas_sazonais(quantidade):
    """
    Gera datas com distribuição sazonal.
    Novembro, maio e dezembro possuem maior volume.
    """

    inicio = pd.Timestamp(DATA_INICIAL)
    fim = pd.Timestamp(DATA_FINAL)

    meses = np.arange(1, 13)

    pesos = np.array([
        0.75, 0.75, 0.85, 0.90,
        1.15, 0.90, 0.85, 0.90,
        0.95, 1.00, 1.35, 1.25
    ])

    pesos = pesos / pesos.sum()

    datas = []

    for _ in range(quantidade):
        mes = rng.choice(meses, p=pesos)

        ano = rng.integers(
            inicio.year,
            fim.year + 1
        )

        primeiro_dia = pd.Timestamp(
            year=ano,
            month=int(mes),
            day=1
        )

        ultimo_dia = primeiro_dia + pd.offsets.MonthEnd(0)

        primeiro_dia = max(primeiro_dia, inicio)
        ultimo_dia = min(ultimo_dia, fim)

        if primeiro_dia > ultimo_dia:
            datas.append(inicio)
            continue

        dias = (ultimo_dia - primeiro_dia).days + 1

        data_gerada = primeiro_dia + pd.Timedelta(
            days=int(rng.integers(0, dias))
        )

        datas.append(data_gerada)

    return pd.to_datetime(datas)


def salvar_csv(df, nome):
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    caminho = RAW_DIR / f"{nome}.csv"

    df.to_csv(
        caminho,
        index=False,
        encoding="utf-8-sig"
    )

    logging.info(
        "%s: %s registros salvos",
        nome,
        f"{len(df):,}"
    )


# ==========================================================
# 1. CLIENTES
# ==========================================================

def gerar_clientes():

    logging.info("Gerando clientes...")

    clientes = []

    for i in range(1, QTD_CLIENTES + 1):

        clientes.append({
            "id_cliente": i,
            "nome": fake.company(),
            "cidade": rng.choice(CIDADES_RS),
            "uf": "RS",
            "segmento": rng.choice(SEGMENTOS),
            "data_cadastro": fake.date_between(
                start_date="-5y",
                end_date="today"
            )
        })

    df = pd.DataFrame(clientes)

    # Inconsistências propositais:
    # duplicação de registros
    duplicados = df.sample(
        n=20,
        random_state=SEED
    ).copy()

    # Variação de caixa em alguns nomes
    duplicados["nome"] = duplicados["nome"].str.upper()

    df = pd.concat(
        [df, duplicados],
        ignore_index=True
    )

    return df


# ==========================================================
# 2. PRODUTOS
# ==========================================================

def gerar_produtos():

    logging.info("Gerando produtos...")

    produtos = []

    for i in range(1, QTD_PRODUTOS + 1):

        categoria = rng.choice(CATEGORIAS)

        custo = round(
            rng.uniform(2, 250),
            2
        )

        margem_precificada = rng.uniform(1.25, 2.20)

        preco = round(
            custo * margem_precificada,
            2
        )

        produtos.append({
            "id_produto": i,
            "descricao": f"{categoria} Modelo {i:04d}",
            "categoria": categoria,
            "marca": rng.choice(MARCAS),
            "custo": custo,
            "preco_tabela": preco
        })

    df = pd.DataFrame(produtos)

    # Inconsistência proposital de texto
    df.loc[10:14, "categoria"] = (
        df.loc[10:14, "categoria"].str.upper()
    )

    return df


# ==========================================================
# 3. PEDIDOS
# ==========================================================

def gerar_pedidos(clientes):

    logging.info("Gerando pedidos...")

    ids_clientes = clientes[
        clientes["id_cliente"].duplicated(keep="first") == False
    ]["id_cliente"].to_numpy()

    pedidos = pd.DataFrame({
        "id_pedido": np.arange(1, QTD_PEDIDOS + 1),
        "id_cliente": rng.choice(
            ids_clientes,
            size=QTD_PEDIDOS
        ),
        "data_pedido": gerar_datas_sazonais(QTD_PEDIDOS),
        "status": rng.choice(
            ["Faturado", "Entregue", "Cancelado", "Em separacao"],
            size=QTD_PEDIDOS,
            p=[0.55, 0.30, 0.08, 0.07]
        ),
        "id_vendedor": rng.integers(
            1,
            QTD_VENDEDORES + 1,
            size=QTD_PEDIDOS
        )
    })

    # Inconsistências propositais:
    # datas inválidas representadas como texto
    indices = pedidos.sample(
        n=10,
        random_state=SEED
    ).index

    pedidos["data_pedido"] = (
        pedidos["data_pedido"].astype(str)
    )

    pedidos.loc[indices, "data_pedido"] = "2026-15-45"

    return pedidos


# ==========================================================
# 4. ITENS DOS PEDIDOS
# ==========================================================

def gerar_itens_pedido(pedidos, produtos):

    logging.info("Gerando itens dos pedidos...")

    # Distribuição desigual de vendas:
    # alguns produtos vendem muito mais que outros.
    pesos_produtos = 1 / np.arange(
        1,
        len(produtos) + 1
    ) ** 0.85

    pesos_produtos = (
        pesos_produtos / pesos_produtos.sum()
    )

    quantidades_itens = rng.integers(
        1,
        9,
        size=len(pedidos)
    )

    ids_pedidos = np.repeat(
        pedidos["id_pedido"].to_numpy(),
        quantidades_itens
    )

    ids_produtos = rng.choice(
        produtos["id_produto"].to_numpy(),
        size=len(ids_pedidos),
        p=pesos_produtos
    )

    quantidades = rng.integers(
        1,
        31,
        size=len(ids_pedidos)
    )

    tabela_produtos = produtos.set_index("id_produto")

    custos = tabela_produtos.loc[
        ids_produtos, "custo"
    ].to_numpy()

    precos = tabela_produtos.loc[
        ids_produtos, "preco_tabela"
    ].to_numpy()

    descontos = rng.choice(
        [0, 2, 5, 8, 10, 12, 15],
        size=len(ids_pedidos),
        p=[0.20, 0.10, 0.25, 0.20, 0.15, 0.07, 0.03]
    )

    precos_praticados = np.round(
        precos * (1 - descontos / 100),
        2
    )

    itens = pd.DataFrame({
        "id_pedido": ids_pedidos,
        "id_produto": ids_produtos,
        "quantidade": quantidades,
        "preco_praticado": precos_praticados,
        "desconto_percentual": descontos
    })

    # Inconsistências propositais
    indices = itens.sample(
        frac=0.002,
        random_state=SEED
    ).index

    itens.loc[indices[:len(indices)//2], "quantidade"] *= -1

    itens.loc[indices[len(indices)//2:], "preco_praticado"] = np.nan

    return itens


# ==========================================================
# 5. MOVIMENTAÇÕES DE ESTOQUE
# ==========================================================


def gerar_movimentos_estoque(
    pedidos,
    itens,
    produtos
):

    logging.info("Gerando movimentos de estoque...")

    # 1. Identificar pedidos válidos
    pedidos_estoque = pedidos.copy()

    pedidos_estoque["data_estoque"] = pd.to_datetime(
        pedidos_estoque["data_pedido"],
        errors="coerce"
    )

    pedidos_validos = pedidos_estoque[
        pedidos_estoque["status"].isin(
            ["Faturado", "Entregue"]
        )
        & pedidos_estoque["data_estoque"].notna()
    ]

    # 2. Identificar itens válidos
    itens_estoque = itens.merge(
        pedidos_validos[
            ["id_pedido", "data_estoque"]
        ],
        on="id_pedido",
        how="inner"
    )

    itens_validos_estoque = itens_estoque[
        itens_estoque["id_produto"].isin(
            produtos["id_produto"]
        )
        & itens_estoque["quantidade"].notna()
        & (itens_estoque["quantidade"] > 0)
        & itens_estoque["preco_praticado"].notna()
        & (itens_estoque["preco_praticado"] > 0)
        & itens_estoque["desconto_percentual"].notna()
        & itens_estoque["desconto_percentual"].between(0, 100)
    ].copy()

    # 3. Agrupar saídas por produto e data
    saidas = (
        itens_validos_estoque
        .groupby(
            ["id_produto", "data_estoque"],
            as_index=False
        )["quantidade"]
        .sum()
    )

    saidas = saidas.rename(
        columns={
            "data_estoque": "data_movimento"
        }
    )

    saidas["tipo"] = "Saida"

    # 4. Criar estoque inicial
    saldo_inicial = pd.DataFrame({
        "id_produto": produtos["id_produto"],
        "data_movimento": pd.Timestamp(DATA_INICIAL),
        "tipo": "Entrada",
        "quantidade": rng.integers(
            100,
            1001,
            size=len(produtos)
        )
    })

    # 5. Gerar ajustes ANTES das reposições
    qtd_ajustes = 1000

    ajustes = pd.DataFrame({
        "id_produto": rng.choice(
            produtos["id_produto"],
            size=qtd_ajustes
        ),
        "data_movimento": gerar_datas_sazonais(
            qtd_ajustes
        ),
        "tipo": "Ajuste",
        "quantidade": rng.integers(
            -20,
            21,
            size=qtd_ajustes
        )
    })

    # 6. Simular reposições considerando vendas e ajustes
    reposicoes = []

    saldos = saldo_inicial.set_index(
        "id_produto"
    )["quantidade"].to_dict()

    for id_produto in produtos["id_produto"]:

        # Demanda diária do produto
        demanda_produto = (
            saidas[
                saidas["id_produto"] == id_produto
            ]
            .set_index("data_movimento")["quantidade"]
            .to_dict()
        )

        # Ajustes diários do produto
        ajustes_produto = (
            ajustes[
                ajustes["id_produto"] == id_produto
            ]
            .groupby("data_movimento")["quantidade"]
            .sum()
            .to_dict()
        )

        # Todas as datas em que houve venda ou ajuste
        datas_movimento = sorted(
            set(demanda_produto.keys())
            | set(ajustes_produto.keys())
        )

        saldo_atual = int(saldos[id_produto])

        for data in datas_movimento:

            demanda = int(
                demanda_produto.get(data, 0)
            )

            ajuste = int(
                ajustes_produto.get(data, 0)
            )

            # Saldo projetado após vendas e ajustes
            saldo_projetado = (
                saldo_atual
                + ajuste
                - demanda
            )

            # Repor somente quando necessário
            if saldo_projetado < 0:

                base_margem = max(
                    demanda,
                    abs(ajuste),
                    1
                )

                margem_seguranca = max(
                    1,
                    int(np.ceil(base_margem * 0.25))
                )

                quantidade_reposicao = (
                    abs(saldo_projetado)
                    + margem_seguranca
                )

                reposicoes.append({
                    "id_produto": id_produto,
                    "data_movimento": data,
                    "tipo": "Entrada",
                    "quantidade": quantidade_reposicao
                })

                saldo_projetado += quantidade_reposicao

            # Atualizar saldo para o próximo dia
            saldo_atual = saldo_projetado

    entradas = pd.DataFrame(
        reposicoes,
        columns=[
            "id_produto",
            "data_movimento",
            "tipo",
            "quantidade"
        ]
    )

    # 7. Consolidar todos os movimentos
    movimentos = pd.concat(
        [
            saldo_inicial,
            entradas,
            saidas,
            ajustes
        ],
        ignore_index=True
    )

    return movimentos


# ==========================================================
# EXECUÇÃO PRINCIPAL
# ==========================================================

def main():

    logging.info("=" * 60)
    logging.info("INICIANDO GERACAO DOS DADOS")
    logging.info("=" * 60)

    clientes = gerar_clientes()

    produtos = gerar_produtos()

    pedidos = gerar_pedidos(clientes)

    itens = gerar_itens_pedido(
        pedidos,
        produtos
    )

    movimentos = gerar_movimentos_estoque(
        pedidos,
        itens,
        produtos
    )

    salvar_csv(clientes, "clientes")
    salvar_csv(produtos, "produtos")
    salvar_csv(pedidos, "pedidos")
    salvar_csv(itens, "itens_pedido")
    salvar_csv(movimentos, "movimentos_estoque")

    logging.info("=" * 60)
    logging.info("GERACAO FINALIZADA COM SUCESSO")
    logging.info("=" * 60)


if __name__ == "__main__":
    main()
