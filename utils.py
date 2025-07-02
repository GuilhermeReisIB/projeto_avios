from PIL import Image, ImageOps
import streamlit as st

def exibir_imagem(path_img: str, cor_borda="#999999", largura_borda=4):
    try:
        imagem = Image.open(path_img).convert("RGB")
        imagem_com_borda = ImageOps.expand(imagem, border=largura_borda, fill=cor_borda)
        st.image(imagem_com_borda, width=300)
    except Exception as e:
        st.warning(f"Erro ao carregar imagem: {e}")