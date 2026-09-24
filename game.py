from tkinter import *
import random

win = Tk()
win.title("Ebb and Flow")
win.geometry("500x500")
win.resizable(width=False, height=False)

directions = [">>>>>", "<<<<<", "^^^^^", "vvvvv"]
direction = random.choice(directions)

leaf = Label(win, text=direction)
leaf.place(x=200, y=170)
leaf.config(font=("Arial", 30))

win.mainloop()