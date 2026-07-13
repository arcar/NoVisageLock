import insightface
import cv2
import numpy as np
import os


MODEL_DIR = "models"

IMAGE = "faces/proprietaire.jpg"

OUTPUT = "embeddings/owner.npy"



os.makedirs(
    "embeddings",
    exist_ok=True
)



app = insightface.app.FaceAnalysis(
    name="buffalo_l",
    providers=[
        "CPUExecutionProvider"
    ]
)


app.prepare(
    ctx_id=0,
    det_size=(640,640)
)



img = cv2.imread(
    IMAGE
)



faces = app.get(
    img
)



if len(faces)==0:

    raise Exception(
        "Aucun visage détecté"
    )



face = faces[0]



embedding = face.embedding



# Normalisation

embedding = embedding / np.linalg.norm(
    embedding
)



np.save(
    OUTPUT,
    embedding
)



print(
    "✅ Profil propriétaire créé"
)