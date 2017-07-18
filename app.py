from tkinter import filedialog, messagebox
import tkinter as tk
from PIL import ImageTk, Image

import os
import sys

import logging.config

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('App')
logger.setLevel(logging.DEBUG)

IMAGE_DIR = './cats/'
HEIGHT = 600
WIDTH = 800


class App(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        self.dir = IMAGE_DIR
        logger.debug("Current directory is {0}".format(self.dir))

        # set up menu
        self.menubar = tk.Menu(self.parent)
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Open",
                                  command=self.choose_directory)
        self.menubar.add_cascade(label="File", menu=self.filemenu)

        self.parent.config(menu=self.menubar)

        # frame inside main frame for containing dynamic widgets
        self.frame = tk.Frame(self.parent, relief='raised')
        self.frame.grid()

        # get files from current directory
        try:
            self.image_paths = [os.path.join(self.dir, f) for f in os.listdir(self.dir)]
        except FileNotFoundError:
            if tk.messagebox.askquestion("Select directory",
                                         "No directory selected. \nSelect a directory now?"):
                self.choose_directory()

        # keep track of files
        self.cur = -1

        self.initialize_start()

    def initialize_start(self):
        # remove widgets from secondary frame
        self.tear_down_all()

        # add widgets to secondary frame
        self.start = tk.Label(self.frame, text='Press "Enter" to start')
        self.start.focus_set()
        self.start.bind('<Return>',
                        lambda event, : self.initialize_slideshow(event))
        self.start.grid(sticky='wens')

        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(0, weight=1)

        logger.debug("Start screen initialized")

    def tear_down_all(self, event=None, *args):
        # remove widgets from secondary frame
        logger.debug("Button pressed: {0}".format(event))

        for widget in self.frame.winfo_children():
            widget.destroy()
            logger.debug("Removed widget: {0}".format(widget))

    def choose_directory(self, event=None, *args):
        self.dir = tk.filedialog.askdirectory(initialdir='.', title='Select directory')
        if self.dir:
            self.image_paths = [os.path.join(self.dir, f) for f in os.listdir(self.dir)]

        logger.debug("Current directory is {0}".format(self.dir))
        logger.debug("File_paths are {0}".format(self.image_paths))

    def initialize_slideshow(self, event=None, *args):

        try:
            os.listdir(path=self.dir)
        except FileNotFoundError:
            tk.messagebox.showwarning("No valid directory",
                                      "No valid directory selected. \nSelect a directory to continue.")
            return

        # remove all existing widgets
        self.tear_down_all(event)

        # set up widgets to control the slideshow
        self.button_next = tk.Button(self.frame, text='Next')
        self.button_next.bind('<ButtonRelease-1>',
                              lambda event, next_image=True: self._button_callback(event, next_image))
        self.button_next.grid(row=0, column=2, sticky='w')

        self.button_back = tk.Button(self.frame, text='Back')
        self.button_back.bind('<ButtonRelease-1>',
                              lambda event, next_image=False: self._button_callback(event, next_image))
        self.button_back.grid(row=0, column=1, sticky='e')

        self.button_end = tk.Button(self.frame, text='End slideshow')
        self.button_end.bind('<ButtonRelease-1>',
                             lambda event: self.tear_down_slideshow(event))
        self.button_end.grid(row=0, column=3, sticky='w')

        # set up widgets that will be set by the display method
        self.photo_label = tk.Label(self.frame)
        self.photo_label.focus_set()
        self.photo_label.bind('<Return>', self.display)
        self.photo_label.grid(row=1, columnspan=4, sticky='nsew')

        self.number_label = tk.Label(self.frame)
        self.number_label.grid(row=0, column=3, sticky='e', padx=10)

        logger.debug("Widgets for slideshow set up: {0}".format(self.frame.winfo_children()))

        #start slideshow
        self.display()

    def _button_callback(self, event=None, *args):
        logger.debug("Button pressed: {0}".format(event))

        self.display(*args)

    def tear_down_slideshow(self, event, *args):
        # remove widgets from secondary frame for slideshow
        logger.debug("Button pressed: {0}".format(event))

        for widget in self.frame.winfo_children():
            widget.destroy()
            logger.debug("Removed widget: {0}".format(widget))

        # reset start screen
        self.initialize_start()

    def display(self, next_image=True):
        logger.debug("Current children: {0}".format(self.frame.winfo_children()))

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
            self.set_image_number()
        except IndexError:
            self.cur = -1
            logger.debug("End of images reached")
            self.display()
            return

    def set_photo(self):
        f = self.image_paths[self.cur]
        image = Image.open(f)
        resized_image = image.resize((WIDTH, HEIGHT), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(resized_image)

        self.photo_label.config(image=photo)
        self.photo_label.image = photo

        logger.debug("Photo set to {0}".format(f))

    def set_image_number(self):
        # updates current image number out of total images
        image_number = '{0}/{1}'.format(self.cur + 1, len(self.image_paths))
        self.number_label.config(text=image_number)

        logger.debug("Image number label set: {0}".format(image_number))

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