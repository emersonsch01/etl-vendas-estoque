# Projeto ETL — Vendas e Estoque

## Sobre o projeto

Projeto de Engenharia de Dados desenvolvido para simular um ambiente analítico de vendas e controle de estoque, contemplando desde a geração e extração dos dados até sua transformação, modelagem dimensional e disponibilização para consultas analíticas no Google BigQuery.

A solução foi desenvolvida utilizando Python, pandas, arquivos CSV e Parquet, além do Google BigQuery como Data Warehouse.

O projeto implementa um pipeline ETL automatizado, organizado em três camadas de processamento: Bronze, Silver e Gold, seguindo uma arquitetura que separa os dados brutos, tratados e modelados para análise.

A base de dados é sintética, gerada para representar operações comerciais envolvendo clientes, produtos, pedidos, vendas e movimentações de estoque.

## Objetivo

Construir um pipeline de Engenharia de Dados capaz de transformar dados operacionais em informações estruturadas e confiáveis para análises de negócio.

Entre os principais objetivos estão:

- Desenvolver um processo automatizado de extração, transformação e carga de dados (ETL).
- Aplicar técnicas de limpeza, padronização e validação de dados.
- Implementar modelagem dimensional utilizando Star Schema.
- Construir fatos de vendas e estoque com granularidades distintas.
- Disponibilizar dados analíticos no Google BigQuery.
- Desenvolver indicadores de desempenho comercial e operacional.
- Implementar verificações de qualidade e integridade dos dados.

## Tecnologias utilizadas

| Tecnologia | Aplicação no projeto |
|---|---|
| Python | Desenvolvimento e execução do pipeline ETL. |
| Pandas | Manipulação, limpeza e transformação dos dados. |
| NumPy | Operações numéricas e apoio ao processamento. |
| Faker | Geração de dados sintéticos para simulação do ambiente comercial. |
| Parquet | Armazenamento dos dados processados nas camadas Silver e Gold. |
| Google BigQuery | Data Warehouse para armazenamento e consultas analíticas. |
| SQL | Criação de tabelas, Views, indicadores e validações. |
| Google Cloud SDK | Autenticação e acesso ao ambiente Google Cloud. |

## Arquitetura do pipeline

O projeto utiliza uma arquitetura de processamento dividida em três camadas: Bronze, Silver e Gold.

Essa organização permite separar os dados conforme seu estágio de processamento, facilitando a manutenção, rastreabilidade e evolução do pipeline.

### Bronze — Dados brutos

Camada responsável por armazenar os dados originalmente extraídos ou gerados pelo processo.

Os dados são disponibilizados em arquivos CSV, preservando sua estrutura inicial para as etapas seguintes.

### Silver — Dados tratados

Camada responsável pela limpeza, padronização e transformação dos dados.

Nessa etapa são realizadas operações como:

- Tratamento de valores ausentes.
- Padronização de tipos de dados.
- Ajustes de formatos e estruturas.
- Validações de consistência.
- Preparação dos dados para a modelagem dimensional.

Os dados tratados são armazenados em formato Parquet.

### Gold — Dados modelados

Camada responsável por disponibilizar os dados estruturados para análise.

Nessa etapa são construídas as dimensões e tabelas fato utilizando modelagem dimensional.

As tabelas Gold são armazenadas em Parquet e posteriormente carregadas no Google BigQuery, onde ficam disponíveis para consultas analíticas.

## Estrutura do projeto

```text
etl-vendas-estoque/
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── rejected/
│   └── gold/
│
├── docs/
│
├── logs/
│
├── sql/
│   ├── create_tables.sql
│   ├── quality_checks.sql
│   └── views_kpis.sql
│
├── src/
│   ├── extract.py
│   ├── generate_data.py
│   ├── load.py
│   ├── model.py
│   ├── quality.py
│   └── transform.py
│
├── requirements.txt
├── run_pipeline.py
├── verificar_dados.py
├── verificar_modelo.py
├── verificar_silver.py
└── README.md
```

### Organização dos diretórios

- `data/raw/`: armazenamento dos dados brutos gerados pelo projeto.
- `data/processed/`: armazenamento dos dados intermediários tratados.
- `data/rejected/`: registros rejeitados durante as validações.
- `data/gold/`: tabelas dimensionais e fatos prontas para carga analítica.
- `docs/`: documentação complementar do projeto.
- `logs/`: registros de execução do pipeline.
- `sql/`: scripts SQL para criação de tabelas, verificações de qualidade e Views analíticas.
- `src/`: scripts Python responsáveis pela geração, transformação, modelagem, qualidade e carga dos dados.

### Scripts principais

| Arquivo | Responsabilidade |
|---|---|
| `generate_data.py` | Geração dos dados sintéticos. |
| `transform.py` | Extração, tratamento e transformação dos dados. |
| `quality.py` | Verificações de qualidade dos dados. |
| `model.py` | Construção das dimensões e tabelas fato. |
| `load.py` | Carregamento dos dados no BigQuery. |
| `run_pipeline.py` | Orquestração da execução do pipeline. |

