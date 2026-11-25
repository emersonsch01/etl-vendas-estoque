SELECT

    d.ano,
    d.mes,
    d.nome_mes,

    DATE_TRUNC(d.data, MONTH) AS mes_referencia,

    COUNT(DISTINCT f.id_pedido) AS total_pedidos,

    SUM(f.quantidade) AS unidades_vendidas,

    ROUND(SUM(f.valor_bruto), 2) AS faturamento_bruto,

    ROUND(SUM(f.valor_desconto), 2) AS total_descontos,

    ROUND(SUM(f.valor_liquido), 2) AS faturamento_liquido,

    ROUND(SUM(f.custo_total), 2) AS custo_total,

    ROUND(SUM(f.margem), 2) AS margem_total

FROM `vendas_estoque.fato_vendas` f

INNER JOIN `vendas_estoque.dim_data` d
    ON f.sk_data = d.sk_data

GROUP BY
    d.ano,
    d.mes,
    d.nome_mes,
    mes_referencia


# ---------------------------------- #


CREATE OR REPLACE VIEW
    `vendas_estoque.vw_faturamento_cliente` AS

SELECT
    c.sk_cliente,
    c.id_cliente,
    c.nome,
    c.cidade,
    c.uf,
    c.segmento,

    COUNT(DISTINCT f.id_pedido) AS total_pedidos,

    SUM(f.quantidade) AS unidades_compradas,

    ROUND(SUM(f.valor_bruto), 2) AS faturamento_bruto,

    ROUND(SUM(f.valor_desconto), 2) AS total_descontos,

    ROUND(SUM(f.valor_liquido), 2) AS faturamento_liquido,

    ROUND(SUM(f.custo_total), 2) AS custo_total,

    ROUND(SUM(f.margem), 2) AS margem_total

FROM `vendas_estoque.fato_vendas` f

INNER JOIN `vendas_estoque.dim_cliente` c
    ON f.sk_cliente = c.sk_cliente

GROUP BY
    c.sk_cliente,
    c.id_cliente,
    c.nome,
    c.cidade,
    c.uf,
    c.segmento;


# ---------------------------------- #


CREATE OR REPLACE VIEW
    `vendas_estoque.vw_desempenho_produto` AS

SELECT
    p.sk_produto,
    p.id_produto,
    p.descricao,
    p.categoria,
    p.marca,

    COUNT(DISTINCT f.id_pedido) AS total_pedidos,

    SUM(f.quantidade) AS unidades_vendidas,

    ROUND(SUM(f.valor_bruto), 2) AS faturamento_bruto,

    ROUND(SUM(f.valor_desconto), 2) AS total_descontos,

    ROUND(SUM(f.valor_liquido), 2) AS faturamento_liquido,

    ROUND(SUM(f.custo_total), 2) AS custo_total,

    ROUND(SUM(f.margem), 2) AS margem_total

FROM `vendas_estoque.fato_vendas` f

INNER JOIN `vendas_estoque.dim_produto` p
    ON f.sk_produto = p.sk_produto

GROUP BY
    p.sk_produto,
    p.id_produto,
    p.descricao,
    p.categoria,
    p.marca;


# ---------------------------------- #


CREATE OR REPLACE VIEW
    `vendas_estoque.vw_desempenho_categoria` AS

SELECT
    p.categoria,

    COUNT(DISTINCT p.sk_produto) AS produtos_vendidos,

    COUNT(DISTINCT f.id_pedido) AS total_pedidos,

    SUM(f.quantidade) AS unidades_vendidas,

    ROUND(SUM(f.valor_bruto), 2) AS faturamento_bruto,

    ROUND(SUM(f.valor_desconto), 2) AS total_descontos,

    ROUND(SUM(f.valor_liquido), 2) AS faturamento_liquido,

    ROUND(SUM(f.custo_total), 2) AS custo_total,

    ROUND(SUM(f.margem), 2) AS margem_total

FROM `vendas_estoque.fato_vendas` f

INNER JOIN `vendas_estoque.dim_produto` p
    ON f.sk_produto = p.sk_produto

GROUP BY
    p.categoria;


# ---------------------------------- #


CREATE OR REPLACE VIEW
    `vendas_estoque.vw_desempenho_vendedor` AS

SELECT
    v.sk_vendedor,
    v.id_vendedor,
    v.nome_vendedor,

    COUNT(DISTINCT f.id_pedido) AS total_pedidos,

    SUM(f.quantidade) AS unidades_vendidas,

    ROUND(SUM(f.valor_bruto), 2) AS faturamento_bruto,

    ROUND(SUM(f.valor_desconto), 2) AS total_descontos,

    ROUND(SUM(f.valor_liquido), 2) AS faturamento_liquido,

    ROUND(SUM(f.custo_total), 2) AS custo_total,

    ROUND(SUM(f.margem), 2) AS margem_total,

    ROUND(
        SAFE_DIVIDE(
            SUM(f.valor_liquido),
            COUNT(DISTINCT f.id_pedido)
        ), 2
    ) AS ticket_medio,

    ROUND(
        SAFE_DIVIDE(
            SUM(f.valor_liquido),
            SUM(SUM(f.valor_liquido)) OVER ()
        ) * 100, 2
    ) AS participacao_faturamento_pct

FROM `vendas_estoque.fato_vendas` f

INNER JOIN `vendas_estoque.dim_vendedor` v
    ON f.sk_vendedor = v.sk_vendedor

GROUP BY
    v.sk_vendedor,
    v.id_vendedor,
    v.nome_vendedor;


# ---------------------------------- #


CREATE OR REPLACE VIEW
    `vendas_estoque.vw_estoque_atual` AS

