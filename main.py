import cv2
import os
import sys
import time
import json
import logging
import threading
import subprocess
import platform
import warnings

import numpy as np
import insightface

from filelock import FileLock, Timeout
from tray import TrayIcon


warnings.filterwarnings(
    "ignore",
    category=FutureWarning
)


# =====================================================
# CHEMINS
# =====================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


CONFIG_FILE = os.path.join(
    BASE_DIR,
    "config.json"
)


OWNER_FILE = os.path.join(
    BASE_DIR,
    "embeddings",
    "owner.npy"
)


LOCK_FILE = os.path.join(
    BASE_DIR,
    "NoVisageLock.lock"
)


LOG_FILE = os.path.join(
    BASE_DIR,
    "novisagelock.log"
)



# =====================================================
# LOG
# =====================================================

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)



# =====================================================
# CONFIG
# =====================================================

with open(
    CONFIG_FILE,
    "r",
    encoding="utf8"
) as f:

    CONFIG = json.load(f)



# =====================================================
# ENROLL
# =====================================================

def launch_enroll():


    logging.info(
        "Lancement enrôlement"
    )


    subprocess.run(
        [
            sys.executable,
            os.path.join(
                BASE_DIR,
                "enroll_camera.py"
            )
        ]
    )



def check_owner():


    if os.path.exists(
        OWNER_FILE
    ):

        return True



    launch_enroll()



    return os.path.exists(
        OWNER_FILE
    )



# =====================================================
# IA
# =====================================================

class FaceIdentifier:


    def __init__(self):


        self.owner = np.load(
            OWNER_FILE
        )


        self.owner /= np.linalg.norm(
            self.owner
        )



        self.model = insightface.app.FaceAnalysis(
            name="buffalo_l",
            providers=[
                "CPUExecutionProvider"
            ]
        )


        self.model.prepare(
            ctx_id=0,
            det_size=(640,640)
        )


        logging.info(
            "InsightFace prêt"
        )



    def recognize(self, frame):


        results = []


        faces = self.model.get(
            frame
        )


        for face in faces:


            emb = face.embedding


            emb /= np.linalg.norm(
                emb
            )


            score = float(
                np.dot(
                    self.owner,
                    emb
                )
            )


            results.append(
                {
                    "owner":
                    score >= CONFIG["owner_threshold"],

                    "score":
                    score,

                    "face":
                    face
                }
            )


        return results



# =====================================================
# APPLICATION
# =====================================================

class NoVisageLock:


    def __init__(self):


        logging.info(
            "Démarrage"
        )


        self.running = True

        self.paused = False

        self.show_preview = False



        if not check_owner():

            raise Exception(
                "Enrôlement impossible"
            )



        self.identifier = FaceIdentifier()



        self.cap = cv2.VideoCapture(
            CONFIG["camera"]
        )


        if not self.cap.isOpened():

            raise Exception(
                "Webcam inaccessible"
            )



        self.last_owner_seen = time.time()



        self.tray = TrayIcon(
            self
        )


        threading.Thread(
            target=self.tray.start,
            daemon=True
        ).start()



        logging.info(
            "Surveillance active"
        )



    # -------------------------------------------------

    def lock_windows(self):


        logging.info(
            "Verrouillage Windows"
        )


        if platform.system() == "Windows":


            subprocess.run(
                [
                    "rundll32.exe",
                    "user32.dll",
                    "LockWorkStation"
                ]
            )



    # -------------------------------------------------

    def change_owner(self):


        if os.path.exists(
            OWNER_FILE
        ):

            os.remove(
                OWNER_FILE
            )


        launch_enroll()



        logging.info(
            "Nouveau propriétaire"
        )



        self.identifier = FaceIdentifier()



    # -------------------------------------------------

    def run(self):


        frame_count = 0



        while self.running:



            if self.paused:

                time.sleep(1)

                continue



            ret, frame = self.cap.read()


            if not ret:

                time.sleep(1)

                continue



            frame_count += 1


            owner_found = False



            if frame_count % CONFIG["frame_skip"] == 0:


                results = self.identifier.recognize(
                    frame
                )



                for item in results:


                    if item["owner"]:

                        owner_found = True



                    if self.show_preview:


                        face = item["face"]


                        x1,y1,x2,y2 = (
                            face.bbox.astype(int)
                        )


                        cv2.rectangle(
                            frame,
                            (x1,y1),
                            (x2,y2),
                            (0,255,0)
                            if item["owner"]
                            else
                            (0,0,255),
                            2
                        )


                        cv2.putText(
                            frame,
                            f"{item['score']:.2f}",
                            (x1,y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (255,255,255),
                            2
                        )



            if owner_found:


                self.last_owner_seen = time.time()



            absence = (
                time.time()
                -
                self.last_owner_seen
            )



            if self.show_preview:


                cv2.imshow(
                    "NoVisageLock",
                    frame
                )

                cv2.waitKey(1)



            else:

                cv2.destroyAllWindows()



            if absence >= CONFIG["absence_timeout"]:


                self.lock_windows()


                # important :
                # le programme continue après verrouillage

                self.last_owner_seen = time.time()



                time.sleep(5)



            time.sleep(
                0.05
            )



    # -------------------------------------------------

    def close(self):


        self.running=False


        self.cap.release()


        cv2.destroyAllWindows()



# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":


    lock = FileLock(
        LOCK_FILE
    )


    try:


        with lock:


            app = NoVisageLock()

            app.run()



    except Timeout:


        pass



    except Exception as e:


        logging.exception(
            e
        )