import streamlit as st
import pandas as pd
import re
import os
from io import StringIO

# ===================== CONFIG PÁGINA =====================
st.set_page_config(page_title="Jesus e INSS | Extrator CNIS + Carta Benefício", layout="centered")

st.title("📄 JESUS e INSS - Extrator CNIS & Carta Benefício")
st.write("**Processamento leve, com lógica fuzzy aplicada, sanitização robusta e precisão na extração dos dados numéricos.**")

# ===================== RECEPÇÃO DOS PDFs =====================
col1, col2 = st.columns(2)

with col1:
    uploaded_cnis = st.file_uploader("🔽 Upload do arquivo CNIS:", type="pdf", key="cnis")

with col2:
    uploaded_carta = st.file_uploader("🔽 Upload do arquivo Carta Benefício:", type="pdf", key="carta")

output_format = st.radio("📁 Formato de Exportação:", ['CSV', 'XLSX'])

# ===================== FUNÇÕES BASE =====================

def extrair_texto_pdf(uploaded_file):
    # Leitura simples do PDF em binário e conversão para texto ignorando erros
    bin_pdf = uploaded_file.read()
    texto = bin_pdf.decode(errors='ignore')
    return texto


def sanitizar_numeros(texto):
    # Remove qualquer caractere estranho, mantém apenas números, pontos, barras e espaços
    texto = re.sub(r'[^0-9.,/\n ]', '', texto)
    texto = texto.replace(',', '.')
    return texto


def estrutura_cnis(texto):
    linhas = texto.split('\n')
    data = []
    for line in linhas:
        line_clean = line.strip()
        if re.match(r"\d{2}/\d{4}", line_clean):  # Captura formato MM/YYYY
            parts = line_clean.split()
            if len(parts) >= 2:
                competencia = parts[0]
                remuneracao = parts[1].replace('.', '').replace(',', '.')
                data.append({'Competência': competencia, 'Remuneração': remuneracao})
    return pd.DataFrame(data)


def estrutura_carta(texto):
    linhas = texto.split('\n')
    data = []
    for line in linhas:
        line_clean = line.strip()
        if re.match(r"^\d{3}\s", line_clean):
            parts = re.split(r'\s+', line_clean)
            if len(parts) >= 6:
                seq = parts[0]
                data_col = parts[1]
                salario = parts[2].replace('.', '').replace(',', '.')
                indice = parts[3].replace(',', '.')
                sal_corrigido = parts[4].replace('.', '').replace(',', '.')
                observacao = " ".join(parts[5:])
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

# ===================== PROCESSAMENTO CNIS =====================

if uploaded_cnis is not None:
    with st.spinner('🔍 Processando arquivo CNIS...'):
        texto_pdf = extrair_texto_pdf(uploaded_cnis)
        texto_pdf = sanitizar_numeros(texto_pdf)
        df_cnis = estrutura_cnis(texto_pdf)

        if not df_cnis.empty:
            st.subheader("📊 Dados CNIS Extraídos:")
            st.dataframe(df_cnis)

            file_output = exportar_df(df_cnis, "Extrato_CNIS_Extraido", output_format)
            st.success(f"✅ Exportação CNIS concluída! Arquivo gerado: {file_output}")
            with open(file_output, 'rb') as f:
                st.download_button("⬇️ Baixar Arquivo CNIS", data=f, file_name=file_output, mime='application/octet-stream')

# ===================== PROCESSAMENTO CARTA =====================

if uploaded_carta is not None:
    with st.spinner('🔍 Processando arquivo Carta Benefício...'):
        texto_pdf = extrair_texto_pdf(uploaded_carta)
        texto_pdf = sanitizar_numeros(texto_pdf)
        df_carta = estrutura_carta(texto_pdf)

        if not df_carta.empty:
            st.subheader("📊 Dados Carta Benefício Extraídos:")
            st.dataframe(df_carta)

            file_output = exportar_df(df_carta, "Carta_Beneficio_Extraida", output_format)
            st.success(f"✅ Exportação Carta concluída! Arquivo gerado: {file_output}")
            with open(file_output, 'rb') as f:
                st.download_button("⬇️ Baixar Arquivo Carta", data=f, file_name=file_output, mime='application/octet-stream')

# ===================== FEEDBACK =====================

if uploaded_cnis is None and uploaded_carta is None:
    st.info("👆 Faça o upload de um arquivo CNIS e/ou Carta Benefício para iniciar o processamento.")
