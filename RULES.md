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

## 12. Visual Elements

### 12.1. Screen Layout

The game window is:

800 × 600

### 12.2. Top HUD

The top of the screen contains three panels, arranged from right to left:

1. TIME panel (rightmost)
2. SCORE panel (middle)
3. METER + Multiplier panel (left of SCORE)

Layout details:

- The panels are placed with a 5-pixel gap between them.
- The rightmost panel has a 20-pixel margin from the right edge.
- The panels use a light blue-gray background with dark text.

Meter panel contains:

- 4 circular indicators
- Filled circles: dark
- Empty circles: light gray
- Multiplier value shown as "xN" at the right of the circles

### 12.3. Bottom HUD

The bottom of the screen contains two buttons:

- POINTING (left)
- MOVING (right)

Layout details:

- The buttons are centered horizontally.
- A 10-pixel gap separates them.
- The buttons touch the bottom edge of the screen (no bottom margin).
- Active button: green (POINTING) or orange (MOVING), white text.
- Inactive button: light gray background, black text.

### 12.4. Pause Button

- Located at the top-left corner of the screen.
- Size: 48 × 48 pixels.
- Two vertical bars inside.
- Normal state: black background, light blue bars.
- Hover state: blue background, white bars.

### 12.5. Leaves

- Two types: green (POINTING) and orange (MOVING).
- Leaf sprite aspect ratio: approximately 1 : 1.84 (based on leaf1Sprite).
- Leaves are distributed across the play area.
- Leaves do not overlap (grid-based placement with jitter).
- All leaves share the same visual direction within a round.

### 12.6. Feedback Indicators

- Correct answer: a green checkmark (✓) shown at the center of the screen.
- Wrong answer: an orange cross (✗) shown at the center of the screen.
- The indicator is displayed for a short time after the answer.

---

## 13. Visual and Audio Notes

### 13.1. Sound Effects

The recreation uses generated tones as sound effects:

- Correct answer: two ascending tones (880 Hz, then 1320 Hz).
- Wrong answer: two descending tones (220 Hz, then 160 Hz).

### 13.2. Background Music

- A waterfall sound is played as background music.
- The music loops continuously during gameplay.
- The music is stopped when the game ends.
- The music resumes when the player restarts.

### 13.3. Mute Controls

The pause menu provides two independent mute toggles:

- Mute Sound: disables all sound effects.
- Mute Music: disables the background music.

The labels change when muted:

- "Mute Sound" → "Sound Muted"
- "Mute Music" → "Music Muted"

---

## 14. Pause Menu

The pause menu contains the following options, listed vertically:

- Resume
- Restart
- Mute Sound / Sound Muted
- Mute Music / Music Muted
- Quit
- How To Play

### 14.1. Menu Behavior

- Menu items are left-aligned.
- Hovering over an item highlights it with a brighter background and white text.
- Clicking an item performs its action.

### 14.2. How To Play

Selecting "How To Play" opens a panel with:

- Game instructions
- A "Back" button to return to the pause menu.

### 14.3. Visual During Pause

While the pause menu is open:

- Leaves are hidden.
- The top HUD is hidden.
- The bottom HUD is hidden.
- Only the pause menu and a slightly darkened background are visible.

### 14.4. Pause Menu Header

A small "Paused" panel is displayed at the top-left corner of the screen while paused.

- Normal state: light background.
- Hover state: brighter background.

---

## 15. End Screen

When the game ends (timer reaches zero):

- The top HUD remains visible (TIME, SCORE, METER).
- The pause button is hidden.
- The bottom HUD (POINTING / MOVING) is hidden.
- The background music stops.

The end screen displays:

1. A gray circle in the center containing the final multiplier ("xN").
2. Below the circle: the text "Score Bonus".
3. Below that text: the final bonus amount as a number.

The top SCORE panel is updated to show the final score, which includes:

Final Score = Score + Final Bonus

A hint is also shown at the bottom:

"Press R to restart  |  ESC to quit"

---

## 16. Important Note

The rules above describe the rules implemented in this Python recreation.

Some numerical values such as:

- Base score
- Meter size
- Multiplier progression
- Final bonus
- Timer duration
- Movement speed
- Sound frequencies
- Visual dimensions

were reconstructed during the recreation process and should not automatically be considered confirmed values from the original Lumosity implementation unless independently verified from the original game.

However, the following values were extracted directly from the game's asset files:

- Leaf sprite aspect ratio (from leaf1Sprite).
- Leaf color values (from LeafGreen and LeafOrange materials).
- Background texture (from Texture237).
