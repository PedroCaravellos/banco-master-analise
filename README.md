# 🏦 Banco Master — Análise Financeira (2020–2024)

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red?logo=streamlit)](https://streamlit.io)
[![Licença](https://img.shields.io/badge/Licença-MIT-green)](LICENSE)
[![Dados](https://img.shields.io/badge/Fonte-BCB%2FIF.data-orange)](https://www3.bcb.gov.br/ifdata/)

Dashboard interativo de análise financeira do **Banco Master S/A** construído com Streamlit, cobrindo o período de 2020 a 2024.

---

## 🎯 Tema de Análise

> **Pergunta central:** Como o crescimento acelerado do Banco Master entre 2020 e 2024 impactou seus indicadores de solvência, alavancagem e concentração de risco de captação?

### Justificativa

O Banco Master foi uma das instituições financeiras privadas que mais cresceu no Brasil entre 2020 e 2024, expandindo seus ativos de R$ 8,2 bilhões para R$ 63 bilhões (+668%). Esse crescimento se deu via:

- Captação agressiva de CDB com taxas de até **140% do CDI**
- Expansão acelerada da carteira de crédito para **segmentos sem acesso ao crédito tradicional**
- Aquisições estratégicas (Willbank, Voiter)

O caso é academicamente relevante por ilustrar a tensão entre **crescimento e solidez prudencial** — tema central da regulação bancária pós-Basel III.

---

## 📊 Funcionalidades do Dashboard

| Seção | Conteúdo |
|-------|----------|
| 📊 Visão Geral | KPIs principais, evolução do balanço |
| 📈 Crescimento | Taxas de crescimento, índice de crescimento acumulado, razão crédito/depósito |
| ⚖️ Risco & Solvência | Índice de Basileia, alavancagem, concentração de captação |
| 💰 Lucratividade | Lucro líquido, ROE, margem líquida, decomposição de receitas |
| 🔮 Predição | Regressão linear com configuração interativa de cenários e horizonte |

---

## 🗂️ Estrutura do Projeto

```
banco_master/
├── app.py                          # Dashboard Streamlit principal
├── requirements.txt                # Dependências Python
├── README.md                       # Este arquivo
├── data/
│   ├── banco_master_financeiro.csv     # Dataset bruto (10 períodos semestrais)
│   └── banco_master_processado.csv     # Dataset com indicadores calculados
├── src/
│   └── coleta_dados.py             # Script de coleta e processamento
├── docs/
│   └── metodologia.md              # Documentação detalhada das fontes e decisões
└── .github/
    └── workflows/
        └── ci.yml                  # GitHub Actions (lint + testes básicos)
```

---

## 🚀 Como Rodar

### Pré-requisitos
- Python 3.10+
- pip

### Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/banco-master-analise.git
cd banco-master-analise

# 2. Crie e ative um ambiente virtual (recomendado)
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
# .venv\Scripts\activate         # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. (Opcional) Execute a coleta/processamento de dados
python src/coleta_dados.py

# 5. Rode o dashboard
streamlit run app.py
```

O dashboard abrirá automaticamente em `http://localhost:8501`.

---

## 📡 Fontes de Dados

| Fonte | URL | Tipo | Período |
|-------|-----|------|---------|
| BCB / IF.data | [olinda.bcb.gov.br](https://olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1) | API OData (pública) | 2020–2024 |
| Portal Dados Abertos BCB | [dadosabertos.bcb.gov.br](https://dadosabertos.bcb.gov.br/dataset/ir-33923798000100) | JSON/CSV | 2020–2024 |
| Balanço 2021 | Monitor Mercantil / publicação oficial | PDF | dez/2021 |
| Demonstrações Financeiras S1/2024 | bancomasterbi.com.br | PDF | jun/2024 |
| Balanço consolidado dez/2024 | poder360.com.br (publicação oficial) | PDF | dez/2024 |

> **CNPJ Banco Master S/A:** 33.923.798/0001-00  
> **Código IF.data:** 33923798

### Como a API IF.data funciona

```python
import requests

url = "https://olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1/odata/IfDataValores"
params = {
    "$filter": "CodigoInstituicao eq '33923798' and AnoPeriodo eq 2024 and Trimestre eq 4",
    "$format": "json",
}
resp = requests.get(url, params=params, timeout=20)
dados = resp.json()["value"]
```

---

## 📦 Dependências

```
streamlit>=1.32.0
pandas>=2.0.0
plotly>=5.18.0
scikit-learn>=1.4.0
requests>=2.31.0
openpyxl>=3.1.0
```

---

## 🔮 Metodologia de Predição

O modelo de predição utiliza **Regressão Linear Simples** com as seguintes características:

- **Variável dependente (y):** Ativo Total (R$ bilhões)
- **Variável independente (X):** Índice temporal (0, 1, 2, … n semestres)
- **Intervalo de confiança:** 95% baseado no desvio padrão dos resíduos
- **Cenários:** Tendência histórica · Conservador (-30%) · Otimista (+20%)

**Limitações assumidas:**
- Modelo linear pode não capturar mudanças estruturais (ex.: aquisição pelo BRB em 2025)
- Base histórica de apenas 10 observações limita a robustez estatística
- Não inclui variáveis macroeconômicas (Selic, inadimplência)

---

## 👥 Autores

Trabalho de Grupo — Análise de Dados em Economia/Finanças  
Graduação · 2025

---

## 📄 Licença

MIT License — veja [LICENSE](LICENSE) para detalhes.
