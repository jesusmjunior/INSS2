import streamlit as st
import pandas as pd
import re
import os

# ===================== CONFIG PÁGINA =====================
st.set_page_config(page_title="Jesus e INSS | Extrator CNIS + Carta Benefício", layout="centered")

st.title("📄 JESUS e INSS - Extrator CNIS & Carta Benefício")
st.write("**Processamento leve, com lógica fuzzy aplicada e sanitização de dados numéricos.**")

uploaded_file = st.file_uploader("🔽 Faça o upload do arquivo PDF (CNIS ou Carta Benefício):", type="pdf")
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

def inferir_documento(binario_pdf):
    texto = binario_pdf.decode(errors='ignore')
    if "Seq." in texto or "Índice" in texto:
        pertinencia = dicionario_fuzzy['β (Beta)']['peso']
        return "Carta Benefício", texto, pertinencia
    elif "Competência" in texto or "/" in texto:
        pertinencia = dicionario_fuzzy['α (Alfa)']['peso']
        return "Extrato CNIS", texto, pertinencia
    else:
        pertinencia = dicionario_fuzzy['γ (Gama)']['peso']
        return "Desconhecido", texto, pertinencia


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

# ===================== EXECUÇÃO PRINCIPAL =====================

if uploaded_file is not None:
    with st.spinner('🔍 Analisando e sanitizando com lógica fuzzy...'):
        bin_pdf = uploaded_file.read()
        tipo_doc, texto_pdf, peso_pertinencia = inferir_documento(bin_pdf)

        st.info(f"🔎 Peso de Pertinência Detectado: {peso_pertinencia}")

        texto_pdf = sanitizar_numeros(texto_pdf)

        if tipo_doc == "Carta Benefício":
            st.success("📑 Documento identificado como **Carta de Benefício**.")
            df_final = estrutura_carta(texto_pdf)
            nome_output = "Carta_Beneficio_Extraida"
        elif tipo_doc == "Extrato CNIS":
            st.warning("📝 Documento identificado como **Extrato CNIS**.")
            df_final = estrutura_cnis(texto_pdf)
            nome_output = "Extrato_CNIS_Extraido"
        else:
            st.error("❌ Documento não identificado claramente (peso crítico).")
            df_final = None

        if df_final is not None and not df_final.empty:
            st.subheader("📊 Dados Extraídos:")
            st.dataframe(df_final)

            file_output = exportar_df(df_final, nome_output, output_format)
            st.success(f"✅ Exportação concluída! Arquivo gerado: {file_output}")
            with open(file_output, 'rb') as f:
                st.download_button("⬇️ Baixar Arquivo", data=f, file_name=file_output, mime='application/octet-stream')

            bloco_usado = [key for key, val in dicionario_fuzzy.items() if val['peso'] == peso_pertinencia]
            st.info(f"🔗 Bloco Lógico Aplicado: {bloco_usado[0]} - {dicionario_fuzzy[bloco_usado[0]]['ação']}")

            st.divider()
            st.info("Deseja integrar com Google Sheets ou API? 🚀 (Futuro recurso)")
            st.info("Deseja validar dados fuzzy ou processar um novo documento?")
else:
    st.info("👆 Faça o upload de um arquivo PDF para iniciar o processamento.")
