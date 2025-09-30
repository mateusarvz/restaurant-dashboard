import streamlit as st
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import unicodedata
from pathlib import Path

def carregar_json(nome_arquivo):
    path = Path("Dict_Valores") / nome_arquivo
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

entradas = carregar_json("dict_entradas.json")
pratos = carregar_json("dict_pratos.json")
sobremesas = carregar_json("dict_sobremesas.json")
bebidas = carregar_json("dict_bebidas.json")


st.markdown(
    "<h1 style='text-align: center;'>Dashboar RestauranteTeste</h1>", 
    unsafe_allow_html=True
)
st.markdown("---")

# ------------------------------
# Conexão com Google Sheets
# ------------------------------

cred_dict = json.loads(st.secrets["GSHEET_CRED"])
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(cred_dict, scope)
client = gspread.authorize(creds)



#arquivo_credenciais = "credenciais.json"
#scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
#creds = ServiceAccountCredentials.from_json_keyfile_name(arquivo_credenciais, scope)
#client = gspread.authorize(creds)


sheet = client.open("DF-Pedidos").sheet1
dados = sheet.get_all_records()
df = pd.DataFrame(dados)

def limpar_datahora(valor):
    if pd.isna(valor):
        return None
    valor = str(valor).strip()
    if valor.endswith(".0"):
        valor = valor.replace(".0", "")
    valor = unicodedata.normalize("NFKC", valor)

    return valor

df["DataHora"] = df["DataHora"].apply(limpar_datahora)
df["DataHora"] = pd.to_datetime(df["DataHora"], errors="coerce", dayfirst=True)
df = df.dropna(subset=["DataHora"]).reset_index(drop=True)
anos_disponiveis = sorted(df["DataHora"].dt.year.unique())
meses = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

if "anos_selecionados" not in st.session_state:
    st.session_state.anos_selecionados = []
if "meses_selecionados" not in st.session_state:
    st.session_state.meses_selecionados = []
if "periodo_mensagem" not in st.session_state:
    st.session_state.periodo_mensagem = ""

with st.sidebar:
    st.markdown("## Seleção de Período")
    # ------------------------------
    # Preparar dados
    # ------------------------------
    df["DataHora"] = pd.to_datetime(df["DataHora"], errors="coerce")
    df_valid = df[df["DataHora"].notna()]

    ano_min = df_valid["DataHora"].dt.year.min()
    ano_max = df_valid["DataHora"].dt.year.max()
    anos_disponiveis = list(range(ano_min, ano_max + 1))

    meses = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }

    # ------------------------------
    # Seletor de Anos
    # ------------------------------
    modo_ano = st.radio(
        "Selecione o tipo de período em anos",
        ["Um ano", "Intervalo de anos"], index=0
    )

    if modo_ano == "Um ano":
        ano = st.selectbox("Selecione o ano", anos_disponiveis, index=len(anos_disponiveis)-1)
        anos_selecionados = [ano]
    else:
        col1, col2 = st.columns(2)
        with col1:
            ano_inicio = st.selectbox("Ano inicial", anos_disponiveis, index=0)
        with col2:
            ano_fim = st.selectbox("Ano final", anos_disponiveis, index=len(anos_disponiveis)-1)

        if ano_inicio <= ano_fim:
            anos_selecionados = list(range(ano_inicio, ano_fim + 1))
        else:
            st.error("O ano inicial deve ser menor ou igual ao ano final.")
            anos_selecionados = []
    st.markdown("---")
    # ------------------------------
    # Seletor de Meses
    # ------------------------------
    
    todos_os_meses = st.checkbox("Selecionar todos os meses", value=True)

    if todos_os_meses:
        meses_selecionados = list(meses.keys())
    else:
        modo_mes = st.radio(
            "Escolha o tipo de seleção em meses",
            ["Um mês", "Intervalo de meses"]
        )

        if modo_mes == "Um mês":
            mes = st.selectbox("Selecione o mês", list(meses.keys()), format_func=lambda x: meses[x])
            meses_selecionados = [mes]
        else:
            mes_inicio, mes_fim = st.select_slider(
                "Selecione o intervalo de meses",
                options=list(meses.keys()),
                value=(1, 12),
                format_func=lambda x: meses[x]
            )
            meses_selecionados = list(range(mes_inicio, mes_fim + 1))

    # ------------------------------
    # Botão único para aplicar tudo
    # ------------------------------
    col1, col2, col3 = st.columns([1, 2, 1])  # a coluna do meio é maior, assim o botão fica centralizado
    with col2:
        if st.button("Aplicar seleção"):
            st.session_state.anos_selecionados = anos_selecionados
            st.session_state.meses_selecionados = meses_selecionados

            if len(anos_selecionados) == 1:
                ano_msg = f"Ano: <b>{anos_selecionados[0]}</b>"
            else:
                ano_msg = f"Anos: <b>{anos_selecionados[0]} a {anos_selecionados[-1]}</b>"

            if len(meses_selecionados) == 1:
                mes_msg = f"Mês: <b>{meses[meses_selecionados[0]]}</b>"
            else:
                mes_msg = f"Meses: <b>{meses[meses_selecionados[0]]} a {meses[meses_selecionados[-1]]}</b>"

            st.session_state.periodo_mensagem = (ano_msg, mes_msg)

    if st.session_state.periodo_mensagem:
        st.markdown("---")
        st.markdown("<h3 style='text-align: center; color: #FF4B4B;'>Período Selecionado</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; font-size:18px;'>{st.session_state.periodo_mensagem[0]}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; font-size:18px;'>{st.session_state.periodo_mensagem[1]}</p>", unsafe_allow_html=True)
        st.markdown("---")

