from tkinter import *
import random

win = Tk()
win.title("Ebb and Flow")
win.geometry("500x500")
win.resizable(width=False, height=False)

directions = [">>>>>", "<<<<<", "^^^^^", "vvvvv"]
direction = random.choice(directions)
moving_direction = random.choice(directions)

leaf = Label(win, text=direction)
leaf.place(x=200, y=170)
leaf.config(font=("Arial", 30))

moving_leaf = Label(win, text=moving_direction)
moving_leaf.place(x=200, y=230)
moving_leaf.config(font=("Arial", 30))

modes = ["pointing", "moving"]
mode = random.choice(modes)

mode_text = StringVar()
mode_text.set(mode)

mode_label = Label(win, textvariable=mode_text)
mode_label.place(x=210, y=80)
mode_label.config(font=("Arial", 15))

score = 0

score_text = StringVar()
score_text.set("Score: 0")

score_label = Label(win, textvariable=score_text)
score_label.place(x=210, y=50)
score_label.config(font=("Arial", 15))

def new_direction():
    global direction
    direction = random.choice(directions)
    leaf.config(text=direction)

def up():
    global score
    if mode == "pointing":
        if direction == "^^^^^":
            print("Correct!")
            score += 1
            score_text.set(f"Score: {score}")
        else:
            print("Wrong!")
    else:
        if moving_direction == "^^^^^":
            print("Correct!")
            score += 1
            score_text.set(f"Score: {score}")
        else:
            print("Wrong!")
    new_direction()

def left():
    global score
    if mode == "pointing":
        if direction == "<<<<<":
            print("Correct!")
            score += 1
            score_text.set(f"Score: {score}")
        else:
            print("Wrong!")
    else:
        if moving_direction == "<<<<<":
            print("Correct!")
            score += 1
            score_text.set(f"Score: {score}")
        else:
            print("Wrong!")
    new_direction()

def right():
    global score
    if mode == "pointing":
        if direction == ">>>>>":
            print("Correct!")
            score += 1
            score_text.set(f"Score: {score}")
        else:
            print("Wrong!")
    else:
        if moving_direction == ">>>>>":
            print("Correct!")
            score += 1
            score_text.set(f"Score: {score}")
        else:
            print("Wrong!")
    new_direction()

def down():
    global score
    if mode == "pointing":
        if direction == "vvvvv":
            print("Correct!")
            score += 1
            score_text.set(f"Score: {score}")
        else:
            print("Wrong!")
    else:
        if moving_direction == "vvvvv":
            print("Correct!")
            score += 1
            score_text.set(f"Score: {score}")
        else:
            print("Wrong!")
    new_direction()

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