Os scripts `verificar_dados.py`, `verificar_modelo.py` e `verificar_silver.py` são utilizados como ferramentas auxiliares para inspeção e validação dos dados durante o desenvolvimento.

## Execução do pipeline

O projeto possui um script principal de orquestração (`run_pipeline.py`), responsável por executar as etapas do processo ETL de forma sequencial e automatizada.

### Pré-requisitos

Antes de executar o projeto, é necessário possuir:

- Python instalado.
- Google Cloud SDK instalado.
- Projeto configurado no Google Cloud.
- Dataset `vendas_estoque` disponível no BigQuery.
- Credenciais autenticadas com permissões para carregar dados no BigQuery.

### 1. Clonar o repositório

```bash
git clone https://github.com/emersonsch01/etl-vendas-estoque.git
cd etl-vendas-estoque
```

### 2. Criar um ambiente virtual

No terminal, execute:

```bash
python -m venv .venv
```

Ative o ambiente virtual no Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar a autenticação do Google Cloud

Execute o comando:

```bash
gcloud auth application-default login
```

Esse procedimento realiza a autenticação das credenciais utilizadas pela aplicação Python para acessar os serviços do Google Cloud.

### 5. Configurar o projeto Google Cloud

No PowerShell, defina a variável de ambiente com o identificador do projeto:

```powershell
$env:GCP_PROJECT_ID="SEU_PROJECT_ID"
```

Substitua `SEU_PROJECT_ID` pelo identificador do seu projeto no Google Cloud.

### 6. Executar o pipeline

Com o ambiente configurado, execute:

```bash
python run_pipeline.py
```

O script principal coordena as seguintes etapas:

1. Geração dos dados sintéticos.
2. Extração e transformação dos dados.
3. Construção das dimensões e tabelas fato.
4. Carregamento dos dados no Google BigQuery.

Durante a execução, são registrados logs contendo informações sobre as etapas processadas, duração e eventuais erros.

### Observação

O pipeline utiliza uma estratégia de carga completa (*Full Refresh*), substituindo os dados das tabelas de destino a cada execução. Portanto, não se trata de uma implementação incremental.

## Data Warehouse — Google BigQuery

O Google BigQuery é utilizado como Data Warehouse do projeto, recebendo as tabelas dimensionais e fatos produzidas na camada Gold.

Os dados são organizados no dataset `vendas_estoque`, permitindo consultas SQL e construção de indicadores analíticos.

### Tabelas do Data Warehouse

O modelo dimensional é composto por seis tabelas:

**Dimensões:**

- `dim_cliente`
- `dim_produto`
- `dim_vendedor`
- `dim_data`

**Tabelas fato:**

- `fato_vendas`
- `fato_estoque_diario`

As dimensões armazenam informações descritivas utilizadas para contextualizar as análises, enquanto as tabelas fato concentram os registros quantitativos dos processos de vendas e estoque.

### Views analíticas e indicadores

Foram desenvolvidas nove Views no BigQuery para disponibilizar indicadores comerciais, financeiros e operacionais.

| View | Indicadores e finalidade |
|---|---|
| `vw_faturamento_mensal` | Faturamento bruto e líquido, descontos, custos e margem por mês. |
| `vw_faturamento_cliente` | Desempenho financeiro e volume de compras por cliente. |
| `vw_desempenho_produto` | Vendas, faturamento e margem por produto. |
| `vw_desempenho_categoria` | Desempenho comercial por categoria de produto. |
| `vw_desempenho_vendedor` | Faturamento, margem, ticket médio e participação nas vendas por vendedor. |
| `vw_estoque_atual` | Posição mais recente do estoque de cada produto. |
| `vw_movimentacao_estoque_produto` | Entradas, saídas, ajustes e saldos acumulados por produto. |
| `vw_cobertura_estoque_produto` | Cobertura estimada de estoque com base no consumo dos últimos 90 dias. |
| `vw_classificacao_estoque` | Classificação dos produtos conforme disponibilidade e cobertura de estoque. |

### Regras de negócio dos indicadores de estoque

Para a análise de cobertura, foi utilizada uma janela de 90 dias de movimentações, considerando como referência a última data disponível na tabela fato de estoque.

A classificação dos produtos considera um prazo de reposição simulado de 7 dias:

- **Sem estoque:** saldo atual menor ou igual a zero.
- **Sem consumo recente:** ausência de saídas no período analisado.
- **Estoque crítico:** cobertura igual ou inferior a 7 dias.
- **Estoque de atenção:** cobertura superior a 7 e igual ou inferior a 14 dias.
- **Estoque adequado:** cobertura superior a 14 dias.

Esses parâmetros são premissas utilizadas na simulação e podem ser ajustados conforme as regras operacionais de um ambiente real.

### Consultas analíticas

As Views permitem realizar análises utilizando SQL diretamente no BigQuery, sem a necessidade de reconstruir os cálculos a cada consulta.

Os resultados podem ser utilizados posteriormente em ferramentas de visualização de dados, como Power BI, para construção de dashboards comerciais e operacionais.

