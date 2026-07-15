import os
import sys
import time
import json
import logging
import threading
import subprocess
import platform
import warnings
import ctypes


import cv2
import numpy as np
import insightface


from tray import TrayIcon
from camera import CameraManager
from windows_events import WindowsEvents



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

    format="%(asctime)s - %(levelname)s - %(message)s",

    force=True

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
# MUTEX WINDOWS
# =====================================================

mutex_handle = None


def already_running():


    global mutex_handle


    if platform.system() != "Windows":

        return False



    mutex_handle = ctypes.windll.kernel32.CreateMutexW(

        None,

        False,

        "NoVisageLock_Instance"

    )


    error = ctypes.windll.kernel32.GetLastError()



    if error == 183:

        return True



    return False





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
# IA RECONNAISSANCE
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





    def recognize(
        self,
        frame
    ):


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
            "Démarrage NoVisageLock"
        )



        self.running = True


        self.security_state = "NORMAL"


        self.verify_start = None



        self.show_preview = False


        self.paused = False



        if not check_owner():


            raise Exception(
                "Profil propriétaire absent"
            )



        self.identifier = FaceIdentifier()



        # -----------------------------
        # CAMERA
        # -----------------------------

        self.camera = CameraManager(

            CONFIG["camera"]

        )



        if not self.camera.open():


            raise Exception(
                "Caméra inaccessible"
            )



        self.last_owner_seen = time.time()



        # -----------------------------
        # EVENTS WINDOWS
        # -----------------------------

        self.events = WindowsEvents(

            self.windows_event

        )


        self.events.start()



        # -----------------------------
        # TRAY
        # -----------------------------

        self.tray = TrayIcon(
            self
        )



        self.tray_thread = threading.Thread(

            target=self.tray.start,

            daemon=True

        )


        self.tray_thread.start()



        logging.info(
            "Surveillance active"
        )
    # =====================================================
    # EVENEMENTS WINDOWS
    # =====================================================

    def windows_event(
        self,
        event
    ):


        logging.info(
            f"EVENT WINDOWS : {event}"
        )


        # -------------------------
        # Mise en veille
        # -------------------------

        if event == "SUSPEND":


            logging.info(
                "Mise en veille : fermeture caméra"
            )


            self.camera.suspend()



        # -------------------------
        # Réveil
        # -------------------------

        elif event == "RESUME":


            logging.info(
                "Réveil Windows"
            )


            time.sleep(3)


            self.camera.resume()



        # -------------------------
        # Verrouillage session
        # -------------------------

        elif event == "LOCK":


            logging.info(
                "Session verrouillée"
            )


            self.camera.close()



        # -------------------------
        # Déverrouillage session
        # -------------------------

        elif event == "UNLOCK":


            logging.info(
                "Session déverrouillée"
            )


            time.sleep(2)


            self.camera.restart()



            self.security_state = "VERIFY_OWNER"


            self.verify_start = time.time()



            logging.info(
                "Mode VERIFY_OWNER activé"
            )



    # =====================================================
    # VERROUILLAGE WINDOWS
    # =====================================================

    def lock_windows(self):


        logging.warning(
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



    # =====================================================
    # CHANGEMENT PROPRIETAIRE
    # =====================================================

    def change_owner(self):


        logging.info(
            "Changement propriétaire"
        )


        if os.path.exists(
            OWNER_FILE
        ):


            os.remove(
                OWNER_FILE
            )



        launch_enroll()



        self.identifier = FaceIdentifier()



        logging.info(
            "Nouveau propriétaire enregistré"
        )



    # =====================================================
    # BOUCLE PRINCIPALE
    # =====================================================

    def run(self):


        logging.info(
            "Boucle surveillance démarrée"
        )


        frame_count = 0



        while self.running:



            if self.paused:


                time.sleep(1)

                continue



            ret, frame = self.camera.read()



            if not ret:


                logging.warning(
                    "Lecture caméra impossible"
                )


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



            # =================================================
            # MODE VERIFICATION PROPRIETAIRE
            # =================================================

            if self.security_state == "VERIFY_OWNER":



                logging.info(

                    f"VERIFY_OWNER actif : visage={owner_found}"

                )



                if owner_found:


                    logging.info(

                        "Propriétaire confirmé après reconnexion"

                    )


                    self.security_state = "NORMAL"


                    self.last_owner_seen = time.time()



                elif (

                    time.time()

                    -

                    self.verify_start

                ) > CONFIG["verify_timeout"]:



                    logging.warning(

                        "Propriétaire non confirmé"

                    )


                    self.security_state = "NORMAL"


                    self.lock_windows()



            # =================================================
            # MODE NORMAL
            # =================================================

            else:



                if owner_found:


                    self.last_owner_seen = time.time()



                absence = (

                    time.time()

                    -

                    self.last_owner_seen

                )



                if absence >= CONFIG["absence_timeout"]:



                    self.lock_windows()



                    self.last_owner_seen = time.time()



            # -------------------------------------------------

            if self.show_preview:


                cv2.imshow(

                    "NoVisageLock",

                    frame

                )


                cv2.waitKey(1)



            else:


                cv2.destroyAllWindows()



            time.sleep(
                0.05
            )



    # =====================================================
    # FERMETURE PROPRE
    # =====================================================

    def close(self):


        logging.info(
            "Arrêt NoVisageLock"
        )


        self.running = False



        try:


            self.camera.close()



        except Exception:


            logging.exception(
                "Erreur fermeture caméra"
            )



        try:


            self.events.stop()



        except Exception:


            logging.exception(
                "Erreur arrêt événements Windows"
            )



        try:


            cv2.destroyAllWindows()



        except Exception:


            pass





# =====================================================
# MAIN
# =====================================================

def main():



    if already_running():


        logging.warning(

            "Instance NoVisageLock déjà active"

        )


        return



    app = None



    try:


        app = NoVisageLock()


        app.run()



    except KeyboardInterrupt:


        logging.info(
            "Arrêt manuel"
        )



    except Exception as e:


        logging.exception(
            e
        )



    finally:


        if app:


            app.close()





if __name__ == "__main__":


    main()