WITH estoque_classificado AS (

    SELECT
        e.sk_produto,
        e.sk_data,
        e.quantidade_entrada,
        e.quantidade_saida,
        e.quantidade_ajuste,
        e.saldo_estoque,

        ROW_NUMBER() OVER (
            PARTITION BY e.sk_produto
            ORDER BY e.sk_data DESC
        ) AS ordem

    FROM `vendas_estoque.fato_estoque_diario` e

)

SELECT
    p.sk_produto,
    p.id_produto,
    p.descricao,
    p.categoria,
    p.marca,

    e.sk_data AS ultima_data_estoque,

    e.quantidade_entrada,
    e.quantidade_saida,
    e.quantidade_ajuste,

    e.saldo_estoque

FROM estoque_classificado e

INNER JOIN `vendas_estoque.dim_produto` p
    ON e.sk_produto = p.sk_produto

WHERE e.ordem = 1;


# ---------------------------------- #


CREATE OR REPLACE VIEW
    `vendas_estoque.vw_movimentacao_estoque_produto` AS

SELECT
    p.sk_produto,
    p.id_produto,
    p.descricao,
    p.categoria,
    p.marca,

    SUM(e.quantidade_entrada) AS total_entradas,

    SUM(e.quantidade_saida) AS total_saidas,

    SUM(e.quantidade_ajuste) AS total_ajustes,

    COUNTIF(
        e.quantidade_entrada != 0
        OR e.quantidade_saida != 0
        OR e.quantidade_ajuste != 0
    ) AS dias_com_movimentacao,

    COUNT(*) AS dias_analisados,

    MAX(e.saldo_estoque) AS maior_saldo_historico,

    ARRAY_AGG(
        e.saldo_estoque
        ORDER BY e.sk_data DESC
        LIMIT 1
    )[OFFSET(0)] AS saldo_atual

FROM `vendas_estoque.fato_estoque_diario` e

INNER JOIN `vendas_estoque.dim_produto` p
    ON e.sk_produto = p.sk_produto

GROUP BY
    p.sk_produto,
    p.id_produto,
    p.descricao,
    p.categoria,
    p.marca;


# ---------------------------------- #


CREATE OR REPLACE VIEW
    `vendas_estoque.vw_cobertura_estoque_produto` AS

WITH parametros AS (
    SELECT 90 AS dias_janela
),

referencia AS (
    SELECT
        MAX(
            PARSE_DATE(
                '%Y%m%d',
                CAST(sk_data AS STRING)
            )
        ) AS data_referencia
    FROM `vendas_estoque.fato_estoque_diario`
),

saidas_periodo AS (
    SELECT
        e.sk_produto,

        SUM(e.quantidade_saida) AS total_saidas_90d,

        COUNTIF(
            e.quantidade_saida > 0
        ) AS dias_com_saida_90d

    FROM `vendas_estoque.fato_estoque_diario` e

    CROSS JOIN referencia r

    WHERE PARSE_DATE(
        '%Y%m%d',
        CAST(e.sk_data AS STRING)
    ) BETWEEN DATE_SUB(
        r.data_referencia,
        INTERVAL 89 DAY
    ) AND r.data_referencia

    GROUP BY
        e.sk_produto
),

base AS (
    SELECT
        p.sk_produto,
        p.id_produto,
        p.descricao,
        p.categoria,
        p.marca,

        e.saldo_estoque AS saldo_atual,

        COALESCE(
            s.total_saidas_90d, 0
        ) AS total_saidas_90d,

        COALESCE(
            s.dias_com_saida_90d, 0
        ) AS dias_com_saida_90d,

        param.dias_janela

    FROM `vendas_estoque.dim_produto` p

    INNER JOIN `vendas_estoque.vw_estoque_atual` e
        ON p.sk_produto = e.sk_produto

    LEFT JOIN saidas_periodo s
        ON p.sk_produto = s.sk_produto

    CROSS JOIN parametros param
)

SELECT
    sk_produto,
    id_produto,
    descricao,
    categoria,
    marca,

    saldo_atual,

    total_saidas_90d,

    dias_com_saida_90d,

    ROUND(
        SAFE_DIVIDE(
            total_saidas_90d,
            dias_janela
        ), 2
    ) AS media_saida_diaria_90d,

    SAFE_DIVIDE(
        saldo_atual,
        SAFE_DIVIDE(
            total_saidas_90d,
            dias_janela
        )
    ) AS cobertura_dias,

    CASE
        WHEN saldo_atual <= 0
            THEN 'Sem estoque'

        WHEN total_saidas_90d = 0
            THEN 'Sem saidas nos ultimos 90 dias'

        ELSE 'Com consumo recente'
    END AS situacao_estoque

FROM base;


# ---------------------------------- #


CREATE OR REPLACE VIEW
    `vendas_estoque.vw_classificacao_estoque` AS

WITH parametros AS (
    SELECT
        7 AS prazo_reposicao_dias
)

SELECT
    e.sk_produto,
    e.id_produto,
    e.descricao,
    e.categoria,
    e.marca,

    e.saldo_atual,
    e.total_saidas_90d,
    e.media_saida_diaria_90d,
    e.cobertura_dias,

    p.prazo_reposicao_dias,

    CASE
        WHEN e.saldo_atual <= 0
            THEN 'Sem estoque'

        WHEN e.total_saidas_90d = 0
            THEN 'Sem consumo recente'

        WHEN e.cobertura_dias <= p.prazo_reposicao_dias
            THEN 'Estoque critico'

        WHEN e.cobertura_dias <= p.prazo_reposicao_dias * 2
            THEN 'Estoque de atencao'

        ELSE 'Estoque adequado'
    END AS classificacao_estoque

FROM `vendas_estoque.vw_cobertura_estoque_produto` e

CROSS JOIN parametros p;
