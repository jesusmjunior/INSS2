import streamlit as st
import pandas as pd
import re
import os

# ===================== CONFIG PÁGINA =====================
st.set_page_config(page_title="Jesus e INSS | Extrator CNIS + Carta Benefício", layout="centered")

st.title("📄 JESUS e INSS - Extrator CNIS & Carta Benefício")
st.write("**Processamento leve, com lógica fuzzy aplicada e sanitização de dados numéricos.**")

# ===================== RECEPÇÃO DOS PDFs =====================
col1, col2 = st.columns(2)

with col1:
    uploaded_cnis = st.file_uploader("🔽 Upload do arquivo CNIS:", type="pdf", key="cnis")

with col2:
    uploaded_carta = st.file_uploader("🔽 Upload do arquivo Carta Benefício:", type="pdf", key="carta")

output_format = st.radio("📁 Formato de Exportação:", ['CSV', 'XLSX'])

# ===================== DICIONÁRIO FUZZY =====================
dicionario_fuzzy = {
    'α (Alfa)': {'bloco': 'Organização de Variáveis', 'peso': 0.9, 'ação': 'Modularizar Variáveis'},
    'β (Beta)': {'bloco': 'Modularização de Regras', 'peso': 0.7, 'ação': 'Modularizar Regras'},
    'γ (Gama)': {'bloco': 'Correção de Falhas', 'peso': 1.0, 'ação': 'Correção Crítica'},
    'δ (Delta)': {'bloco': 'Boas Práticas e Refatoração', 'peso': 0.6, 'ação': 'Refatorar Código'},
    'ε (Epsilon)': {'bloco': 'Redução Estrutural', 'peso': 0.75, 'ação': 'Eliminar Redundâncias'},
    'θ (Theta)': {'bloco': 'Otimização Performance', 'peso': 0.95, 'ação': 'Otimizar Código'},
}

# ===================== FUNÇÕES BASE =====================

def sanitizar_numeros(texto):
    texto = re.sub(r'[^0-9,./\n ]', '', texto)
    texto = texto.replace(',', '.')
    return texto


def estrutura_cnis(texto):
    linhas = texto.split('\n')
    data = []
    for line in linhas:
        if '/' in line and any(char.isdigit() for char in line):
            parts = line.strip().split()
            if len(parts) >= 2:
                data.append({'Competência': parts[0], 'Remuneração': parts[1]})
    return pd.DataFrame(data)


def estrutura_carta(texto):
    linhas = texto.split('\n')
    data = []
    for line in linhas:
        if line.strip().startswith(tuple("0123456789")):
            parts = line.strip().split()
            if len(parts) >= 5:
                data.append({
                    'Seq.': parts[0],
                    'Data': parts[1],
                    'Salário': parts[2],
                    'Índice': parts[3],
                    'Sal. Corrigido': parts[4],
                    'Observação': " ".join(parts[5:]) if len(parts) > 5 else ""
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
        bin_pdf = uploaded_cnis.read()
        texto_pdf = bin_pdf.decode(errors='ignore')
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
        bin_pdf = uploaded_carta.read()
        texto_pdf = bin_pdf.decode(errors='ignore')
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
