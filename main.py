import pandas as pd


import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=pd.errors.SettingWithCopyWarning)

import streamlit as st
from busca_hibrida import buscar_similares_hibrido
from utils import exibir_imagem
from PIL import Image
import ast

st.set_page_config(
        layout="wide", 
        page_title='Aviamentos',
        # initial_sidebar_state="collapsed"
    )


st.title("🔍 Busca Aviamentos")

with st.form(key="form_busca"):
    col1, col2 = st.columns(2)
    with col1:
        material = st.text_input("Código do Material")
    with col2:
        cor_material = st.text_input("Cor do Material")
    submitted = st.form_submit_button("Buscar Similares")

if submitted:
    if not material or not cor_material:
        st.warning("Preencha o material e a cor.")
    else:
        with st.spinner("Buscando similares..."):
            resultados = buscar_similares_hibrido(material, cor_material)

            if not resultados:
                st.warning('Não foi localizada imagem desse material')
                # st.error("Nenhum item encontrado ou erro ao carregar imagem.")

            else:
                ## Converte string para dicionário
                try:
                    lista_dicts = [ast.literal_eval(linha.strip()) for linha in resultados]
                except:
                    lista_dicts = resultados # [ast.literal_eval(linha.strip()) for linha in resultados]



                ## Cria uma query considerando a imagem de referência
                lista_atributos = []
                for a in lista_dicts[0].keys():
                    if a in ['grupo', 'categoria_produto']:
                        texto = f"{a} ==  '{lista_dicts[0][a]}' "
                        lista_atributos.append(texto)
                        query = ' and '.join(lista_atributos)

                ## Gera um DataFrame
                df_final = pd.DataFrame()
                for dicionario in lista_dicts:
                    df_temp = pd.DataFrame([dicionario])  # transforma em DataFrame de 1 linha
                    df_final = pd.concat([df_final, df_temp], ignore_index=True)            

                ## Filtra e organiza o resultado
                df_final_01 = (
                    df_final
                    .iloc[1:] ## retira o primeiro registro visto é a própria referência
                    .query("qtde_estoque > 0") ## considera apenas estoque superior a zero
                    .sort_values('qtde_estoque', ascending=False) ## classifica por volume de estoque
                    # .sort_values('distancia')
                    .query(query) ## filtra o mesmo grupo e categoria para não alucinar
                    .head(15)
                    .reset_index(drop=True)
                    )



                st.subheader("Material de Referência")
                exibir_imagem(resultados[0]['path_completo'])

                cols = st.columns(3)
                for idx, (i, r) in enumerate(df_final_01.iterrows()):
                    with cols[idx % 3]:
                        st.markdown(f"**{i+1}. Estoque:** {r['qtde_estoque']:,.0f}")
                        st.markdown(
                            f"Material: {r['material']} | Cor_material: {r['cor_material']}<br>"
                            f"Grupo: {r['grupo']} | Subgrupo: {r['subgrupo']} | Categoria: {r['categoria_produto']}",
                            unsafe_allow_html=True
                        )
                        exibir_imagem(r['path_completo'])