## Qualidade dos dados e validações

A qualidade dos dados é verificada ao longo do projeto por meio de rotinas desenvolvidas em Python e consultas SQL no BigQuery.

O objetivo é identificar possíveis inconsistências, garantir a integridade das informações e validar os resultados gerados pelo pipeline.

### Verificações realizadas

Entre as principais validações implementadas estão:

- Verificação da quantidade de registros nas tabelas e Views analíticas.
- Verificação da unicidade das chaves utilizadas no modelo dimensional.
- Identificação de valores nulos em campos essenciais.
- Conferência dos cálculos financeiros de vendas.
- Verificação de saldos negativos na posição de estoque.
- Conciliação entre movimentações de estoque e saldos calculados.
- Validação da consistência entre entradas, saídas, ajustes e saldo final.

### Resultados das validações

Após a execução dos testes, foram obtidos os seguintes resultados:

| Validação | Resultado |
|---|---|
| Quantidade de registros e unicidade das chaves nas 9 Views | 9 de 9 aprovadas |
| Consistência dos cálculos financeiros nas 5 Views avaliadas | 0 divergências |
| Produtos avaliados na posição atual de estoque | 500 |
| Produtos com saldo negativo | 0 |
| Produtos com saldo nulo nos campos avaliados | 0 |
| Produtos conciliados entre movimentações e saldo atual | 500 |
| Divergências na conciliação de estoque | 0 |
| Valores nulos nos campos essenciais das 7 Views verificadas | 0 |

Os testes demonstraram consistência entre os valores financeiros calculados e os saldos de estoque produzidos pelo pipeline.

As verificações foram realizadas tanto nas etapas de processamento em Python quanto diretamente no BigQuery, permitindo avaliar a integridade dos dados em diferentes momentos do fluxo ETL.

Arquivos relacionados

src/quality.py: módulo de verificações de qualidade durante o processamento.
sql/quality_checks.sql: consultas SQL utilizadas nas verificações do Data Warehouse.
verificar_dados.py: script de inspeção dos dados.
verificar_modelo.py: script de verificação do modelo dimensional
verificar_silver.py: script de inspeção dos dados tratados na camada Silver.

## Limitações, premissas e decisões técnicas

Para simular um ambiente de dados comerciais, algumas premissas foram adotadas durante o desenvolvimento.

### Premissas do projeto

- **Dados sintéticos:** os registros de clientes, produtos, vendedores, vendas e movimentações de estoque foram gerados artificialmente para fins de estudo.
- **Vendedores fictícios:** os vendedores são identificados por nomes genéricos, como `Vendedor 01` e `Vendedor 02`.
- **Reposição de estoque:** a simulação considera regras artificiais para geração das movimentações, não representando necessariamente o comportamento de uma operação comercial real.
- **Cobertura de estoque:** o cálculo utiliza os últimos 90 dias disponíveis na base, considerando como referência a data mais recente registrada.
- **Prazo de reposição:** foi adotado um prazo simulado de 7 dias para classificação da disponibilidade de estoque.

### Decisões técnicas

- **Arquitetura Bronze, Silver e Gold:** separação dos dados conforme suas etapas de processamento.
- **Formato Parquet:** utilizado nas camadas tratadas e modeladas para armazenamento estruturado e eficiente.
- **Star Schema:** adotado para organizar os dados analíticos em dimensões e tabelas fato.
- **Carga completa:** o pipeline utiliza atualização integral das tabelas no BigQuery (`WRITE_TRUNCATE`), substituindo os dados existentes a cada execução.
- **Granularidades independentes:** vendas são registradas por item de pedido, enquanto o estoque é consolidado por produto e dia.

### Limitações atuais

O projeto foi desenvolvido como uma solução de estudo e demonstração técnica. Portanto, algumas funcionalidades comuns em ambientes corporativos ainda não foram implementadas, como cargas incrementais, controle de histórico de alterações dimensionais (SCD), orquestração externa e monitoramento automatizado em ambiente de produção.

## Próximas melhorias

O projeto foi estruturado para permitir evoluções futuras, aproximando sua arquitetura de um ambiente de Engenharia de Dados utilizado em empresas.

Entre as melhorias planejadas estão:

- **Carga incremental:** implementar processos que identifiquem e processem apenas registros novos ou alterados, evitando a substituição integral das tabelas.
- **Orquestração:** integrar uma ferramenta como Apache Airflow para agendamento, dependências e monitoramento das etapas do pipeline.
- **Testes automatizados:** ampliar a cobertura de testes utilizando ferramentas como Pytest e validações específicas para dados.
- **Histórico dimensional:** implementar Slowly Changing Dimensions (SCD), permitindo preservar alterações históricas em determinadas dimensões.
- **Monitoramento:** desenvolver mecanismos de acompanhamento de execução, falhas, duração e qualidade dos dados.
- **Visualização de dados:** conectar o BigQuery ao Power BI para desenvolver dashboards comerciais e operacionais.
- **Infraestrutura como código:** avaliar a utilização de ferramentas como Terraform para automatizar a configuração dos recursos em nuvem.