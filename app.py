"""
app.py — Dashboard Streamlit: Análise Financeira Banco Master S/A (2020–2024)
==============================================================================
Tema de análise:
    Crescimento acelerado e riscos de solvência do Banco Master —
    uma análise da expansão de ativos, alavancagem e concentração de captação
    via CDB no período 2020–2024.

Para rodar localmente:
    pip install streamlit pandas plotly scikit-learn
    streamlit run app.py
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
from pathlib import Path
from sklearn.linear_model import LinearRegression

# ─── Configuração da página ────────────────────────────────────────────────
st.set_page_config(
    page_title="Banco Master — Análise Financeira",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS customizado ────────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        border-left: 4px solid #0066cc;
        margin-bottom: 0.5rem;
    }
    .metric-card h4 { color: #555; font-size: 0.8rem; margin: 0; }
    .metric-card h2 { color: #111; font-size: 1.5rem; margin: 0.2rem 0 0; }
    .alerta { background: #fff3cd; border-left: 4px solid #f0ad4e;
              padding: 0.8rem 1rem; border-radius: 6px; font-size: 0.9rem; }
    .insight { background: #d1ecf1; border-left: 4px solid #17a2b8;
               padding: 0.8rem 1rem; border-radius: 6px; font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)

# ─── Carregamento de dados ──────────────────────────────────────────────────
@st.cache_data
def carregar_dados():
    caminho = Path(__file__).parent / "data" / "banco_master_processado.csv"
    if not caminho.exists():
        caminho = Path(__file__).parent / "data" / "banco_master_financeiro.csv"
    df = pd.read_csv(caminho)
    df["data"] = pd.to_datetime(
        df["periodo"].str.replace("S1", "06").str.replace("S2", "12"),
        format="%Y-%m", errors="coerce"
    )
    num_cols = [
        "ativo_total_bi", "carteira_credito_bi", "depositos_totais_bi",
        "patrimonio_liquido_bi", "lucro_liquido_mi", "receita_intermediacao_bi",
        "resultado_tvm_bi", "indice_basileia_pct", "roe_pct",
    ]
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.sort_values("data").reset_index(drop=True)
    # Indicadores derivados
    df["crescimento_ativo_pct"] = df["ativo_total_bi"].pct_change() * 100
    df["crescimento_credito_pct"] = df["carteira_credito_bi"].pct_change() * 100
    df["margem_lucro_pct"] = (df["lucro_liquido_mi"] / 1000) / df["receita_intermediacao_bi"] * 100
    df["alavancagem"] = df["ativo_total_bi"] / df["patrimonio_liquido_bi"]
    df["razao_credito_deposito"] = df["carteira_credito_bi"] / df["depositos_totais_bi"]
    df["lucro_liquido_bi"] = df["lucro_liquido_mi"] / 1000
    return df

df = carregar_dados()

# ─── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Brasão_de_Armas_do_Brasil.svg/200px-Brasão_de_Armas_do_Brasil.svg.png", width=40)
    st.title("🏦 Banco Master")
    st.caption("Análise Financeira 2020–2024")
    st.divider()

    secoes = st.radio(
        "Navegar para",
        ["📊 Visão Geral", "📈 Crescimento", "⚖️ Risco & Solvência",
         "💰 Lucratividade", "🔮 Predição"],
        label_visibility="collapsed",
    )

    st.divider()
    st.caption("**Fonte dos dados**")
    st.caption("BCB/IF.data · Demonstrações Financeiras publicadas pelo Banco Master · Balanço consolidado dez/2024")
    st.caption("**Período**")
    st.caption("1º Sem/2020 – 2º Sem/2024")

    # Filtro de período
    periodos = df["periodo"].tolist()
    periodo_inicio, periodo_fim = st.select_slider(
        "Filtrar período",
        options=periodos,
        value=(periodos[0], periodos[-1]),
    )
    idx_ini = periodos.index(periodo_inicio)
    idx_fim = periodos.index(periodo_fim)
    df_filtrado = df.iloc[idx_ini:idx_fim + 1].copy()

# ─── Cabeçalho ──────────────────────────────────────────────────────────────
st.title("Análise Financeira — Banco Master S/A")
st.markdown(
    "**Tema:** Expansão acelerada, concentração de captação via CDB e riscos de solvência (2020–2024)"
)
st.divider()

# ════════════════════════════════════════════════════════════════════════════
if "Visão Geral" in secoes:
    st.subheader("📊 Visão Geral — Indicadores Principais")

    ultimo = df_filtrado.iloc[-1]
    penultimo = df_filtrado.iloc[-2] if len(df_filtrado) > 1 else ultimo

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        delta_ativo = ultimo.ativo_total_bi - penultimo.ativo_total_bi
        st.metric("Ativo Total", f"R$ {ultimo.ativo_total_bi:.1f} bi",
                  f"{delta_ativo:+.1f} bi vs período anterior")
    with c2:
        delta_cred = ultimo.carteira_credito_bi - penultimo.carteira_credito_bi
        st.metric("Carteira de Crédito", f"R$ {ultimo.carteira_credito_bi:.1f} bi",
                  f"{delta_cred:+.1f} bi vs período anterior")
    with c3:
        delta_pl = ultimo.patrimonio_liquido_bi - penultimo.patrimonio_liquido_bi
        st.metric("Patrimônio Líquido", f"R$ {ultimo.patrimonio_liquido_bi:.1f} bi",
                  f"{delta_pl:+.1f} bi vs período anterior")
    with c4:
        delta_ll = ultimo.lucro_liquido_mi - penultimo.lucro_liquido_mi
        st.metric("Lucro Líquido", f"R$ {ultimo.lucro_liquido_mi:.0f} mi",
                  f"{delta_ll:+.0f} mi vs período anterior")

    st.markdown("---")
    # Gráfico radar de indicadores normalizados
    col1, col2 = st.columns([2, 1])
    with col1:
        fig = go.Figure()
        cores = px.colors.qualitative.Set2
        for i, row in df_filtrado.iterrows():
            fig.add_trace(go.Scatter(
                x=df_filtrado["periodo"],
                y=df_filtrado["ativo_total_bi"],
                mode="lines+markers",
                name="Ativo Total (R$ bi)",
                line=dict(color="#0066cc", width=2),
                showlegend=True,
            ))
            break
        fig.add_trace(go.Scatter(
            x=df_filtrado["periodo"], y=df_filtrado["carteira_credito_bi"],
            mode="lines+markers", name="Crédito (R$ bi)",
            line=dict(color="#e67e22", width=2),
        ))
        fig.add_trace(go.Scatter(
            x=df_filtrado["periodo"], y=df_filtrado["depositos_totais_bi"],
            mode="lines+markers", name="Depósitos (R$ bi)",
            line=dict(color="#27ae60", width=2),
        ))
        fig.add_trace(go.Scatter(
            x=df_filtrado["periodo"], y=df_filtrado["patrimonio_liquido_bi"],
            mode="lines+markers", name="PL (R$ bi)",
            line=dict(color="#8e44ad", width=2),
        ))
        fig.update_layout(
            title="Evolução dos Principais Indicadores de Balanço",
            xaxis_title="Período", yaxis_title="R$ Bilhões",
            hovermode="x unified", height=380, template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("""
        <div class='insight'>
        <b>📌 Insight</b><br>
        Em 4 anos, o Banco Master multiplicou seus ativos por <b>7,7x</b> — de R$ 8,2 bi 
        para R$ 63 bi. A carteira de crédito cresceu <b>9,8x</b> no mesmo período, 
        superando o crescimento dos depósitos (7,6x) e do patrimônio líquido (5,2x).
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        crescimento_total = (
            (df_filtrado.iloc[-1].ativo_total_bi / df_filtrado.iloc[0].ativo_total_bi) - 1
        ) * 100

        st.metric("Crescimento do Ativo (período)", f"{crescimento_total:.0f}%")
        st.metric("Índice de Basileia (último)", f"{ultimo.indice_basileia_pct:.1f}%")
        st.metric("ROE (último)", f"{ultimo.roe_pct:.1f}%")
        st.metric("Alavancagem (último)", f"{ultimo.alavancagem:.1f}x")

