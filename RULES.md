# Ebb and Flow — Game Rules

## 1. Game Objective

Ebb and Flow is a reaction and attention game based on two different rules:

- POINTING: Follow the direction in which the leaf is pointing.
- MOVING: Follow the direction in which the leaf is moving.

The active mode is displayed at the bottom of the screen.

---

## 2. Answering

The player can answer using:

- Arrow Keys
- W, A, S, D

Controls:

W / ↑ → Up
S / ↓ → Down
A / ← → Left
D / → → Right

For every answer, the game checks the current mode:

- In POINTING, the answer is compared with the leaf's pointing direction.
- In MOVING, the answer is compared with the leaf's movement direction.

After each answer, a new round is generated with new directions and a new mode.

---

## 3. Correct Answer

When the player gives a correct answer:

- The score increases.
- The amount of score gained depends on the current multiplier.
- The progress meter increases.
- A correct-answer feedback is displayed.
- A correct-answer sound effect can be played.
- The next round starts.

Score Formula:

Score Gain = Base Score × Multiplier

The recreation currently uses:

Base Score = 50

Therefore:

Multiplier x1 → +50
Multiplier x2 → +100
Multiplier x3 → +150
Multiplier x4 → +200
...

---

## 4. Meter and Multiplier

Correct answers fill the progress meter.

The recreation uses a 4-step meter:

● ● ● ●

Each correct answer fills one step.

When all 4 steps are filled:

- The meter resets.
- The multiplier increases by 1.
- The multiplier has a maximum value of x10.

Example:

Multiplier x1
Correct → Meter 1/4
Correct → Meter 2/4
Correct → Meter 3/4
Correct → Meter 4/4

→ Meter resets
→ Multiplier becomes x2

The same process continues for higher multipliers.

---

## 5. Wrong Answer

When the player gives an incorrect answer:

- No score is added.
- The current progress is penalized.
- If the meter contains progress, the meter is reset.
- If the meter is already empty, the multiplier decreases by 1.
- The multiplier cannot go below x1.
- A wrong-answer feedback is displayed.
- A wrong-answer sound effect can be played.
- The next round starts.

Penalty behavior:

If Meter > 0:
    Meter → 0

If Meter = 0:
    Multiplier → Multiplier - 1

The minimum multiplier is:

x1

---

## 6. Game Timer

The game starts with:

60 seconds

The timer decreases while the game is active.

The timer does not decrease while the game is paused.

When the timer reaches zero:

- The game ends.
- No further answers can be submitted.
- The final score is displayed.
- A final bonus is added to the score.

---

## 7. End-of-Game Bonus

When the timer reaches zero, a final bonus is calculated using the current multiplier.

Current recreation formula:

Final Bonus = 250 × Multiplier

Examples:

Multiplier x1 → +250
Multiplier x2 → +500
Multiplier x3 → +750
Multiplier x4 → +1000

The final score is therefore:

Final Score = Current Score + Final Bonus

---

## 8. Game Stages / Rounds

Each answer creates a new round.

At the beginning of each round:

1. A new game mode is selected.
2. A new pointing direction is selected.
3. A new moving direction is selected.
4. The leaves are repositioned.
5. The player must determine the correct response according to the active mode.

The two main modes are:

POINTING
MOVING

The player must continuously switch attention between these two rules.

---

## 9. Movement

When the active mode is MOVING, the leaves move according to the selected movement direction.

Possible directions:

>>>>>
<<<<<
^^^^^
vvvvv

The leaves continuously move across the game area and re-enter from the opposite side when they leave the screen.

---

## 10. Pause

The game can be paused using:

SPACE

or by clicking the pause button.

While paused:

- The timer stops.
- The leaves stop moving.
- Answers are ignored.
- The pause menu is displayed.

The game can be resumed from the pause menu.

---

## 11. Restart

After the game ends, the player can restart using:

R

Restarting resets:

Score      → 0
Time       → 60 seconds
Multiplier → x1
Meter      → 0
Game Over  → False

A new mode and new directions are also generated.

---

## 12. Important Note

The rules above describe the rules implemented in this Python recreation.

Some numerical values such as:

- Base score
- Meter size
- Multiplier progression
- Final bonus
- Timer duration
- Movement speed

were reconstructed during the recreation process and should not automatically be considered confirmed values from the original Lumosity implementation unless independently verified from the original game.
