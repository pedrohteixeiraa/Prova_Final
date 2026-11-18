import os
from io import BytesIO

import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(
    page_title="Índice de Qualidade de Vida Urbana IQVU dos bairros de Belo Horizonte",
    layout="wide"
)

# Caminho RELATIVO (assim funciona no computador e no Streamlit Cloud)
arquivo = "bd_iqvu_1994_2016.csv"

COL_GRUPO = "NOMEUP"    
COL_ANO = "ANO"         
COL_VALOR = "IQVU"      
COL_SERIE = "ï»¿SERIE"

GRUPO_1 = "Taquaril"
GRUPO_2 = "Santa Ines"

VALOR_SERIE = "SERIE HISTORICA"

COR_1 = "#FF6B6B"
COR_2 = "#00F5D4"
CORES = {GRUPO_1: COR_1, GRUPO_2: COR_2}

DIMENSOES = {
    "Educacao": "Educação",
    "Saude": "Saúde",
    "Habitacao": "Habitação",
    "Infraestrutura": "Infraestrutura",
    "Cultura": "Cultura",
}

DISPERSAO_X = "Educacao"
DISPERSAO_Y = "Saude"

ASSUNTO = "IQVU"
TITULO_PAINEL = " Índice de Qualidade de Vida Urbana IQVU"
FONTE = "Fonte dos dados: dados abertos da Prefeitura de Belo Horizonte — https://dados.pbh.gov.br/"

df = pd.read_csv("bd_iqvu_1994_2016.csv", sep=";", encoding="latin-1",
decimal=",")
df.columns = df.columns.str.replace("\ufeff", "", regex=False).str.strip()
df[COL_GRUPO] = df[COL_GRUPO].astype(str).str.strip()
st.dataframe(df)

df_filtrado = df[
    (df[COL_GRUPO].isin([GRUPO_1, GRUPO_2])) &
    (df[COL_SERIE] == VALOR_SERIE)
].copy()

df_filtrado = df_filtrado.sort_values(COL_ANO)


df_tabela = df_filtrado[[COL_GRUPO, COL_ANO, COL_VALOR]]

ANO_FINAL = df_filtrado[COL_ANO].max()
ANO_INICIAL = df_filtrado[COL_ANO].min()

df_ultimo_ano = df_filtrado[df_filtrado[COL_ANO] == ANO_FINAL]

dados_longo = df_ultimo_ano.melt(
    id_vars=["Col_Grupo"],
    value_vars= ["Taquaril", "Santa ines"],
    var_name="Dimensao",
    value_name="Valor",
).rename(columns={COL_GRUPO: "Bairro"})
dados_longo["Dimensao"] = dados_longo["Dimensao"].map(DIMENSOES)

df_ultimo_ano = df_filtrado[df_filtrado[COL_ANO] == ANO_FINAL]

dados_longo = df_ultimo_ano.melt(
    id_vars=COL_GRUPO,
    value_vars=list(DIMENSOES.keys()),
    var_name="Dimensao",
    value_name="Valor",
).rename(columns={COL_GRUPO: "Bairro"})
dados_longo["Dimensao"] = dados_longo["Dimensao"].map(DIMENSOES)

dados_empilhado = dados_longo[["Bairro", "Dimensao", "Valor"]]

dados_radar = dados_longo.rename(columns={"Valor": "Nota"})[["Bairro", "Dimensao", "Nota"]]

dados_pizza = df_ultimo_ano[[COL_GRUPO, COL_VALOR]].rename(columns={COL_GRUPO: "Bairro"})

st.title(TITULO_PAINEL)

st.sidebar.header("Controles")
opcao = st.sidebar.radio("Selecione a visualização:", ["Tabela", "Gráficos"])
if opcao == "Tabela":
    st.header(f"Tabela do {ASSUNTO} (Série Histórica)")
    st.dataframe(df_tabela, use_container_width=True, hide_index=True)
