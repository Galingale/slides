import tkinter as tk
from PIL import ImageTk, Image
import os
import sys

IMAGE_DIR = './images/'
HEIGHT = 600
WIDTH = 800


class App(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.images = [os.path.join(IMAGE_DIR, f) for f in os.listdir(IMAGE_DIR)]
        self.cur = -1

        self.initialize()

    def initialize(self):

        self.label = tk.Label(self, text='Press "Enter" to start')
        self.label.grid(row=1, column=0, columnspan=4)
        self.label.focus_set()
        self.label.bind('<Return>', self.display)

        self.button_next = tk.Button(self, text='Next', command=lambda: self.display())
        self.button_next.grid(row=0, column=2, sticky='w')

        self.button_back = tk.Button(self, text='Back', command=lambda: self.display(next_image=False))
        self.button_back.grid(row=0, column=1, sticky='e')

    def display(self, next_image=True):

        cur_a = self.cur

        if next_image:
            self.cur += 1
            #print('Next from {0} to {1}'.format(cur_a, self.cur))
        elif not next_image and self.cur <= 0:
            self.cur = len(self.images)-1
            #print('Back from {0} to {1}'.format(cur_a, self.cur))
        elif not next_image:
            self.cur -= 1
            #print('Back from {0} to {1}'.format(cur_a, self.cur))

        try:
            f = self.images[self.cur]
        except IndexError:
            self.cur = -1
            self.display()
            return

        image = Image.open(f)
        image = image.resize((WIDTH, HEIGHT), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(image)

        self.label.config(image=photo)
        self.label.image = photo
        self.label.text = 'Photo {0}'.format(self.cur)

        # displays current image number out of total images
        image_number = tk.Label(self, text='{0}/{1}'.format(self.cur + 1, len(self.images)))
        image_number.grid(row=0, column=3, sticky='e', padx=10)

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