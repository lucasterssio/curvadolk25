
import streamlit as st
import pyettj.ettj as ettj
import pandas as pd
from datetime import datetime, timedelta
import yfinance as yf
import time

# Configuração de página
st.set_page_config(layout="wide", page_title="Curva DOLK25", page_icon="📉")

# Estilo visual
st.markdown("""
    <style>
    .main { background-color: #0f1117; color: #f0f2f6; }
    th, td { text-align: center !important; }
    .block-container { padding-top: 1rem; }
    </style>
""", unsafe_allow_html=True)

st.title("📈 Curva de Juros + Dólar Futuro (DOLK25)")
st.caption("Visualização em tempo real com atualização a cada 3 minutos")

# 🔁 Sidebar
st.sidebar.header("Configurações")
autorefresh = st.sidebar.checkbox("🔄 Atualização automática", value=True)
tempo = st.sidebar.slider("⏱️ Intervalo (segundos)", 60, 300, 180, step=30)

# Buscar curva ETTJ
def buscar_curva_mais_recente():
    dias_para_voltar = 0
    while dias_para_voltar < 10:
        data_tentativa = datetime.today() - timedelta(days=dias_para_voltar)
        data_formatada = data_tentativa.strftime('%d/%m/%Y')
        try:
            df = ettj.get_ettj(data_formatada)
            return df, data_formatada
        except ValueError:
            dias_para_voltar += 1
    raise Exception("Curva ETTJ não encontrada nos últimos 10 dias úteis.")

# Preço Dólar Futuro (Yahoo Finance)
def pegar_preco_dolk25():
    try:
        dol = yf.Ticker("DOL=F")
        dados = dol.history(period="1d", interval="1m")
        return float(dados["Close"].dropna().iloc[-1])
    except:
        return None

# Cálculo de PU simulado
def calcular_preco_simulado(taxa, dias_corridos):
    return 6000 / ((1 + taxa / 100) ** (dias_corridos / 252))

# Loop para atualização
placeholder = st.empty()

while True:
    with placeholder.container():
        st.markdown("---")
        col_a, col_b = st.columns(2)

        with col_a:
            preco_dol = pegar_preco_dolk25()
            if preco_dol:
                st.metric("💵 Dólar Futuro (DOLK25)", f"R$ {preco_dol:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            else:
                st.warning("Dólar Futuro indisponível (verifique conexão)")

        with col_b:
            try:
                df, data_utilizada = buscar_curva_mais_recente()
                st.metric("📅 Curva disponível em:", data_utilizada)
            except:
                st.error("Erro ao buscar curva ETTJ")
                break

        dias_para_di = {
            'Ponta Menor (DI1F25)': 250,
            'Ponta Principal (DI1F26)': 500,
            'Intermediário (DI1F27)': 750,
            'Ponta Longa (DI1F30)': 1000,
            'Ponta Maior (DI1F32)': 1250
        }

        df['Dias Corridos'] = df['Dias Corridos'].astype(int)
        df['DI x pré 252'] = df['DI x pré 252'].astype(float)

        data_display = []
        for nome, dias in dias_para_di.items():
            linha = df.iloc[(df['Dias Corridos'] - dias).abs().argmin()]
            taxa = linha['DI x pré 252']
            preco = calcular_preco_simulado(taxa, dias)

            tendencia = "🔴 Venda" if taxa > 12.5 else "🟢 Compra" if taxa < 10.5 else "⚪ Neutra"

            data_display.append({
                "🧭 Ponto": nome,
                "💰 PU Simulado": f"R$ {preco:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                "📊 Taxa (%)": f"{taxa:.2f}",
                "📈 Tendência": tendencia
            })

        st.table(pd.DataFrame(data_display))
        st.markdown("---")
        st.caption("Atualização automática a cada 3 minutos | Dados com atraso | Apenas visualização")

    if not autorefresh:
        break
    time.sleep(tempo)
    placeholder.empty()
