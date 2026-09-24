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

def up():
    print("up")

def left():
    print("left")

def right():
    print("right")

def down():
    print("down")

bt1 = Button(win, text="W", command=up)
bt1.place(x=230, y=300)
bt1.config(width=5)

bt2 = Button(win, text="A", command=left)
bt2.place(x=180, y=340)
bt2.config(width=5)

bt3 = Button(win, text="S", command=down)
bt3.place(x=230, y=340)
bt3.config(width=5)

bt4 = Button(win, text="D", command=right)
bt4.place(x=280, y=340)
bt4.config(width=5)

win.mainloop()