# ════════════════════════════════════════════════════════════════════════════
elif "Crescimento" in secoes:
    st.subheader("📈 Análise de Crescimento")

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Taxa de Crescimento do Ativo (%)",
            "Taxa de Crescimento da Carteira de Crédito (%)",
            "Crescimento Acumulado (base: 2020-S1 = 100)",
            "Razão Crédito / Depósitos",
        ),
    )
    df_plot = df_filtrado.dropna(subset=["crescimento_ativo_pct"])

    fig.add_trace(go.Bar(
        x=df_plot["periodo"], y=df_plot["crescimento_ativo_pct"].round(1),
        name="Δ Ativo", marker_color="#0066cc",
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        x=df_plot["periodo"], y=df_plot["crescimento_credito_pct"].round(1),
        name="Δ Crédito", marker_color="#e67e22",
    ), row=1, col=2)

    # Crescimento acumulado indexado
    base = df_filtrado.iloc[0]
    df_idx = df_filtrado.copy()
    df_idx["idx_ativo"] = df_idx["ativo_total_bi"] / base.ativo_total_bi * 100
    df_idx["idx_credito"] = df_idx["carteira_credito_bi"] / base.carteira_credito_bi * 100
    df_idx["idx_pl"] = df_idx["patrimonio_liquido_bi"] / base.patrimonio_liquido_bi * 100

    for nome, col, cor in [("Ativo", "idx_ativo", "#0066cc"),
                            ("Crédito", "idx_credito", "#e67e22"),
                            ("PL", "idx_pl", "#8e44ad")]:
        fig.add_trace(go.Scatter(
            x=df_idx["periodo"], y=df_idx[col].round(1),
            mode="lines+markers", name=nome, line=dict(color=cor),
        ), row=2, col=1)

    fig.add_trace(go.Scatter(
        x=df_filtrado["periodo"],
        y=df_filtrado["razao_credito_deposito"].round(3),
        mode="lines+markers", name="Crédito/Depósito",
        line=dict(color="#c0392b", width=2),
        fill="tozeroy", fillcolor="rgba(192,57,43,0.1)",
    ), row=2, col=2)

    fig.update_layout(height=600, template="plotly_white", showlegend=False,
                      title_text="Dinâmica de Crescimento — Banco Master")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div class='alerta'>
    ⚠️ <b>Atenção:</b> A taxa de crescimento semestral do ativo chegou a <b>37%</b> 
    no 1º semestre de 2024. Crescimentos dessa magnitude em instituições financeiras 
    exigem escrutínio cuidadoso da qualidade dos ativos gerados.
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
elif "Risco" in secoes:
    st.subheader("⚖️ Risco & Solvência")

    col1, col2 = st.columns(2)

    with col1:
        # Índice de Basileia
        fig = go.Figure()
        fig.add_hline(y=11, line_dash="dash", line_color="red",
                      annotation_text="Mínimo regulatório (11%)")
        fig.add_trace(go.Scatter(
            x=df_filtrado["periodo"], y=df_filtrado["indice_basileia_pct"],
            mode="lines+markers+text",
            text=df_filtrado["indice_basileia_pct"].round(1).astype(str) + "%",
            textposition="top center",
            line=dict(color="#0066cc", width=3),
            fill="tozeroy", fillcolor="rgba(0,102,204,0.1)",
        ))
        fig.update_layout(
            title="Índice de Basileia (%)",
            yaxis=dict(range=[9, 17]),
            template="plotly_white", height=300,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Alavancagem
        fig2 = go.Figure(go.Bar(
            x=df_filtrado["periodo"],
            y=df_filtrado["alavancagem"].round(1),
            marker=dict(
                color=df_filtrado["alavancagem"],
                colorscale="RdYlGn_r",
                showscale=True,
                colorbar=dict(title="Alavancagem"),
            ),
            text=df_filtrado["alavancagem"].round(1),
            textposition="outside",
        ))
        fig2.update_layout(
            title="Alavancagem (Ativo / Patrimônio Líquido)",
            template="plotly_white", height=300,
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("#### Análise de Concentração de Captação")
    st.markdown("""
    O Banco Master captou recursos majoritariamente via **CDB** com taxas entre 
    **120% e 140% do CDI** — significativamente acima da média do mercado (~100% CDI).
    Essa estratégia gerou crescimento rápido, mas concentrou o risco de liquidez.
    """)

    # Composição do passivo estimada
    fig3 = go.Figure(go.Pie(
        labels=["CDB/CDI (Master)", "Depósitos Interfinanceiros", "Dívidas Subordinadas", "Outros"],
        values=[72, 15, 8, 5],
        hole=0.4,
        marker_colors=["#c0392b", "#e67e22", "#f39c12", "#bdc3c7"],
    ))
    fig3.update_layout(
        title="Composição estimada do Passivo — dez/2024",
        template="plotly_white", height=320,
    )
    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.plotly_chart(fig3, use_container_width=True)
    with col_b:
        st.markdown("""
        <div class='alerta' style='margin-top:2rem'>
        ⚠️ <b>Risco identificado:</b> Em dez/2024, o Banco Master tinha 
        <b>R$ 7,6 bilhões</b> em CDBs/CDIs com vencimento concentrado até 
        <b>junho/2025</b>. Esse descasamento de prazo motivou o processo 
        de aquisição pelo BRB anunciado em março/2025.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class='insight' style='margin-top:1rem'>
        📌 <b>Contexto:</b> O acordo de venda de <b>58%</b> do capital ao BRB 
        por R$ 2 bilhões foi anunciado em 28/03/2025, sinalizando necessidade 
        de reforço de capital prudencial.
        </div>
        """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
elif "Lucratividade" in secoes:
    st.subheader("💰 Lucratividade")

    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_filtrado["periodo"], y=df_filtrado["lucro_liquido_mi"],
            name="Lucro Líquido (R$ mi)", marker_color="#27ae60",
            text=df_filtrado["lucro_liquido_mi"].round(0).astype(int),
            textposition="outside",
        ))
        fig.update_layout(title="Lucro Líquido (R$ milhões)",
                          template="plotly_white", height=320)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = make_subplots(specs=[[{"secondary_y": True}]])
        fig2.add_trace(go.Scatter(
            x=df_filtrado["periodo"], y=df_filtrado["roe_pct"],
            mode="lines+markers", name="ROE (%)", line=dict(color="#8e44ad", width=2),
        ), secondary_y=False)
        fig2.add_trace(go.Scatter(
            x=df_filtrado["periodo"],
            y=df_filtrado["margem_lucro_pct"].round(1),
            mode="lines+markers", name="Margem Líquida (%)",
            line=dict(color="#e74c3c", width=2, dash="dot"),
        ), secondary_y=True)
        fig2.update_layout(title="ROE e Margem Líquida (%)",
                           template="plotly_white", height=320,
                           legend=dict(orientation="h"))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("#### Decomposição da Receita — 2024")
    receitas = pd.DataFrame({
        "Componente": ["Receita de Crédito", "TVM", "Cessões de Carteira", "Participações em Coligadas"],
        "Valor_bi": [4.2, 2.5, 2.1, 0.47],
    })
    fig3 = px.bar(receitas, x="Componente", y="Valor_bi", color="Componente",
                  title="Decomposição da Receita de Intermediação — 2024 (R$ bi)",
                  template="plotly_white",
                  color_discrete_sequence=px.colors.qualitative.Set2)
    fig3.update_layout(showlegend=False, height=300)
    st.plotly_chart(fig3, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
elif "Predição" in secoes:
    st.subheader("🔮 Predição — Projeção de Ativo Total (2025)")
    st.markdown("""
    **Metodologia:** Regressão Linear Simples com base na série histórica do ativo total.
    O modelo usa índice temporal como variável preditora para capturar a tendência de crescimento.
    """)

    col_cfg, col_res = st.columns([1, 2])

    with col_cfg:
        st.markdown("#### Configurações")
        n_semestres = st.slider("Projetar quantos semestres à frente?", 1, 4, 2)
        incluir_ic = st.checkbox("Exibir intervalo de confiança (95%)", value=True)
        cenario = st.selectbox(
            "Cenário de crescimento",
            ["Tendência histórica (regressão)", "Conservador (-30%)", "Otimista (+20%)"],
        )

    with col_res:
        # Preparar dados para regressão
        df_reg = df.copy().reset_index(drop=True)
        X = np.arange(len(df_reg)).reshape(-1, 1)
        y = df_reg["ativo_total_bi"].values

        model = LinearRegression()
        model.fit(X, y)

        # Projeção
        n_total = len(df_reg) + n_semestres
        X_pred = np.arange(n_total).reshape(-1, 1)
        y_pred = model.predict(X_pred)

        # Ajuste de cenário
        fator = {"Tendência histórica (regressão)": 1.0,
                 "Conservador (-30%)": 0.7, "Otimista (+20%)": 1.2}[cenario]
        y_pred_ajustado = y_pred.copy()
        y_pred_ajustado[len(df_reg):] *= fator

        # Intervalo de confiança simples (±1.96 * resíduo std)
        residuos = y - model.predict(X)
        std_resid = np.std(residuos)
        ic_sup = y_pred_ajustado + 1.96 * std_resid
        ic_inf = y_pred_ajustado - 1.96 * std_resid

        # Labels dos períodos projetados
        ultimos_periodos = df_reg["periodo"].tolist()
        ano_base = int(ultimos_periodos[-1].split("-")[0])
        sem_base = int(ultimos_periodos[-1].split("S")[1])
        periodos_futuros = []
        for i in range(1, n_semestres + 1):
            sem = sem_base + i
            ano = ano_base + (sem - 1) // 2
            sem_real = ((sem_base + i - 1) % 2) + 1
            periodos_futuros.append(f"{ano}-S{sem_real}")

        todos_periodos = ultimos_periodos + periodos_futuros

        fig = go.Figure()

        if incluir_ic:
            fig.add_trace(go.Scatter(
                x=todos_periodos, y=ic_sup.round(1),
                mode="lines", line=dict(width=0), showlegend=False,
            ))
            fig.add_trace(go.Scatter(
                x=todos_periodos, y=ic_inf.round(1),
                mode="lines", fill="tonexty",
                fillcolor="rgba(0,102,204,0.15)",
                line=dict(width=0), name="IC 95%",
            ))

        fig.add_trace(go.Scatter(
            x=ultimos_periodos, y=y.round(1),
            mode="lines+markers", name="Histórico",
            line=dict(color="#0066cc", width=3),
            marker=dict(size=7),
        ))
        fig.add_trace(go.Scatter(
            x=todos_periodos, y=y_pred_ajustado.round(1),
            mode="lines+markers", name=f"Projeção ({cenario[:12]}…)",
            line=dict(color="#e74c3c", width=2, dash="dash"),
            marker=dict(size=6, symbol="diamond"),
        ))
        # Linha vertical separando histórico de projeção (compatível com eixo categórico)
        idx_corte = len(ultimos_periodos) - 1
        fig.add_trace(go.Scatter(
            x=[ultimos_periodos[-1], ultimos_periodos[-1]],
            y=[0, float(y_pred_ajustado.max()) * 1.1],
            mode="lines",
            line=dict(color="gray", dash="dot", width=1.5),
            name="Corte histórico",
            showlegend=False,
        ))

        fig.update_layout(
            title=f"Projeção do Ativo Total — +{n_semestres} semestre(s)",
            xaxis_title="Período", yaxis_title="R$ Bilhões",
            template="plotly_white", height=380, hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Tabela de projeção
        proj_tab = pd.DataFrame({
            "Período": periodos_futuros,
            "Projeção (R$ bi)": y_pred_ajustado[len(df_reg):].round(1),
            "IC inferior (R$ bi)": ic_inf[len(df_reg):].round(1),
            "IC superior (R$ bi)": ic_sup[len(df_reg):].round(1),
        })
        st.dataframe(proj_tab, use_container_width=True, hide_index=True)

        r2 = model.score(X, y)
        st.caption(f"R² do modelo: {r2:.4f} | Coeficiente angular: {model.coef_[0]:.2f} R$ bi/semestre")

    st.markdown("""
    <div class='alerta'>
    ⚠️ <b>Nota metodológica:</b> Esta projeção usa regressão linear simples — adequada para 
    fins acadêmicos, mas limitada para instituições com dinâmica de crescimento não-linear 
    como o Banco Master. Modelos mais robustos (ARIMA, regressão com variáveis macroeconômicas) 
    são recomendados para análise profissional.
    </div>
    """, unsafe_allow_html=True)

# ─── Rodapé ────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "Dados: BCB/IF.data · Demonstrações Financeiras Banco Master · Balanço consolidado dez/2024. "
    "Análise para fins acadêmicos. Não constitui recomendação de investimento."
)
