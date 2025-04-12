
import streamlit as st
import pyettj.ettj as ettj
import pandas as pd
from datetime import datetime, timedelta

# Função para buscar curva mais recente
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

# Função para simular preço com base na taxa
def calcular_preco_simulado(taxa, dias_corridos):
    return 6000 / ((1 + taxa / 100) ** (dias_corridos / 252))

# Layout Streamlit
st.set_page_config(layout="wide")
st.title("📈 Curva de Juros com Simulação - DOLK25")

# Buscar curva
with st.spinner("Buscando curva ETTJ mais recente..."):
    df, data_utilizada = buscar_curva_mais_recente()

# Selecionar pontos DI
dias_para_di = {
    'Ponta Menor (DI1F25)': 250,
    'Ponta Principal (DI1F26)': 500,
    'Intermediário (DI1F27)': 750,
    'Ponta Longa (DI1F30)': 1000,
    'Ponta Maior (DI1F32)': 1250
}

# Processar DataFrame
df['Dias Corridos'] = df['Dias Corridos'].astype(int)
df['DI x pré 252'] = df['DI x pré 252'].astype(float)

st.subheader(f"🗓️ Curva do dia: {data_utilizada}")

data_display = []
for nome, dias in dias_para_di.items():
    linha = df.iloc[(df['Dias Corridos'] - dias).abs().argmin()]
    taxa = linha['DI x pré 252']
    preco = calcular_preco_simulado(taxa, dias)

    # Stop/gain input
    col1, col2 = st.columns(2)
    with col1:
        stop = st.number_input(f"Stop para {nome}", value=taxa + 1.0, step=0.1)
    with col2:
        gain = st.number_input(f"Gain para {nome}", value=taxa - 1.0, step=0.1)

    tendencia = "🔴 Venda" if taxa > stop else "🟢 Compra" if taxa < gain else "⚪ Neutra"

    data_display.append({
        "Ponto": nome,
        "Preço Simulado (R$)": f"R$ {preco:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        "Taxa (%)": f"{taxa:.2f}",
        "Tendência": tendencia
    })

# Exibir tabela
st.table(pd.DataFrame(data_display))

st.markdown("---")
st.caption("Desenvolvido para monitorar a curva ETTJ com base no contrato DOLK25 - versão beta")
