import streamlit as st
import pandas as pd
import os
import re

# ------------------- CONFIG -------------------
st.set_page_config(page_title="Jesus e INSS | Extrator CNIS Robust", layout="centered")

st.title("📄 JESUS e INSS - Extrator CNIS (Versão Robusta)")
st.write("**Leitura total, contagem de linhas e organização limpa dos dados**")

uploaded_file = st.file_uploader("🔽 Faça o upload do arquivo TXT do Extrato CNIS:", type="txt")
output_format = st.radio("📁 Formato de Exportação:", ['CSV', 'XLSX'])

# ------------------- FUNÇÕES -------------------

def contar_linhas(texto):
    linhas = texto.split('\n')
    return len(linhas), linhas

def extrair_remuneracoes(linhas):
    padrao = r"(\d{2}/\d{4})\s+([\d\.,]+)"
    data = []
    for linha in linhas:
        matches = re.findall(padrao, linha)
        for m in matches:
            competencia = m[0]
            remuneracao = m[1].replace(".", "").replace(",", ".")  # Corrige formato
            data.append({'Competência': competencia, 'Remuneração': remuneracao})
    return pd.DataFrame(data)

def exportar_df(df, nome_base, formato):
    if formato == 'CSV':
        df.to_csv(f"{nome_base}.csv", index=False)
        return f"{nome_base}.csv"
    else:
        df.to_excel(f"{nome_base}.xlsx", index=False)
        return f"{nome_base}.xlsx"

# ------------------- EXECUÇÃO PRINCIPAL -------------------

if uploaded_file is not None:
    with st.spinner('🔍 Lendo e processando todas as linhas...'):
        texto = uploaded_file.read().decode(errors='ignore')
        total_linhas, lista_linhas = contar_linhas(texto)
        st.info(f"📑 Total de linhas no arquivo: **{total_linhas} linhas**")

        df_remuneracoes = extrair_remuneracoes(lista_linhas)
        total_registros = len(df_remuneracoes)
        st.success(f"✅ Total de registros extraídos: **{total_registros} registros**")

        if not df_remuneracoes.empty:
            st.subheader("📊 Dados Organizados:")
            st.dataframe(df_remuneracoes)

            file_output = exportar_df(df_remuneracoes, "CNIS_Organizado", output_format)
            st.success(f"Arquivo exportado: {file_output}")
            with open(file_output, 'rb') as f:
                st.download_button("⬇️ Baixar Arquivo", data=f, file_name=file_output, mime='application/octet-stream')

            st.divider()
            st.info("Deseja processar um novo documento?")

        else:
            st.error("❌ Nenhum dado encontrado.")

else:
    st.info("👆 Faça o upload do arquivo TXT do Extrato CNIS para iniciar.")