# ------------------------------
# Filtragem dos dados
# ------------------------------
df_periodo = df[
    (df["DataHora"].dt.year.isin(st.session_state.anos_selecionados)) &
    (df["DataHora"].dt.month.isin(st.session_state.meses_selecionados))
]
# ------------------------------
# Variável de período selecionado
# ------------------------------
if st.session_state.periodo_mensagem:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f"<p style='text-align: center; font-size:18px;'>{st.session_state.periodo_mensagem[0]}</p>",
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"<p style='text-align: left; font-size:18px;'>{st.session_state.periodo_mensagem[1]}</p>",
            unsafe_allow_html=True
        )
# ------------------------------
# Abas de análise
# ------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Visão Geral",
    "🥗 Entradas",
    "🍽️ Pratos",
    "🍰 Sobremesas",
    "🥤 Bebidas",
    "📈 Vendas por Tempo"
])
# ------------------------------
# Aba 1 - Visão Geral
# ------------------------------
with tab1:
    if df_periodo.empty:
        st.warning("Nenhum dado disponível para o período selecionado.")
    else:
        # ------------------------------
        # Métricas
        # ------------------------------
        total_vendas = df_periodo["Valor"].sum()
        qtd_pedidos = df_periodo["IDPedido"].nunique()
        ticket_medio = total_vendas / qtd_pedidos if qtd_pedidos > 0 else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Vendas", f"R$ {total_vendas:,.2f}")
        col2.metric("Número de Pedidos", qtd_pedidos)
        col3.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")

        # ------------------------------
        # Preparar dados para gráficos
        # ------------------------------
        df_periodo["Ano"] = df_periodo["DataHora"].dt.year
        df_periodo["Mes"] = df_periodo["DataHora"].dt.month
        vendas_por_ano_mes = df_periodo.groupby(["Ano", "Mes"])["Valor"].sum().reset_index()

        meses_selecionados = st.session_state.meses_selecionados
        st.markdown("---")

    # ------------------------------
    # Gráfico de vendas por mês ou por ano
    # ------------------------------
        cores = [
            "#BD4F4F", "#BA70A2", "#7C79B4", "#6B8E6C", 
            "#84ACA4", "#89779F", "#9B995D", "#796B79"
        ]

        fig, ax = plt.subplots(figsize=(10,5))

        if len(meses_selecionados) == 1:
            mes = meses_selecionados[0]
            vendas_mes = df_periodo[df_periodo["DataHora"].dt.month == mes]
            vendas_por_ano = vendas_mes.groupby(vendas_mes["DataHora"].dt.year)["IDPedido"].count().reset_index()
            vendas_por_ano.rename(columns={"DataHora": "Ano", "IDPedido": "Quantidade"}, inplace=True)

            ax.bar(vendas_por_ano["Ano"].astype(str), vendas_por_ano["Quantidade"], 
                color="#EA6464", edgecolor="black", width=0.5)
            st.markdown(
                f"<p style='text-align: center; font-size:18px;'>{'Vendas no ' + st.session_state.periodo_mensagem[1]}</p>",
                unsafe_allow_html=True
            )
            ax.grid(axis="y", linestyle="--", alpha=0.7)
            st.pyplot(fig)

        else:
            anos_unicos = sorted(df_periodo["DataHora"].dt.year.unique())
            for i, ano in enumerate(anos_unicos):
                vendas_ano = df_periodo[df_periodo["DataHora"].dt.year == ano]
                vendas_mensais = vendas_ano.groupby(vendas_ano["DataHora"].dt.month)["IDPedido"].count()
                
                # Manter apenas até o último mês com venda
                meses_com_venda = vendas_mensais.index[vendas_mensais > 0]
                if len(meses_com_venda) > 0:
                    vendas_mensais = vendas_mensais.loc[:meses_com_venda[-1]]
                    cor = cores[i % len(cores)]
                    ax.plot(vendas_mensais.index, vendas_mensais.values, marker="o", label=str(ano), color=cor, linewidth=2)

            ax.set_title("Vendas Mensais por Ano", fontsize=16)
            ax.set_xticks(range(1, 13))
            ax.set_xticklabels(["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"])
            ax.grid(axis="y", linestyle="--", alpha=0.7)
            ax.legend(title="Ano")
            st.pyplot(fig)

        # ------------------------------
        # Gráfico de vendas por dia da semana
        # ------------------------------

        dias_ingles_para_portugues = {
        "Monday": "Segunda-feira",
        "Tuesday": "Terça-feira",
        "Wednesday": "Quarta-feira",
        "Thursday": "Quinta-feira",
        "Friday": "Sexta-feira",
        "Saturday": "Sábado",
        "Sunday": "Domingo"
    }

        df_periodo["DiaSemana"] = df_periodo["DataHora"].dt.day_name()  # pega o nome em inglês
        df_periodo["DiaSemana"] = df_periodo["DiaSemana"].map(dias_ingles_para_portugues)  # traduz para português
        
        vendas_por_dia = df_periodo.groupby("DiaSemana")["IDPedido"].count()
        ordem_dias = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira",
                    "Sexta-feira", "Sábado", "Domingo"]
        vendas_por_dia = vendas_por_dia.reindex(ordem_dias, fill_value=0)


        ordem_dias = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira",
                    "Sexta-feira", "Sábado", "Domingo"]
        vendas_por_dia = vendas_por_dia.reindex(ordem_dias, fill_value=0)

        fig, ax = plt.subplots(figsize=(10, 5))
        vendas_por_dia.plot(kind="bar", color="#EE6666", edgecolor="black", ax=ax)

        ax.set_title("Vendas por Dia da Semana", fontsize=16)
        ax.set_xlabel("")
        ax.grid(axis="y", linestyle="--", alpha=0.7)
        st.pyplot(fig)


