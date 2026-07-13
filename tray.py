import pystray

from PIL import Image, ImageDraw



class TrayIcon:


    def __init__(self, app):


        self.app = app



        menu = pystray.Menu(


            pystray.MenuItem(
                "Afficher caméra",
                self.show
            ),


            pystray.MenuItem(
                "Masquer caméra",
                self.hide
            ),


            pystray.MenuItem(
                "Pause",
                self.pause
            ),


            pystray.MenuItem(
                "Reprendre",
                self.resume
            ),


            pystray.MenuItem(
                "Changer propriétaire",
                self.owner
            ),


            pystray.MenuItem(
                "Quitter",
                self.quit
            )

        )



        self.icon = pystray.Icon(

            "NoVisageLock",

            self.create_icon(),

            "NoVisageLock",

            menu

        )



    def create_icon(self):


        img = Image.new(
            "RGB",
            (64,64),
            "black"
        )


        draw = ImageDraw.Draw(
            img
        )


        draw.ellipse(
            (10,10,54,54),
            fill="green"
        )


        return img



    def show(self):

        self.app.show_preview=True



    def hide(self):

        self.app.show_preview=False



    def pause(self):

        self.app.paused=True



    def resume(self):

        self.app.paused=False



    def owner(self):

        self.app.change_owner()



    def quit(self):

        self.app.close()

        self.icon.stop()



    def start(self):

        self.icon.run()