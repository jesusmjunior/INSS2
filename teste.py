import streamlit as st
import pandas as pd
import numpy as np
import json
import re
from io import StringIO

# ================================
# CONFIGURAÇÃO INICIAL PRIMEIRA LINHA
# ================================
st.set_page_config(page_title="Jesus e INSS | Sistema Completo", layout="wide")

# ================================
# LOGIN SIMPLES
# ================================
def login():
    st.title("🔐 Área Protegida - Login Obrigatório")
    user = st.text_input("Usuário (Email)")
    password = st.text_input("Senha", type="password")

    if user == "jesusmjunior2021@gmail.com" and password == "jr010507":
        st.success("Login efetuado com sucesso ✅")
        return True
    else:
        if user and password:
            st.error("Usuário ou senha incorretos ❌")
        st.stop()  # Para bloquear acesso caso não logado

# ================================
# EXECUTA LOGIN
# ================================
login()

# ================================
# FUNÇÕES DE LEITURA E ESTRUTURAÇÃO =====================

def ler_texto(uploaded_file):
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8", errors='ignore'))
    texto = stringio.read()
    return texto


def estrutura_cnis(texto):
    linhas = texto.split('\n')
    data = []
    for line in linhas:
        match = re.search(r"(\d{2}/\d{4})\s+([0-9.]+,[0-9]{2})", line)
        if match:
            competencia = match.group(1)
            remuneracao = match.group(2).replace('.', '').replace(',', '.')
            data.append({'Competência': competencia, 'Remuneração': remuneracao, 'Origem': 'CNIS'})
    return pd.DataFrame(data)


def estrutura_carta(texto):
    linhas = texto.split('\n')
    data = []
    for line in linhas:
        match = re.match(r"^(\d{3})\s+(\d{2}/\d{4})\s+([0-9.,]+)\s+([0-9.,]+)\s+([0-9.,]+)(\s+.*)?", line)
        if match:
            seq = match.group(1)
            data_col = match.group(2)
            salario = match.group(3).replace('.', '').replace(',', '.')
            indice = match.group(4).replace(',', '.')
            sal_corrigido = match.group(5).replace('.', '').replace(',', '.')
            observacao = match.group(6).strip() if match.group(6) else ""
            data.append({
                'Seq.': seq,
                'Data': data_col,
                'Salário': salario,
                'Índice': indice,
                'Sal. Corrigido': sal_corrigido,
                'Observação': observacao,
                'Origem': 'Carta Benefício'
            })
    return pd.DataFrame(data)


def exportar_csv(df, nome_base):
    df.to_csv(f"{nome_base}.csv", index=False)
    return f"{nome_base}.csv"


def organizar_cnis(file):
    df = pd.read_csv(file, delimiter=';', encoding='utf-8')
    df = df.iloc[:,0].str.split(',', expand=True)
    df.columns = ['Seq', 'Competência', 'Remuneração', 'Ano']
    df['Remuneração'] = pd.to_numeric(df['Remuneração'], errors='coerce')
    df = df[df['Remuneração'] < 50000]  # Remove discrepantes - fuzzy
    return df

def organizar_desconsiderados(file):
    df = pd.read_csv(file, delimiter=';', encoding='utf-8')
    df = df.iloc[:,0].str.split(',', expand=True)
    df.columns = ['Seq', 'Seq.', 'Data', 'Salário', 'Índice', 'Sal. Corrigido', 'Observação', 'Ano', 'Duplicado']
    df['Sal. Corrigido'] = pd.to_numeric(df['Sal. Corrigido'], errors='coerce')
    return df

def fator_previdenciario(Tc, Es, Id, a=0.31):
    fator = (Tc * a / Es) * (1 + ((Id + Tc * a) / 100))
    return round(fator, 4)

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# ================================
# UPLOAD
# ================================
st.sidebar.header("🔽 Upload dos Arquivos")
cnis_file = st.sidebar.file_uploader("Upload - CNIS", type=["csv"])
carta_file = st.sidebar.file_uploader("Upload - Carta", type=["csv"])
desconsid_file = st.sidebar.file_uploader("Upload - Desconsiderados", type=["csv"])

aba = st.sidebar.radio("Navegação", ["Dashboard", "Gráficos", "Explicação", "Simulador", "Relatório", "Atualização Monetária", "Salários Desconsiderados"])

# ================================
# PROCESSAMENTO PRINCIPAL
# ================================
if cnis_file and carta_file and desconsid_file:
    # Processamento de CNIS e Carta
    df_cnis = organizar_cnis(cnis_file)
    df_desconsiderados = organizar_desconsiderados(desconsid_file)

    # 80% Maiores Salários
    df_cnis_sorted = df_cnis.sort_values(by='Remuneração', ascending=False)
    qtd_80 = int(len(df_cnis_sorted) * 0.8)
    df_top80 = df_cnis_sorted.head(qtd_80)
    df_bottom10 = df_cnis_sorted.tail(len(df_cnis_sorted) - qtd_80)

    # Desconsiderados Vantajosos
    min_80 = df_top80['Remuneração'].min()
    df_vantajosos = df_desconsiderados[df_desconsiderados['Sal. Corrigido'] > min_80]

    # Parâmetros default
    Tc_default, Es_default, Id_default, a_default = 38, 21.8, 60, 0.31
    media_salarios = df_top80['Remuneração'].mean()
    fator = fator_previdenciario(Tc_default, Es_default, Id_default, a_default)
    salario_beneficio = round(media_salarios * fator, 2)

    # Formatação de Moeda
    df_top80['Remuneração'] = df_top80['Remuneração'].apply(formatar_moeda)
    df_vantajosos['Sal. Corrigido'] = df_vantajosos['Sal. Corrigido'].apply(formatar_moeda)

    # ================================
    # TAREFA 1 - Salários Desconsiderados
    # ================================
    df_desconsiderados_cnis = df_cnis[df_cnis['Remuneração'].astype(float) < 1000]  # Filtrando salários desconsiderados CNIS
    df_desconsiderados_carta = df_vantajosos[df_vantajosos['Sal. Corrigido'].astype(float) < 1000]  # Filtrando salários desconsiderados Carta

    df_desconsiderados = pd.concat([df_desconsiderados_cnis, df_desconsiderados_carta], ignore_index=True)

    file_output_desconsiderados = exportar_csv(df_desconsiderados, "Salarios_Desconsiderados")
    st.dataframe(df_desconsiderados, use_container_width=True)
    st.download_button("⬇️ Baixar Salários Desconsiderados CSV", data=open(file_output_desconsiderados, 'rb'), file_name=file_output_desconsiderados, mime='text/csv')

    # ================================
    # ATUALIZAÇÃO MONETÁRIA
    # ================================
    if aba == "Atualização Monetária":
        st.title("💰 Atualização Monetária por Período Econômico")
        st.markdown("Aplique atualização monetária em cascata com índices ajustáveis para planos econômicos.")
        # Continuação de implementação dos índices para atualização monetária...

else:
    st.info("🔔 Faça upload dos arquivos obrigatórios para liberar o dashboard.")