# ------------------------------
# Aba 2 - Entradas
# ------------------------------
def normalizar_texto(s):
    if pd.isna(s):
        return s
    s = " ".join(s.split())  
    s = unicodedata.normalize("NFC", s.strip())
    return s

entradas_expandidas = (
    df_periodo["Entradas"]
    .dropna()
    .str.split(",")
    .explode()
    .map(normalizar_texto)
)

pratos_expandidos = (
    df_periodo["Pratos"]
    .dropna()
    .str.split(",")
    .explode()
    .map(normalizar_texto)
)

sobremesas_expandidas = (
    df_periodo["Sobremesas"]
    .dropna()
    .str.split(",")
    .explode()
    .map(normalizar_texto)
)

bebidas_expandidas = (
    df_periodo["Bebidas"]
    .dropna()
    .str.split(",")
    .explode()
    .map(normalizar_texto)
)   

contagem_entradas = entradas_expandidas.value_counts()
dicionario_entradas = contagem_entradas.to_dict()

contagem_pratos = pratos_expandidos.value_counts()
dicionario_pratos = contagem_pratos.to_dict()

contagem_sobremesas = sobremesas_expandidas.value_counts()
dicionario_sobremesas = contagem_sobremesas.to_dict()

contagem_bebidas = bebidas_expandidas.value_counts()
dicionario_bebidas = contagem_bebidas.to_dict()

