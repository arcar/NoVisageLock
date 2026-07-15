# =====================================================
# windows_events.py
#
# Gestion événements Windows pour NoVisageLock
#
# Nécessite :
# pip install pywin32
#
# Compatible Python 3.12
# =====================================================

import threading
import logging
import time

import win32con
import win32gui
import win32api
import win32ts


# =====================================================
# CONSTANTES
# =====================================================

WM_POWERBROADCAST = 0x0218
WM_WTSSESSION_CHANGE = 0x02B1


PBT_APMSUSPEND = 0x0004
PBT_APMRESUMEAUTOMATIC = 0x0012
PBT_APMRESUMESUSPEND = 0x0007


WTS_SESSION_LOCK = 0x7
WTS_SESSION_UNLOCK = 0x8



# =====================================================
# CLASSE EVENEMENTS WINDOWS
# =====================================================

class WindowsEvents:


    def __init__(self, callback):


        self.callback = callback

        self.running = False

        self.thread = None

        self.hwnd = None



    # =================================================

    def start(self):


        if self.running:

            return



        self.running = True



        self.thread = threading.Thread(

            target=self._run,

            daemon=True

        )


        self.thread.start()



    # =================================================

    def _run(self):


        logging.info(
            "WindowsEvents démarré"
        )


        # ------------------------------
        # Classe fenêtre invisible
        # ------------------------------

        wc = win32gui.WNDCLASS()


        wc.lpfnWndProc = self._wnd_proc


        wc.lpszClassName = (
            "NoVisageLockHiddenWindow"
        )


        wc.hInstance = win32api.GetModuleHandle(
            None
        )


        try:

            class_atom = win32gui.RegisterClass(
                wc
            )


        except Exception:


            class_atom = (
                wc.lpszClassName
            )



        # ------------------------------
        # Création fenêtre cachée
        # ------------------------------

        self.hwnd = win32gui.CreateWindow(

            class_atom,

            "NoVisageLock",

            0,

            0,

            0,

            0,

            0,

            0,

            0,

            wc.hInstance,

            None

        )



        logging.info(
            "Fenêtre Windows Events créée"
        )



        # ------------------------------
        # Activation notifications session
        # ------------------------------

        try:


            win32ts.WTSRegisterSessionNotification(

                self.hwnd,

                0

            )


            logging.info(
                "Notifications session activées"
            )


        except Exception as e:


            logging.warning(
                f"WTS notification indisponible : {e}"
            )



        # ------------------------------
        # Boucle messages Windows
        # ------------------------------

        while self.running:


            win32gui.PumpWaitingMessages()


            time.sleep(
                0.1
            )



        if self.hwnd:


            win32gui.DestroyWindow(
                self.hwnd
            )



        logging.info(
            "WindowsEvents arrêté"
        )



    # =================================================

    def _wnd_proc(
        self,
        hwnd,
        msg,
        wparam,
        lparam
    ):


        try:


            # =====================================
            # VEILLE / REVEIL
            # =====================================

            if msg == WM_POWERBROADCAST:


                if wparam == PBT_APMSUSPEND:


                    logging.info(
                        "PC mise en veille"
                    )


                    self.callback(
                        "SUSPEND"
                    )



                elif wparam in (

                    PBT_APMRESUMEAUTOMATIC,

                    PBT_APMRESUMESUSPEND

                ):


                    logging.info(
                        "PC sortie de veille"
                    )


                    self.callback(
                        "RESUME"
                    )



            # =====================================
            # VERROUILLAGE SESSION
            # =====================================

            elif msg == WM_WTSSESSION_CHANGE:



                if wparam == WTS_SESSION_LOCK:


                    logging.info(
                        "Session verrouillée"
                    )


                    self.callback(
                        "LOCK"
                    )



                elif wparam == WTS_SESSION_UNLOCK:


                    logging.info(
                        "Session déverrouillée"
                    )


                    self.callback(
                        "UNLOCK"
                    )



        except Exception as e:


            logging.exception(
                e
            )



        return win32gui.DefWindowProc(

            hwnd,

            msg,

            wparam,

            lparam

        )



    # =================================================

    def stop(self):


        self.running = False


        if self.hwnd:


            win32gui.PostMessage(

                self.hwnd,

                win32con.WM_CLOSE,

                0,

                0

            )