import tkinter as tk
from PIL import ImageTk, Image

import os
import sys

import logging.config

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('App')
logger.setLevel(logging.DEBUG)

IMAGE_DIR = './images/'
HEIGHT = 600
WIDTH = 800


class App(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.image_paths = [os.path.join(IMAGE_DIR, f) for f in os.listdir(IMAGE_DIR)]
        self.cur = -1

        self.initialize_start()

    def initialize_start(self):

        self.start = tk.Label(self, text='Press "Enter" to start')
        self.start.focus_set()
        self.start.bind('<Return>',
                        lambda event, : self.initialize_slideshow(event))
        self.start.grid(sticky='wens')

        logger.debug("Start screen initialized")

    def tear_down_all(self, event, *args):
        logger.debug("Button pressed: {0}".format(event))

        for widget in self.winfo_children():
            widget.destroy()
            logger.debug("Removed widget: {0}".format(widget))

    def _button_callback(self, event, *args):
        logger.debug("Button pressed: {0}".format(event))

        self.display(*args)

    def initialize_slideshow(self, event, *args):
        # remove all existing widgets
        self.tear_down_all(event)

        # set up widgets for the slideshow
        self.button_next = tk.Button(self, text='Next')
        self.button_next.bind('<ButtonRelease-1>',
                              lambda event, next_image=True: self._button_callback(event, next_image))
        self.button_next.grid(row=0, column=2, sticky='w')

        self.button_back = tk.Button(self, text='Back')
        self.button_back.bind('<ButtonRelease-1>',
                              lambda event, next_image=False: self._button_callback(event, next_image))
        self.button_back.grid(row=0, column=1, sticky='e')

        self.button_end = tk.Button(self, text='End slideshow')
        self.button_end.bind('<ButtonRelease-1>',
                             lambda event: self.tear_down_slideshow(event))
        self.button_end.grid(row=0, column=3, sticky='w')

        logger.debug("Widgets for slideshow set up")
        logger.debug("Widgets: {0}".format(self.winfo_children()))

        #start slideshow
        self.display()

    def tear_down_slideshow(self, event, *args):
        # remove widgets for slideshow
        logger.debug("Button pressed: {0}".format(event))

        for widget in self.winfo_children():
            widget.destroy()
            logger.debug("Removed widget: {0}".format(widget))

        # reset start screen
        self.initialize_start()

    def display(self, next_image=True):

        cur_a = self.cur

        if next_image:
            self.cur += 1
            logger.debug('Next from {0} to {1}'.format(cur_a, self.cur))
        elif not next_image and self.cur <= 0:
            self.cur = len(self.image_paths)-1
            logger.debug('Back from {0} to {1}'.format(cur_a, self.cur))
        elif not next_image:
            self.cur -= 1
            logger.debug('Back from {0} to {1}'.format(cur_a, self.cur))

        try:
            self.set_photo()
            logger.debug("Photo set to {0}".format(self.image_paths[self.cur]))
        except IndexError:
            self.cur = -1
            logger.debug("End of images reached")
            self.display()
            return

        # updates current image number out of total images
        self.image_number = tk.Label(self, text='{0}/{1}'.format(self.cur + 1, len(self.image_paths)))
        self.image_number.grid(row=0, column=3, sticky='e', padx=10)


    def set_photo(self):
        f = self.image_paths[self.cur]
        photo = self.prep_image(f)

        self.photo_label = tk.Label(self, image=photo)
        self.photo_label.image = photo
        self.photo_label.focus_set()
        self.photo_label.bind('<Return>', self.display)
        self.photo_label.grid(row=1, columnspan=4, sticky='nsew')

    def prep_image(self, f):
        image = Image.open(f)
        resized_image = image.resize((WIDTH, HEIGHT), Image.ANTIALIAS)
        return ImageTk.PhotoImage(resized_image)

    def quit(self):
        sys.exit()


def main():
    root = tk.Tk()
    root.title('Slides')
    root.geometry(str(WIDTH) + 'x' + str(HEIGHT))
    app = App(root)
    app.grid(row=0, column=0)
    root.mainloop()

if __name__ == "__main__":
    main()