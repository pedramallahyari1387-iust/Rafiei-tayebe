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

time_left = 60

time_text = StringVar()
time_text.set("Time: 60s")

time_label = Label(win, textvariable=time_text)
time_label.place(x=30, y=5, width=100, height=35)
time_label.config(font=("Arial", 15), bg="#ADADAD", fg="#0D0D0D")

score = 0

score_text = StringVar()
score_text.set("Score: 0")

score_label = Label(win, textvariable=score_text)
score_label.place(x=200, y=5, width=100, height=35)
score_label.config(font=("Arial", 15), bg="#ADADAD", fg="#0D0D0D")

stage = 1

stage_text = StringVar()
stage_text.set(f"Stage: {stage}")

stage_label = Label(win, textvariable=stage_text)
stage_label.place(x=370, y=5, width=100, height=35)
stage_label.config(font=("Arial", 15), bg="#ADADAD", fg="#0D0D0D")

def new_direction():
    global direction
    global moving_direction
    global mode
    global stage

    direction = random.choice(directions)
    moving_direction = random.choice(directions)
    mode = random.choice(modes)
    stage += 1

    leaf.config(text=direction)
    moving_leaf.config(text=moving_direction)
    mode_text.set(mode)
    stage_text.set(f"Stage: {stage}")

def timer():
    global time_left

    if time_left > 0:
        time_left -= 1
        time_text.set(f"Time: {time_left}s")
        win.after(1000, timer)
    else:
        print("Time has run out!")
        bt1.config(state="disabled")
        bt2.config(state="disabled")
        bt3.config(state="disabled")
        bt4.config(state="disabled")

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

timer()
win.mainloop()