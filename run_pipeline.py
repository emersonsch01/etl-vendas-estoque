from pathlib import Path
import logging
import subprocess
import sys
import time
from datetime import datetime
import os


# ==========================================================
# CONFIGURAÇÕES
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent

SRC_DIR = BASE_DIR / "src"
LOG_DIR = BASE_DIR / "logs"

LOG_DIR.mkdir(
    parents=True,
    exist_ok=True
)

ARQUIVO_LOG = LOG_DIR / (
    f"pipeline_{datetime.now():%Y%m%d_%H%M%S}.log"
)


# ==========================================================
# CONFIGURAÇÃO DOS LOGS
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(
            ARQUIVO_LOG,
            encoding="utf-8"
        ),
        logging.StreamHandler(sys.stdout)
    ]
)


# ==========================================================
# EXECUÇÃO DE CADA ETAPA
# ==========================================================

def executar_etapa(nome_etapa, arquivo):

    caminho_script = SRC_DIR / arquivo

    logging.info("=" * 60)
    logging.info("INICIANDO ETAPA: %s", nome_etapa)
    logging.info("=" * 60)

    if not caminho_script.exists():
        raise FileNotFoundError(
            f"Script não encontrado: {caminho_script}"
        )

    inicio = time.perf_counter()

    ambiente = os.environ.copy()

    resultado = subprocess.run(
        [sys.executable, str(caminho_script)],
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=ambiente
    )

    # Registra a saída do script
    if resultado.stdout:
        for linha in resultado.stdout.splitlines():
            logging.info("[PROCESSO] %s", linha)

    if resultado.stderr:
        for linha in resultado.stderr.splitlines():
            logging.info("[PROCESSO] %s", linha)

    duracao = time.perf_counter() - inicio

    if resultado.returncode != 0:

        logging.error(
            "ETAPA FALHOU: %s",
            nome_etapa
        )

        raise RuntimeError(
            f"Erro na etapa: {nome_etapa}. "
            f"Consulte o log: {ARQUIVO_LOG}"
        )

    logging.info(
        "ETAPA CONCLUÍDA: %s | Tempo: %.2f segundos",
        nome_etapa,
        duracao
    )


# ==========================================================
# PIPELINE PRINCIPAL
# ==========================================================

def main():

    project_id = os.getenv("GCP_PROJECT_ID")

    if not project_id:
        raise ValueError(
            "A variável GCP_PROJECT_ID não está configurada."
        )

    logging.info(
        "Projeto Google Cloud configurado: %s",
        project_id
    )

    inicio_total = time.perf_counter()

    logging.info("=" * 60)
    logging.info("INICIANDO PIPELINE ETL VENDAS E ESTOQUE")
    logging.info("=" * 60)

    etapas = [
        ("Geração dos dados", "generate_data.py"),
        ("Extração e transformação", "transform.py"),
        ("Modelagem dimensional", "model.py"),
        ("Carga no BigQuery", "load.py")
    ]

    try:

        for nome_etapa, arquivo in etapas:

            executar_etapa(
                nome_etapa,
                arquivo
            )

        duracao_total = time.perf_counter() - inicio_total

        logging.info("=" * 60)
        logging.info("PIPELINE FINALIZADO COM SUCESSO")
        logging.info(
            "TEMPO TOTAL: %.2f segundos",
            duracao_total
        )
        logging.info("LOG SALVO EM: %s", ARQUIVO_LOG)
        logging.info("=" * 60)

    except Exception:

        logging.exception(
            "PIPELINE INTERROMPIDO POR ERRO"
        )

        raise


if __name__ == "__main__":
    main()
