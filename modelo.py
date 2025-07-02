import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from transformers import ViTModel, ViTImageProcessor
from PIL import Image
import torch
import numpy as np

# Carrega modelo e processor uma única vez
processor = ViTImageProcessor.from_pretrained("google/vit-base-patch16-224-in21k")
model = ViTModel.from_pretrained("google/vit-base-patch16-224-in21k")
model.eval()

def extrair_vetor(imagem: Image.Image) -> np.ndarray:
    inputs = processor(images=imagem, return_tensors="pt")
    with torch.no_grad():
        inputs = {k: v.to("cpu") for k, v in inputs.items()}
        outputs = model(**inputs)
    vetor = outputs.last_hidden_state[:, 0].squeeze().numpy()
    return vetor / np.linalg.norm(vetor)
