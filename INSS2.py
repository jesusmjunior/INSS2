import streamlit as st
import pandas as pd
import PyPDF2
import os

st.set_page_config(page_title="Jesus e INSS | Extrator CNIS + Carta Benefício", layout="centered")

st.title("📄 JESUS E INSS - Extrator CNIS & Carta Benefício")
st.write("**Processamento leve com inferência fuzzy e exportação em CSV/XLSX**")

# --------------- CONFIGURAÇÕES INICIAIS --------------------
uploaded_file = st.file_uploader("🔽 Faça o upload do arquivo PDF (CNIS ou Carta Benefício):", type="pdf")
output_format = st.radio("📁 Formato de Exportação:", ['CSV', 'XLSX'])

# ------------------ FUNÇÕES BASE --------------------------

def extrair_texto_pdf(pdf_path):
    texto = ""
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            texto += page.extract_text()
    return texto

def inferir_documento(texto):
    if "Seq." in texto or "Índice" in texto:
        return "Carta Benefício"
    elif "Competência" in texto or "/" in texto:
        return "Extrato CNIS"
    else:
        return "Desconhecido"

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

# ------------------ EXECUÇÃO PRINCIPAL --------------------

if uploaded_file is not None:
    with st.spinner('🔍 Verificando e processando o PDF...'):
        temp_pdf_path = f"temp_{uploaded_file.name}"
        with open(temp_pdf_path, "wb") as f:
            f.write(uploaded_file.read())

        texto_pdf = extrair_texto_pdf(temp_pdf_path)
        tipo_doc = inferir_documento(texto_pdf)

        if tipo_doc == "Carta Benefício":
            st.success("📑 Documento identificado como **Carta de Benefício** (inferência fuzzy).")
            df_final = estrutura_carta(texto_pdf)
            nome_output = "Carta_Beneficio_Extraida"
        elif tipo_doc == "Extrato CNIS":
            st.warning("📝 Documento identificado como **Extrato CNIS** (inferência fuzzy).")
            df_final = estrutura_cnis(texto_pdf)
            nome_output = "Extrato_CNIS_Extraido"
        else:
            st.error("❌ Documento não identificado claramente.")
            df_final = None

        if df_final is not None and not df_final.empty:
            st.subheader("📊 Dados Extraídos:")
            st.dataframe(df_final)

            file_output = exportar_df(df_final, nome_output, output_format)
            st.success(f"✅ Exportação concluída! Arquivo gerado: {file_output}")
            with open(file_output, 'rb') as f:
                st.download_button("⬇️ Baixar Arquivo", data=f, file_name=file_output, mime='application/octet-stream')

            st.divider()
            st.info("Deseja integrar com Google Sheets ou API? 🚀 (Futuro recurso)")
            st.info("Deseja validar dados fuzzy ou processar um novo documento?")

        os.remove(temp_pdf_path)

else:
    st.info("👆 Faça o upload de um arquivo PDF para iniciar o processamento.")
