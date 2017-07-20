from tkinter import filedialog, messagebox
from tkinter import ttk
import tkinter as tk
from PIL import ImageTk, Image

import os
import sys

from itertools import cycle

import logging.config

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('App')
logger.setLevel(logging.DEBUG)

IMAGE_DIR = './images/'
HEIGHT = 600
WIDTH = 800
DELAY = 3500 #msecs
LARGE_FONT = ('Verdana', 12)
NORM_FONT = ('Verdana', 10)


class App(tk.Tk):

    def __init__(self):
        tk.Tk.__init__(self)

        self.title('Slideshow')
        self.geometry('800x600')

        os.chdir(IMAGE_DIR)

        container = tk.Frame(self, bd=1)
        container.pack(side='top', fill='both', expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Set directory",
                             command=lambda: self.set_directory())
        menubar.add_cascade(label="File", menu=filemenu)
        tk.Tk.config(self, menu=menubar)

        self.frames = {}

        for f in (StartPage, PictureViewer, AutoSlideshow):
            frame = f(container, self)
            logging.debug("Self: {0}".format(self))
            self.frames[f] = frame
            frame.grid(row=0, column=0, sticky='nsew')
            logging.debug("Frame created: {0}".format(frame))

        print(self.frames)

        self.show_frame(StartPage)

    def show_frame(self, container):
        frame = self.frames[container]
        logging.debug("Frame {0}".format(frame))
        frame.tkraise()

    def set_directory(self):
        try:
            new_dir = tk.filedialog.askdirectory(initialdir='.', title='Select directory')
            os.chdir(new_dir)
        except OSError:
            # window canceled, don't do anything
            return

        logging.debug("Set directory to: {0}".format(os.getcwd()))


def callback(event, *args, **kwargs):
    logging.debug("Button pressed: {0}".format(event))
    for arg in args:
        logging.debug("Arg: {0}".format(arg))
    for kwarg in kwargs:
        logging.debug("Kwarg: {0}".format(kwarg))

def popupmsg(msg):
    popup = tk.Tk()
    popup.wm_title("!")
    label = ttk.Label(popup, text=msg, font=NORM_FONT)
    label.pack(side="top", fill="x", pady=10, padx=10)
    B1 = ttk.Button(popup, text="Okay", command=popup.destroy)
    B1.pack()
    popup.mainloop()


class StartPage(tk.Frame):

    def __init__(self, parent, master):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.master = master

        start_viewer = ttk.Button(self, text='Start picture viewer',
                                  command=lambda: self.master.show_frame(PictureViewer))
        start_viewer.pack(pady=10, padx=10)

        start_slideshow = ttk.Button(self, text='Start automatic slideshow',
                                     command=lambda: self.master.show_frame(AutoSlideshow))
        start_slideshow.pack(pady=10, padx=10)


class PictureViewer(tk.Frame):

    def __init__(self, parent, master):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.master = master

        self.set_up()

    def set_up(self):
        label = ttk.Label(self, text='Picture viewer', font='LARGE_FONT')
        label.pack(pady=10, padx=10)

        end = ttk.Button(self, text='End picture viewer',
                         command=lambda: self.master.show_frame(StartPage))
        end.pack()

    def display(self, next_image=True):
        pass


class AutoSlideshow(tk.Frame):

    def __init__(self, parent, master):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.master = master
        self.current_slide = 0
        self.delay = DELAY

        self.set_image_paths()
        logging.debug("Image paths: {0}".format(self.image_paths))

        self.set_up()

    def set_up(self):
        self.label = ttk.Label(self, text='Slideshow', font='LARGE_FONT')
        self.label.pack(pady=10, padx=10)

        self.button_frame = tk.Frame(self)
        self.button_frame.pack(side='top')

        self.play_button = ttk.Button(self.button_frame, text='Play',
                                      command=lambda: self.start_slideshow())
        self.play_button.pack(side='left')
        self.end_button = ttk.Button(self.button_frame, text='Back to start page',
                                     command=lambda: self.master.show_frame(StartPage))
        self.end_button.pack()

        self.photo_frame = tk.Frame(self)
        self.photo_frame.pack()

        self.photo_label = tk.Label(self.photo_frame, bg='white', height=HEIGHT, width=WIDTH)
        self.photo_label.pack(padx=10, pady=10)

    def set_image_paths(self):
        try:
            cur_dir = os.getcwd()
            self.image_paths = [os.path.join(cur_dir, f) for f in os.listdir(cur_dir)]
            logging.debug("Image paths set to: {0}".format(self.image_paths))
        except FileNotFoundError:
            select = tk.messagebox.askquestion("Select directory",
                                               "No valid directory selected. \nSelect a directory now?")
            if select is 'yes':
                App.set_directory()
            return

    def prep_photo(self, path):
        if not self.image_paths:
            try:
                self.set_image_paths()
            except:
                popupmsg("Can't find images")
                return

        image = Image.open(path)
        resized_image = image.resize((WIDTH, HEIGHT), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(resized_image)

        if photo is None:
            logging.debug("Could not prep photo")
            return

        return photo

    def start_slideshow(self):
        if not self.image_paths:
            try:
                self.set_image_paths()
            except:
                popupmsg("Can't find images")
                return

        self.loop = 1
        self.timer()

    def timer(self):
        if self.loop:
            self.set_photo()
            self.after(self.delay, self.timer)

    def set_photo(self):

        try:
            # get path of photo and prep it
            path = self.image_paths[self.current_slide]
            image = Image.open(path)
            resized_image = image.resize((WIDTH, HEIGHT), Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(resized_image)

            #set the photo
            self.photo_label.config(image=photo)
            self.photo_label.image = photo
            logger.debug("Photo set")

            # update the current slide
            self.current_slide += 1
            logger.debug(self.current_slide)

        except IndexError:
            logger.debug("End of images reached")
            return

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()