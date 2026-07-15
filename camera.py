import cv2
import time
import logging
import threading


class CameraManager:


    def __init__(self, camera_id=0):

        self.camera_id = camera_id

        self.cap = None

        self.lock = threading.Lock()



    # =================================================

    def open(self):

        with self.lock:


            self.close()


            logging.info(
                "Ouverture webcam"
            )


            self.cap = cv2.VideoCapture(
                self.camera_id,
                cv2.CAP_DSHOW
            )


            if not self.cap.isOpened():


                logging.error(
                    "Webcam impossible à ouvrir"
                )


                self.cap = None

                return False



            self.cap.set(
                cv2.CAP_PROP_BUFFERSIZE,
                1
            )


            logging.info(
                "Webcam opérationnelle"
            )


            return True



    # =================================================

    def read(self):


        with self.lock:


            if self.cap is None:

                return False, None


            return self.cap.read()



    # =================================================

    def close(self):


        if self.cap:


            logging.info(
                "Fermeture webcam"
            )


            self.cap.release()


            self.cap = None



    # =================================================

    def restart(self):


        logging.info(
            "Redémarrage webcam"
        )


        self.close()


        time.sleep(2)


        return self.open()



    # =================================================

    def suspend(self):


        logging.info(
            "Suspension webcam"
        )


        self.close()



    # =================================================

    def resume(self):


        logging.info(
            "Réactivation webcam"
        )


        time.sleep(3)


        self.open()