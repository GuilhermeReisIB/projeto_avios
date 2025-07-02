import numpy as np
import pandas as pd
import faiss
from modelo import extrair_vetor
from sentence_transformers import SentenceTransformer
from PIL import Image
import streamlit as st

import requests
from io import BytesIO


# Carrega dados e modelo
df = pd.read_csv("data/df_materiais_amostra_2025_07_02.csv")
index = faiss.read_index("data/index_completo.faiss")
df_metadados = pd.read_csv("data/metadados_completo.csv")
modelo_texto = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def buscar_similares_hibrido(material: str, cor: str, top_k=20):
    
    # Filtra o registro
    filtro = df.query(""" material.str.upper() == '{}' and cor_material.str.upper() == '{}'  """.format(material.upper(), cor.upper()))

    ## CRIA A URL PARA S3
    filtro["url"] = (
        "https://inbrands-streamlit.s3.us-east-2.amazonaws.com/media/aviamentos/" +
        filtro["material"].astype(str).str.strip().str.lower() + "_" +
        filtro["cor_material"].astype(str).str.strip().str.lower() + ".jpg"
    )

    # url = "https://inbrands-streamlit.s3.us-east-2.amazonaws.com/media/aviamentos/{}_{}.jpg".format(material.strip().lower(), cor.strip().lower() )
    # st.write(url)

    if filtro.empty:
        return []

    row = filtro.iloc[0]
    path_img = row["url"]

    try:
        response = requests.get(path_img)
        # st.write(f"Tentando acessar: {path_img}")
        # st.write(f"Status da resposta: {response.status_code}")
        response.raise_for_status()  # Lança exceção se status != 200
        imagem = Image.open(BytesIO(response.content)).convert("RGB")
    except Exception as e:
        # st.write(f"Erro ao abrir imagem: {e}")
        return []

    # Vetor de imagem (ViT)
    vetor_img = extrair_vetor(imagem)


    # Vetor de texto
    texto = f"{row['grupo']} | {row['subgrupo']} | {row['categoria_produto']}"
    vetor_txt = modelo_texto.encode(texto, normalize_embeddings=True)

    # Vetor final
    vetor_final = np.concatenate([vetor_txt, vetor_img]).reshape(1, -1)

    # Consulta FAISS
    D, I = index.search(vetor_final, top_k)
    resultados = df_metadados.iloc[I[0]].copy()
    resultados["distancia"] = D[0]
    # resultados["url"] = path_img  # adiciona a URL usada como base
    # Adiciona a URL correta para cada linha
    resultados["url"] = (
        "https://inbrands-streamlit.s3.us-east-2.amazonaws.com/media/aviamentos/" +
        resultados["material"].astype(str).str.strip().str.lower() + "_" +
        resultados["cor_material"].astype(str).str.strip().str.lower() + ".jpg"
    )

    return resultados.to_dict(orient="records")


