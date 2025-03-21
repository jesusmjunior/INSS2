import streamlit as st
import pandas as pd
import re
import os
from io import StringIO

# ===================== CONFIG PÁGINA =====================
st.set_page_config(page_title="Jesus e INSS | Extrator CNIS + Carta Benefício", layout="centered")

st.title("📄 JESUS e INSS - Extrator CNIS & Carta Benefício")
st.write("**Processamento leve: Receba dados extraídos em TXT e converta para tabela estruturada, exportando em CSV/XLSX.**")

# ===================== RECEPÇÃO DOS TXT =====================
col1, col2 = st.columns(2)

with col1:
    uploaded_cnis_txt = st.file_uploader("🔽 Upload do arquivo CNIS (TXT):", type="txt", key="cnis_txt")

with col2:
    uploaded_carta_txt = st.file_uploader("🔽 Upload do arquivo Carta Benefício (TXT):", type="txt", key="carta_txt")

output_format = st.radio("📁 Formato de Exportação:", ['CSV', 'XLSX'])

# ===================== FUNÇÕES BASE =====================

def ler_texto(uploaded_file):
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    texto = stringio.read()
    return texto


def sanitizar_numeros(texto):
    texto = re.sub(r'[^0-9.,/\n ]', '', texto)
    texto = texto.replace(',', '.')
    return texto


def estrutura_cnis(texto):
    linhas = texto.split('\n')
    data = []
    for line in linhas:
        line_clean = line.strip()
        match = re.match(r"(\d{2}/\d{4})\s+([0-9.]+)", line_clean)
        if match:
            competencia = match.group(1)
            remuneracao = match.group(2).replace('.', '').replace(',', '.')
            data.append({'Competência': competencia, 'Remuneração': remuneracao})
    return pd.DataFrame(data)


def estrutura_carta(texto):
    linhas = texto.split('\n')
    data = []
    for line in linhas:
        line_clean = line.strip()
        match = re.match(r"^(\d{3})\s+(\d{2}/\d{4})\s+([0-9.,]+)\s+([0-9.,]+)\s+([0-9.,]+)\s+(.*)", line_clean)
        if match:
            seq = match.group(1)
            data_col = match.group(2)
            salario = match.group(3).replace('.', '').replace(',', '.')
            indice = match.group(4).replace(',', '.')
            sal_corrigido = match.group(5).replace('.', '').replace(',', '.')
            observacao = match.group(6)
            data.append({
                'Seq.': seq,
                'Data': data_col,
                'Salário': salario,
                'Índice': indice,
                'Sal. Corrigido': sal_corrigido,
                'Observação': observacao
            })
    return pd.DataFrame(data)


def exportar_df(df, nome_base, formato):
    if formato == 'CSV':
        df.to_csv(f"{nome_base}.csv", index=False)
        return f"{nome_base}.csv"
    else:
        df.to_excel(f"{nome_base}.xlsx", index=False)
        return f"{nome_base}.xlsx"

# ===================== PROCESSAMENTO CNIS TXT =====================

if uploaded_cnis_txt is not None:
    with st.spinner('🔍 Processando arquivo CNIS (TXT)...'):
        texto_txt = ler_texto(uploaded_cnis_txt)
        texto_txt = sanitizar_numeros(texto_txt)
        df_cnis = estrutura_cnis(texto_txt)

        if not df_cnis.empty:
            st.subheader("📊 Dados CNIS Extraídos:")
            st.dataframe(df_cnis)

            file_output = exportar_df(df_cnis, "Extrato_CNIS_Extraido", output_format)
            st.success(f"✅ Exportação CNIS concluída! Arquivo gerado: {file_output}")
            with open(file_output, 'rb') as f:
                st.download_button("⬇️ Baixar Arquivo CNIS", data=f, file_name=file_output, mime='application/octet-stream')

# ===================== PROCESSAMENTO CARTA TXT =====================

if uploaded_carta_txt is not None:
    with st.spinner('🔍 Processando arquivo Carta Benefício (TXT)...'):
        texto_txt = ler_texto(uploaded_carta_txt)
        texto_txt = sanitizar_numeros(texto_txt)
        df_carta = estrutura_carta(texto_txt)

        if not df_carta.empty:
            st.subheader("📊 Dados Carta Benefício Extraídos:")
            st.dataframe(df_carta)

            file_output = exportar_df(df_carta, "Carta_Beneficio_Extraida", output_format)
            st.success(f"✅ Exportação Carta concluída! Arquivo gerado: {file_output}")
            with open(file_output, 'rb') as f:
                st.download_button("⬇️ Baixar Arquivo Carta", data=f, file_name=file_output, mime='application/octet-stream')

# ===================== FEEDBACK =====================

if uploaded_cnis_txt is None and uploaded_carta_txt is None:
    st.info("👆 Faça o upload de um arquivo CNIS e/ou Carta Benefício em formato TXT para iniciar o processamento.")
