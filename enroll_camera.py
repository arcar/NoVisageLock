import cv2
import os
import numpy as np
import insightface
import time


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


OWNER_DIR = os.path.join(
    BASE_DIR,
    "embeddings"
)


OWNER_FILE = os.path.join(
    OWNER_DIR,
    "owner.npy"
)



os.makedirs(
    OWNER_DIR,
    exist_ok=True
)



print("Initialisation caméra...")


model = insightface.app.FaceAnalysis(
    name="buffalo_l",
    providers=[
        "CPUExecutionProvider"
    ]
)


model.prepare(
    ctx_id=0,
    det_size=(640,640)
)



cap = cv2.VideoCapture(0)


print(
    "Regardez la caméra..."
)


samples = []



while True:


    ret, frame = cap.read()


    if not ret:
        continue



    faces = model.get(
        frame
    )


    for face in faces:


        emb = face.embedding


        emb /= np.linalg.norm(
            emb
        )


        samples.append(
            emb
        )


        print(
            f"Capture {len(samples)}/20"
        )



        x1,y1,x2,y2 = (
            face.bbox.astype(int)
        )


        cv2.rectangle(
            frame,
            (x1,y1),
            (x2,y2),
            (0,255,0),
            2
        )



    cv2.imshow(
        "Enregistrement propriétaire",
        frame
    )


    if cv2.waitKey(1)==27:

        break



    if len(samples)>=20:

        break



    time.sleep(
        0.1
    )



cap.release()

cv2.destroyAllWindows()



if len(samples)<5:

    print(
        "Pas assez de données"
    )

    exit()



# moyenne des embeddings

owner = np.mean(
    samples,
    axis=0
)


owner /= np.linalg.norm(
    owner
)



np.save(
    OWNER_FILE,
    owner
)



print(
    "✅ Profil propriétaire enregistré"
)

print(
    OWNER_FILE
)