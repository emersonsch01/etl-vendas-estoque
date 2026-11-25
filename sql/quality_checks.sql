
-- =====================================================
-- ETAPA 6: TESTES DE QUALIDADE NO BIGQUERY
-- =====================================================

-- Substitua SEU_ID_DO_PROJETO pelo ID do projeto.


-- 1. CHAVES PRIMARIAS DUPLICADAS NAS DIMENSOES

SELECT
    'dim_cliente' AS tabela,
    COUNT(*) AS registros_duplicados
FROM (
    SELECT sk_cliente
    FROM `vendas_estoque.dim_cliente`
    GROUP BY sk_cliente
    HAVING COUNT(*) > 1
)

UNION ALL

SELECT
    'dim_produto',
    COUNT(*)
FROM (
    SELECT sk_produto
    FROM `vendas_estoque.dim_produto`
    GROUP BY sk_produto
    HAVING COUNT(*) > 1
)

UNION ALL

SELECT
    'dim_vendedor',
    COUNT(*)
FROM (
    SELECT sk_vendedor
    FROM `vendas_estoque.dim_vendedor`
    GROUP BY sk_vendedor
    HAVING COUNT(*) > 1
)

UNION ALL

SELECT
    'dim_data',
    COUNT(*)
FROM (
    SELECT sk_data
    FROM `vendas_estoque.dim_data`
    GROUP BY sk_data
    HAVING COUNT(*) > 1
);


-- 2. CAMPOS OBRIGATORIOS NULOS NA FATO DE VENDAS

SELECT
    COUNTIF(id_pedido IS NULL) AS pedidos_nulos,
    COUNTIF(sk_cliente IS NULL) AS clientes_nulos,
    COUNTIF(sk_produto IS NULL) AS produtos_nulos,
    COUNTIF(sk_data IS NULL) AS datas_nulas,
    COUNTIF(sk_vendedor IS NULL) AS vendedores_nulos,
    COUNTIF(quantidade IS NULL) AS quantidades_nulas
FROM
    `vendas_estoque.fato_vendas`;


-- 3. INTEGRIDADE REFERENCIAL DA FATO DE VENDAS

SELECT
    'cliente' AS relacionamento,
    COUNT(*) AS registros_sem_correspondencia
FROM
    `vendas_estoque.fato_vendas` f
LEFT JOIN
    `vendas_estoque.dim_cliente` d
    ON f.sk_cliente = d.sk_cliente
WHERE
    d.sk_cliente IS NULL

UNION ALL

SELECT
    'produto',
    COUNT(*)
FROM
    `vendas_estoque.fato_vendas` f
LEFT JOIN
    `vendas_estoque.dim_produto` d
    ON f.sk_produto = d.sk_produto
WHERE
    d.sk_produto IS NULL

UNION ALL

SELECT
    'vendedor',
    COUNT(*)
FROM
    `vendas_estoque.fato_vendas` f
LEFT JOIN
    `vendas_estoque.dim_vendedor` d
    ON f.sk_vendedor = d.sk_vendedor
WHERE
    d.sk_vendedor IS NULL

UNION ALL

SELECT
    'data',
    COUNT(*)
FROM
    `vendas_estoque.fato_vendas` f
LEFT JOIN
    `vendas_estoque.dim_data` d
    ON f.sk_data = d.sk_data
WHERE
    d.sk_data IS NULL;


-- 4. QUANTIDADES INVALIDAS NAS VENDAS

SELECT
    COUNTIF(quantidade <= 0) AS quantidades_invalidas
FROM
    `vendas_estoque.fato_vendas`;


-- 5. VALIDACAO DOS VALORES FINANCEIROS

SELECT
    COUNTIF(valor_bruto < 0) AS valores_brutos_negativos,

    COUNTIF(valor_liquido < 0) AS valores_liquidos_negativos,

    COUNTIF(custo_total < 0) AS custos_negativos,

    COUNTIF(
        ABS(valor_desconto - (valor_bruto - valor_liquido)) > 0.02
    ) AS descontos_inconsistentes,

    COUNTIF(
        ABS(margem - (valor_liquido - custo_total)) > 0.02
    ) AS margens_inconsistentes

FROM
    `vendas_estoque.fato_vendas`;


-- 6. DUPLICIDADE NA GRANULARIDADE DO ESTOQUE

SELECT
    COUNT(*) AS combinacoes_duplicadas
FROM (
    SELECT
        sk_produto,
        sk_data
    FROM
        `vendas_estoque.fato_estoque_diario`
    GROUP BY
        sk_produto,
        sk_data
    HAVING COUNT(*) > 1
);


-- 7. INTEGRIDADE REFERENCIAL DO ESTOQUE

SELECT
    COUNT(*) AS produtos_sem_correspondencia
FROM
    `vendas_estoque.fato_estoque_diario` f
LEFT JOIN
    `vendas_estoque.dim_produto` d
    ON f.sk_produto = d.sk_produto
WHERE
    d.sk_produto IS NULL;


-- 8. SALDOS NEGATIVOS DE ESTOQUE

SELECT
    COUNTIF(saldo_estoque < 0) AS saldos_negativos,
    MIN(saldo_estoque) AS menor_saldo
FROM
    `vendas_estoque.fato_estoque_diario`;
