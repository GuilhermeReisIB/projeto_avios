from PIL import Image, ImageOps
import streamlit as st
from io import BytesIO
import requests

def exibir_imagem(path_img: str, cor_borda="#999999", largura_borda=4):
    try:
        imagem = Image.open(path_img).convert("RGB")
        imagem_com_borda = ImageOps.expand(imagem, border=largura_borda, fill=cor_borda)
        st.image(imagem_com_borda, width=300)
    except Exception as e:
        st.warning(f"Erro ao carregar imagem: {e}")


def exibir_imagem(path_img: str, cor_borda="#999999", largura_borda=4):
    try:
        if path_img.startswith("http"):
            response = requests.get(path_img)
            response.raise_for_status()
            imagem = Image.open(BytesIO(response.content)).convert("RGB")
        else:
            imagem = Image.open(path_img).convert("RGB")

        imagem_com_borda = ImageOps.expand(imagem, border=largura_borda, fill=cor_borda)
        st.image(imagem_com_borda, width=300)
    except Exception as e:
        st.warning(f"Erro ao carregar imagem: {e}")