def plot_horizontal_valor_total(df_periodo, coluna_item, dicionario_valores, titulo, cor='#FF3B3B'):
    if df_periodo.empty:
        st.warning(f"Sem dados para {titulo.lower()}.")
        return
    
    itens_expandidos = (
        df_periodo[coluna_item]
        .dropna()
        .str.split(",")
        .explode()
        .map(lambda x: x.strip())
    )

    contagem_itens = itens_expandidos.value_counts()
    contagem_filtrada = {k: v for k, v in contagem_itens.items() if k and k.lower() != 'nenhuma'}
    itens_ordenados = dict(sorted(contagem_filtrada.items(), key=lambda x: x[1], reverse=True))

    nomes = list(itens_ordenados.keys())
    quantidades = list(itens_ordenados.values())

    # Ajustar altura proporcional ao número de itens
    altura_fig = max(6, len(nomes) * 0.5)  # mínimo 6, 0.5 por barra
    fig, ax = plt.subplots(figsize=(12, altura_fig))

    bars = ax.barh(nomes, quantidades, color=cor, edgecolor='black', alpha=1)
    ax.invert_yaxis()

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.grid(False)

    ax.set_title(titulo, fontsize=16, weight='bold')
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.tick_params(left=False, bottom=False)
    ax.set_xticks([])

    # Limite horizontal fixo para padronizar largura visual
    ax.set_xlim(0, max(quantidades)*1.2 if quantidades else 1)

    for bar, item in zip(bars, nomes):
        quantidade = bar.get_width()
        valor_total = quantidade * dicionario_valores.get(item, 0)

        ax.text(quantidade*0.02, bar.get_y() + bar.get_height()/2,
                f'{int(quantidade)}', va='center', ha='left', fontsize=10, fontweight='bold', color='white')

        ax.text(quantidade + max(quantidades)*0.02, bar.get_y() + bar.get_height()/2,
                f'R$ {valor_total:,.2f}', va='center', ha='left', fontsize=10, fontweight='bold', color='black')

    fig.subplots_adjust(left=0.2, right=0.8, top=0.85, bottom=0.15)
    st.pyplot(fig)


# ------------------------------
# Usando a função para cada aba
# ------------------------------
with tab2:
    if df_periodo.empty:
        st.warning("Nenhum dado disponível para o período selecionado.")
    else:
        plot_horizontal_valor_total(df_periodo, "Entradas", entradas, "Entradas", cor='#FF4C4C')

with tab3:
    if df_periodo.empty:
        st.warning("Nenhum dado disponível para o período selecionado.")
    else:
        plot_horizontal_valor_total(df_periodo, "Pratos", pratos, "Pratos", cor='#FF4C4C')

with tab4:
    if df_periodo.empty:
        st.warning("Nenhum dado disponível para o período selecionado.")
    else:
        plot_horizontal_valor_total(df_periodo, "Sobremesas", sobremesas, "Sobremesas", cor='#FF4C4C')

with tab5:
    if df_periodo.empty:
        st.warning("Nenhum dado disponível para o período selecionado.")
    else:
        plot_horizontal_valor_total(df_periodo, "Bebidas", bebidas, "Bebidas", cor='#FF4C4C')

# ------------------------------
# Aba 6 - Vendas por Tempo
# ------------------------------
with tab6:
    if df_periodo.empty:
        st.warning("Nenhum dado disponível para o período selecionado.")
    else:
        df_periodo_filtrado = df_periodo[
            (df_periodo["DataHora"].dt.hour >= 18) & 
            (df_periodo["DataHora"].dt.hour <= 23)
        ]

        intervalos = pd.date_range("18:00", "23:00", freq="30min").strftime("%H:%M")

        df_periodo_filtrado['Horario'] = df_periodo_filtrado["DataHora"].dt.floor('30min').dt.strftime("%H:%M")
        vendas_por_horario = df_periodo_filtrado.groupby("Horario")["IDPedido"].count()
        vendas_por_horario = vendas_por_horario.reindex(intervalos, fill_value=0)

        fig, ax = plt.subplots(figsize=(10, 4))
        vendas_por_horario.plot(kind="line", color="#D26262", marker='o', ax=ax)

        ax.set_title("Vendas por Horário", fontsize=16)
        ax.set_xticks(range(len(intervalos)))
        ax.set_xticklabels(intervalos, rotation=45)
        ax.grid(axis="y", linestyle="--", alpha=0.7)

        st.pyplot(fig)

