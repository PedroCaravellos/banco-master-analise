"""
coleta_dados.py
===============
Coleta e consolida dados financeiros públicos do Banco Master S/A.

Fontes utilizadas:
  1. Banco Central do Brasil - Sistema IF.data (API OData)
     URL: https://olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1/odata/
     CNPJ Banco Master S/A: 33.923.798/0001-00

  2. Portal de Dados Abertos do BCB
     URL: https://dadosabertos.bcb.gov.br/dataset/ir-33923798000100

  3. Demonstrações Financeiras publicadas pelo Banco Master
     - Balanço 2021: publicidadelegal.monitormercantil.com.br
     - Balanço S1/2024: bancomasterbi.com.br
     - Balanço consolidado dez/2024: static.poder360.com.br

NOTA: O Banco Central disponibiliza dados via IF.data com defasagem de 1 trimestre.
      Os dados consolidados anuais vêm das demonstrações financeiras publicadas.

Autores: Trabalho de Grupo - Análise Financeira Banco Master
Data: Abril 2025
"""

import requests
import pandas as pd
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# CNPJ do Banco Master S/A (8 dígitos para API IF.data)
CODIGO_MASTER = "33923798"

# Base URL da API IF.data do Banco Central
IFDATA_BASE = "https://olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1/odata"


def buscar_ifdata_trimestre(codigo: str, ano: int, trimestre: int) -> dict:
    """
    Busca indicadores financeiros de uma instituição no IF.data do BCB.

    Args:
        codigo: Código CNPJ (8 primeiros dígitos) da instituição
        ano: Ano de referência (ex: 2024)
        trimestre: Trimestre (1 a 4)

    Returns:
        Dicionário com os campos retornados pela API ou dict vazio em caso de erro.

    Exemplo de uso:
        dados = buscar_ifdata_trimestre("33923798", 2024, 4)
    """
    endpoint = f"{IFDATA_BASE}/IfDataValores"
    params = {
        "$filter": f"CodigoInstituicao eq '{codigo}' and AnoPeriodo eq {ano} and Trimestre eq {trimestre}",
        "$format": "json",
        "$top": 1,
    }
    try:
        resp = requests.get(endpoint, params=params, timeout=20)
        resp.raise_for_status()
        value = resp.json().get("value", [])
        return value[0] if value else {}
    except Exception as e:
        print(f"[AVISO] IF.data indisponível para {ano}/T{trimestre}: {e}")
        return {}


def carregar_dados_locais() -> pd.DataFrame:
    """
    Carrega o dataset consolidado já extraído e validado.

    O arquivo banco_master_financeiro.csv foi construído combinando:
      - Dados da API IF.data (quando acessível)
      - Dados das demonstrações financeiras publicadas
      - Notícias e relatórios de fontes oficiais

    Returns:
        DataFrame com séries históricas do Banco Master.
    """
    caminho = DATA_DIR / "banco_master_financeiro.csv"
    df = pd.read_csv(caminho)
    df["data"] = pd.to_datetime(
        df["periodo"].str.replace("S1", "06").str.replace("S2", "12"),
        format="%Y-%m",
        errors="coerce",
    )
    # Garantir tipos numéricos
    colunas_num = [
        "ativo_total_bi", "carteira_credito_bi", "depositos_totais_bi",
        "patrimonio_liquido_bi", "lucro_liquido_mi", "receita_intermediacao_bi",
        "resultado_tvm_bi", "indice_basileia_pct", "roe_pct",
    ]
    for col in colunas_num:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.sort_values("data").reset_index(drop=True)


def calcular_indicadores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula indicadores derivados para análise financeira.

    Indicadores calculados:
        - crescimento_ativo_pct: variação percentual do ativo total (período a período)
        - crescimento_credito_pct: variação percentual da carteira de crédito
        - margem_lucro_pct: lucro líquido / receita de intermediação financeira
        - alavancagem: ativo total / patrimônio líquido
        - razao_credito_deposito: carteira de crédito / depósitos totais
    """
    df = df.copy()
    df["crescimento_ativo_pct"] = df["ativo_total_bi"].pct_change() * 100
    df["crescimento_credito_pct"] = df["carteira_credito_bi"].pct_change() * 100
    df["margem_lucro_pct"] = (df["lucro_liquido_mi"] / 1000) / df["receita_intermediacao_bi"] * 100
    df["alavancagem"] = df["ativo_total_bi"] / df["patrimonio_liquido_bi"]
    df["razao_credito_deposito"] = df["carteira_credito_bi"] / df["depositos_totais_bi"]
    return df


def exportar_para_analise(df: pd.DataFrame) -> None:
    """Salva versão processada do dataset com todos os indicadores calculados."""
    caminho = DATA_DIR / "banco_master_processado.csv"
    df.to_csv(caminho, index=False)
    print(f"[OK] Dataset processado salvo em: {caminho}")


if __name__ == "__main__":
    print("=" * 60)
    print("  Coleta de Dados - Banco Master S/A")
    print(f"  Executado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 60)

    # 1. Tentativa de coleta via API (pode falhar dependendo do ambiente)
    print("\n[1/3] Tentando acesso à API IF.data do Banco Central...")
    dados_api = buscar_ifdata_trimestre(CODIGO_MASTER, 2024, 4)
    if dados_api:
        print(f"      Dados encontrados: {dados_api}")
    else:
        print("      API indisponível - usando dataset consolidado local.")

    # 2. Carregamento e processamento
    print("\n[2/3] Carregando dataset consolidado...")
    df = carregar_dados_locais()
    df = calcular_indicadores(df)
    print(f"      {len(df)} registros carregados ({df['periodo'].min()} a {df['periodo'].max()})")

    # 3. Exportação
    print("\n[3/3] Exportando dataset processado...")
    exportar_para_analise(df)

    print("\n[CONCLUÍDO] Dados prontos para análise no Streamlit.")
