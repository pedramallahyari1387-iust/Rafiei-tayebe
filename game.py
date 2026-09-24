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
leaf.place(x=200, y=100)
leaf.config(font=("Arial", 30),fg="#008000")

moving_leaf = Label(win, text=moving_direction)
moving_leaf.place(x=200, y=160)
moving_leaf.config(font=("Arial", 30),fg="#FF5F1F")

pointing_label = Label(win, text="POINTING")
pointing_label.place(x=130, y=420, width=100, height=40)
pointing_label.config(font=("Arial", 12), bg="#ADADAD", fg="#0D0D0D")

moving_label = Label(win, text="MOVING")
moving_label.place(x=270, y=420, width=100, height=40)
moving_label.config(font=("Arial", 12), bg="#ADADAD", fg="#0D0D0D")

def update_mode():
    if mode == "pointing":
        pointing_label.config(bg="#008000", fg="white")
        moving_label.config(bg="#ADADAD", fg="#0D0D0D")
    else:
        moving_label.config(bg="#FF5F1F", fg="white")
        pointing_label.config(bg="#ADADAD", fg="#0D0D0D")

modes = ["pointing", "moving"]
mode = random.choice(modes)
update_mode()

message_text = StringVar()
message_text.set("START")

message_label = Label(win, textvariable=message_text)
message_label.place(x=0, y=330, width=500, height=70)
message_label.config(font=("Arial", 20), bg="#ADADAD", fg="#0D0D0D")

#---
time_left = 60

time_text = StringVar()
time_text.set("Time: 60s")

time_label = Label(win, textvariable=time_text)
time_label.place(x=30, y=5, width=100, height=35)
time_label.config(font=("Arial", 15), bg="#ADADAD", fg="#0D0D0D")
#---
score = 0

score_text = StringVar()
score_text.set("Score: 0")

score_label = Label(win, textvariable=score_text)
score_label.place(x=200, y=5, width=100, height=35)
score_label.config(font=("Arial", 15), bg="#ADADAD", fg="#0D0D0D")
#---
stage = 1

stage_text = StringVar()
stage_text.set(f"Stage: {stage}")

stage_label = Label(win, textvariable=stage_text)
stage_label.place(x=370, y=5, width=100, height=35)
stage_label.config(font=("Arial", 15), bg="#ADADAD", fg="#0D0D0D")
#---

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
    update_mode()
    stage_text.set(f"Stage: {stage}")

def timer():
    global time_left

    if time_left > 0:
        time_left -= 1
        time_text.set(f"Time: {time_left}s")
        win.after(1000, timer)
    else:
        message_text.set("Time has run out!")
        message_label.config(bg="#000047", fg="#00FFFF")
        bt1.config(state="disabled")
        bt2.config(state="disabled")
        bt3.config(state="disabled")
        bt4.config(state="disabled")

def up():
    global score
    if mode == "pointing":
        if direction == "^^^^^":
            message_text.set("Correct!")
            message_label.config(bg="#004700", fg="#00FF00")
            score += 1
            score_text.set(f"Score: {score}")
        else:
            message_text.set("Wrong!")
            message_label.config(bg="#470000", fg="#FF0000")
    else:
        if moving_direction == "^^^^^":
            message_text.set("Correct!")
            message_label.config(bg="#004700", fg="#00FF00")
            score += 1
            score_text.set(f"Score: {score}")
        else:
            message_text.set("Wrong!")
            message_label.config(bg="#470000", fg="#FF0000")
    new_direction()

def left():
    global score
    if mode == "pointing":
        if direction == "<<<<<":
            message_text.set("Correct!")
            message_label.config(bg="#004700", fg="#00FF00")
            score += 1
            score_text.set(f"Score: {score}")
        else:
            message_text.set("Wrong!")
            message_label.config(bg="#470000", fg="#FF0000")
    else:
        if moving_direction == "<<<<<":
            message_text.set("Correct!")
            message_label.config(bg="#004700", fg="#00FF00")
            score += 1
            score_text.set(f"Score: {score}")
        else:
            message_text.set("Wrong!")
            message_label.config(bg="#470000", fg="#FF0000")
    new_direction()

def right():
    global score
    if mode == "pointing":
        if direction == ">>>>>":
            message_text.set("Correct!")
            message_label.config(bg="#004700", fg="#00FF00")
            score += 1
            score_text.set(f"Score: {score}")
        else:
            message_text.set("Wrong!")
            message_label.config(bg="#470000", fg="#FF0000")
    else:
        if moving_direction == ">>>>>":
            message_text.set("Correct!")
            message_label.config(bg="#004700", fg="#00FF00")
            score += 1
            score_text.set(f"Score: {score}")
        else:
            message_text.set("Wrong!")
            message_label.config(bg="#470000", fg="#FF0000")
    new_direction()

def down():
    global score
    if mode == "pointing":
        if direction == "vvvvv":
            message_text.set("Correct!")
            message_label.config(bg="#004700", fg="#00FF00")
            score += 1
            score_text.set(f"Score: {score}")
        else:
            message_text.set("Wrong!")
            message_label.config(bg="#470000", fg="#FF0000")
    else:
        if moving_direction == "vvvvv":
            message_text.set("Correct!")
            message_label.config(bg="#004700", fg="#00FF00")
            score += 1
            score_text.set(f"Score: {score}")
        else:
            message_text.set("Wrong!")
            message_label.config(bg="#470000", fg="#FF0000")
    new_direction()

bt1 = Button(win, text="W", command=up)
bt1.place(x=230, y=230)
bt1.config(width=5)

bt2 = Button(win, text="A", command=left)
bt2.place(x=180, y=270)
bt2.config(width=5)

bt3 = Button(win, text="S", command=down)
bt3.place(x=230, y=270)
bt3.config(width=5)

bt4 = Button(win, text="D", command=right)
bt4.place(x=280, y=270)
bt4.config(width=5)

timer()
win.mainloop()