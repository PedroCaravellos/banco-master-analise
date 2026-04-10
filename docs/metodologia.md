# Metodologia — Fontes, Decisões e Limitações

## 1. Tema escolhido

**Crescimento acelerado e riscos de solvência do Banco Master (2020–2024)**

O Banco Master foi selecionado por ser um caso concreto e atual de tensão entre crescimento e solidez prudencial. Os dados estão disponíveis publicamente via demonstrações financeiras e sistema IF.data do BCB.

---

## 2. Pergunta de análise

> "Como o crescimento acelerado do Banco Master entre 2020 e 2024 impactou seus indicadores de solvência, alavancagem e concentração de risco de captação?"

**Por que esta pergunta?**
- É mensurável (indicadores de Basileia, alavancagem, razão crédito/depósito)
- Tem relevância regulatória e acadêmica
- Permite predição de uma variável (ativo total) baseada na tendência histórica

---

## 3. Fontes de dados

### 3.1 API IF.data — Banco Central do Brasil
- **URL base:** `https://olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1/odata/`
- **Endpoint:** `IfDataValores`
- **Filtros usados:** `CodigoInstituicao eq '33923798'`
- **Disponibilidade:** Dados trimestrais com defasagem de ~1 trimestre
- **Formato:** OData/JSON

### 3.2 Portal de Dados Abertos do BCB
- **URL:** `https://dadosabertos.bcb.gov.br/dataset/ir-33923798000100`
- **Conteúdo:** Conjunto de dados abertos da instituição no SFN

### 3.3 Demonstrações Financeiras publicadas
| Documento | Período | URL |
|-----------|---------|-----|
| Balanço 2021 | dez/2021 | publicidadelegal.monitormercantil.com.br |
| DF Banco Master de Investimento | jun/2024 | bancomasterbi.com.br |
| Balanço consolidado | dez/2024 | static.poder360.com.br |

---

## 4. Preparação dos dados

### 4.1 Decisões de limpeza
- **Periodicidade:** Dados semestrais (S1 = junho, S2 = dezembro)
- **Unidade:** Valores em R$ bilhões para grandes indicadores, R$ milhões para lucro líquido
- **Valores ausentes:** Não há — todas as 10 observações têm valores completos
- **Dados estimados:** Valores de 2020-S1 a 2022-S2 foram estimados com base na evolução apresentada nas demonstrações financeiras anuais, interpolando crescimento linear entre os valores publicados

### 4.2 Indicadores calculados
```
crescimento_ativo_pct    = pct_change(ativo_total_bi) × 100
crescimento_credito_pct  = pct_change(carteira_credito_bi) × 100
margem_lucro_pct         = (lucro_liquido_mi / 1000) / receita_intermediacao_bi × 100
alavancagem              = ativo_total_bi / patrimonio_liquido_bi
razao_credito_deposito   = carteira_credito_bi / depositos_totais_bi
```

---

## 5. Ponto de predição

**Variável-alvo:** Ativo Total (R$ bilhões)

**Justificativa:** O ativo total é o indicador síntese do tamanho e crescimento da instituição. Sua projeção permite estimar a trajetória de expansão e avaliar a sustentabilidade do modelo.

**Modelo:** Regressão Linear Simples
- R² ≈ 0.97 (alta aderência à tendência linear)
- Coeficiente: ~5,5 R$ bi por semestre
- Limitações: não captura não-linearidades, mudanças estruturais (BRB) ou variáveis macro

---

## 6. Limitações e vieses

1. **Dados parcialmente estimados** para períodos anteriores a 2023 (interpolação linear)
2. **Sem dados de inadimplência** — IF.data não estava acessível durante coleta
3. **Modelo de predição simplificado** — adequado para graduação, insuficiente para análise regulatória
4. **Descontinuidade esperada em 2025** — a aquisição pelo BRB tornará os dados históricos menos preditivos

---

## 7. Referências

- BCB. *Sistema IF.data — Notas Metodológicas.* 2024.
- Banco Master S/A. *Demonstrações Financeiras 2021.* Monitor Mercantil, 2022.
- Banco Master S/A. *Balanço Consolidado Dezembro 2024.* Poder360, 2025.
- SUNO Research. *Banco Master divulga balanço com lucro de R$ 1 bilhão em 2024.* Abr/2025.
- BLB Escola de Negócios. *Aquisição do Banco Master pelo BRB: análise estratégica.* 2025.
