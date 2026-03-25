
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


st.set_page_config(
    page_title="Painel de Veículos",
    page_icon="🚘",
    layout="wide"
)



@st.cache_data
def carregar_base():
    try:
        df = pd.read_csv("vehicles_processed.csv")
    except:
        df = pd.read_csv("vehicles.csv")
        df["brand"] = df["model"].str.split().str[0]
        df["date_posted"] = pd.to_datetime(df["date_posted"])
        df["paint_color"].fillna("unknown", inplace=True)
        df["is_4wd"].fillna(0, inplace=True)

    df["model_year"] = pd.to_numeric(df["model_year"], errors="coerce")
    return df


def aplicar_filtros(df):
    st.sidebar.header("🔎 Filtros")

    anos = df["model_year"].dropna().astype(int)
    ano_range = st.sidebar.slider(
        "Ano do veículo",
        int(anos.min()), int(anos.max()),
        (int(anos.min()), int(anos.max()))
    )

    preco_range = st.sidebar.slider(
        "Faixa de preço",
        int(df["price"].min()),
        int(df["price"].max()),
        (int(df["price"].min()), int(df["price"].max()))
    )

    condicoes = ["Todas"] + sorted(df["condition"].dropna().unique())
    cond = st.sidebar.selectbox("Condição", condicoes)

    filtrado = df[
        (df["model_year"].between(*ano_range)) &
        (df["price"].between(*preco_range))
    ]

    if cond != "Todas":
        filtrado = filtrado[filtrado["condition"] == cond]

    st.sidebar.metric("Total filtrado", len(filtrado))

    return filtrado


def grafico_comparacao(df):
    st.subheader("📊 Comparação entre Marcas")

    marcas = sorted(df["brand"].dropna().unique())

    col1, col2, col3 = st.columns([2,2,1])
    with col1:
        m1 = st.selectbox("Marca A", marcas)
    with col2:
        m2 = st.selectbox("Marca B", marcas)
    with col3:
        percentual = st.checkbox("Mostrar em %")

    d1 = df[df["brand"] == m1]
    d2 = df[df["brand"] == m2]

    fig = go.Figure()

    hist_mode = "percent" if percentual else None

    fig.add_histogram(x=d1["price"], name=m1, opacity=0.6, histnorm=hist_mode)
    fig.add_histogram(x=d2["price"], name=m2, opacity=0.6, histnorm=hist_mode)

    fig.update_layout(
        barmode="overlay",
        template="plotly_white",
        xaxis_title="Preço",
        yaxis_title="%" if percentual else "Quantidade"
    )

    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    c1.metric(f"{m1} média", f"${d1['price'].mean():,.0f}")
    c2.metric(f"{m2} média", f"${d2['price'].mean():,.0f}")


def tabela_dados(df):
    st.subheader("📋 Tabela de dados")

    colunas = st.multiselect(
        "Escolha colunas",
        df.columns.tolist(),
        default=["brand", "model", "model_year", "price"]
    )

    qtd = st.selectbox("Linhas", [50,100,200], index=1)

    if colunas:
        st.dataframe(df[colunas].head(qtd), use_container_width=True)
    else:
        st.warning("Selecione ao menos uma coluna")


def grafico_tipos(df):
    st.subheader("🚙 Tipos de veículos")

    top = df["brand"].value_counts().head(8).index
    selecionados = st.multiselect(
        "Marcas",
        df["brand"].unique(),
        default=top
    )

    if selecionados:
        temp = df[df["brand"].isin(selecionados)]

        resumo = temp.groupby(["brand","type"]).size().reset_index(name="qtd")

        fig = px.bar(
            resumo,
            x="brand",
            y="qtd",
            color="type",
            barmode="group"
        )

        st.plotly_chart(fig, use_container_width=True)


def correlacoes(df):
    st.subheader("🔗 Correlações")

    cols = ["price","odometer","model_year","days_listed"]
    corr = df[cols].corr()

    fig = px.imshow(corr, text_auto=True)
    st.plotly_chart(fig, use_container_width=True)


def estatisticas(df, total):
    st.subheader("📊 Indicadores")

    c1,c2,c3,c4 = st.columns(4)

    c1.metric("Total", len(df))
    c2.metric("Preço médio", f"${df['price'].mean():,.0f}")
    c3.metric("Km médio", f"{df['odometer'].mean():,.0f}")
    c4.metric("Ano médio", f"{df['model_year'].mean():.0f}")



base = carregar_base()
dados = aplicar_filtros(base)

st.title("🚘 Dashboard de Veículos")

grafico_comparacao(dados)

st.divider()

tabela_dados(dados)

st.divider()

grafico_tipos(dados)

st.divider()

correlacoes(dados)

st.divider()

estatisticas(dados, base)

st.caption("Atualizado em " + pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"))