else:
    st.header(f"Gráficos do {ASSUNTO} — {GRUPO_1} e {GRUPO_2}")

    st.subheader(f"1. Gráfico de Linha — {GRUPO_1}")
    df_grupo_1 = df_tabela[df_tabela[COL_GRUPO] == GRUPO_1]

    fig_linha_1 = px.line(
        df_grupo_1,
        x=COL_ANO,
        y=COL_VALOR,
        markers=True,
        title=f"Evolução do {ASSUNTO} — {GRUPO_1} ({ANO_INICIAL} a {ANO_FINAL})",
        template="plotly_dark",
    )
    fig_linha_1.update_traces(line_color=COR_1, line_width=3, marker_size=8)
    fig_linha_1.update_xaxes(type="category")
    st.plotly_chart(fig_linha_1, use_container_width=True)

    st.subheader(f"2. Gráfico de Linha — {GRUPO_2}")
    df_grupo_2 = df_tabela[df_tabela[COL_GRUPO] == GRUPO_2]

    fig_linha_2 = px.line(
        df_grupo_2,
        x=COL_ANO,
        y=COL_VALOR,
        markers=True,
        title=f"Evolução do {ASSUNTO} — {GRUPO_2} ({ANO_INICIAL} a {ANO_FINAL})",
        template="plotly_dark",
    )
    fig_linha_2.update_traces(line_color=COR_2, line_width=3, marker_size=8)
    fig_linha_2.update_xaxes(type="category")
    st.plotly_chart(fig_linha_2, use_container_width=True)

    st.subheader("3. Gráfico de Barras Agrupadas")
    fig_barras = px.bar(
        df_tabela,
        x=COL_ANO,
        y=COL_VALOR,
        color=COL_GRUPO,
        barmode="group",
        title=f"Comparativo Anual de {ASSUNTO} (Barras Agrupadas)",
        color_discrete_map=CORES,
        template="plotly_dark",
    )
    fig_barras.update_xaxes(type="category")
    st.plotly_chart(fig_barras, use_container_width=True)

    st.subheader(f"4. Gráfico de Barras Empilhadas (Dimensões em {ANO_FINAL})")
    fig_empilhado = px.bar(
        dados_empilhado,
        x="Bairro",
        y="Valor",
        color="Dimensao",
        barmode="stack",
        title=f"Composição do {ASSUNTO} por Dimensão — Ano {ANO_FINAL} (Barras Empilhadas)",
        template="plotly_dark",
    )
    st.plotly_chart(fig_empilhado, use_container_width=True)

    st.subheader("5. Gráfico de Pizza")
    fig_pizza = px.pie(
        dados_pizza,
        names="Bairro",
        values=COL_VALOR,
        title=f"Proporção do {ASSUNTO} entre os Bairros ({ANO_FINAL})",
        color="Bairro",
        color_discrete_map=CORES,
        template="plotly_dark",
    )
    fig_pizza.update_traces(textinfo="percent+label+value")
    st.plotly_chart(fig_pizza, use_container_width=True)

    st.subheader("6. Gráfico de Radar")
    fig_radar = px.line_polar(
        dados_radar,
        r="Nota",
        theta="Dimensao",
        color="Bairro",
        line_close=True,
        title=f"Perfil Multidimensional (Gráfico de Radar - {ANO_FINAL})",
        color_discrete_map=CORES,
        template="plotly_dark",
    )
    fig_radar.update_traces(fill="toself")
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])))
    st.plotly_chart(fig_radar, use_container_width=True)

    st.subheader("7. Gráfico de Área")
    fig_area = px.area(
        df_tabela,
        x=COL_ANO,
        y=COL_VALOR,
        color=COL_GRUPO,
        title=f"Evolução em Área do {ASSUNTO} ({ANO_INICIAL} a {ANO_FINAL})",
        color_discrete_map=CORES,
        template="plotly_dark",
    )
    fig_area.update_xaxes(type="category")
    st.plotly_chart(fig_area, use_container_width=True)

    st.subheader("8. Gráfico de Dispersão (Bolhas)")
    fig_dispersao = px.scatter(
        df_filtrado,
        x=DISPERSAO_X,
        y=DISPERSAO_Y,
        color=COL_GRUPO,
        size=COL_VALOR,
        hover_data=[COL_ANO],
        title=f"Dispersão: {DIMENSOES.get(DISPERSAO_X, DISPERSAO_X)} vs "
              f"{DIMENSOES.get(DISPERSAO_Y, DISPERSAO_Y)} (Tamanho = {ASSUNTO})",
        color_discrete_map=CORES,
        template="plotly_dark",
    )
    st.plotly_chart(fig_dispersao, use_container_width=True)

    st.subheader("9. Gráfico Boxplot")
    fig_box = px.box(
        df_tabela,
        x=COL_GRUPO,
        y=COL_VALOR,
        color=COL_GRUPO,
        points="all",
        title=f"Distribuição Estatística do {ASSUNTO} (Boxplot)",
        color_discrete_map=CORES,
        template="plotly_dark",
    )
    st.plotly_chart(fig_box, use_container_width=True)

st.markdown("---")
st.caption(FONTE)



