"""
====================================================================
EBB AND FLOW — PYTHON RECREATION (v17 — Light HUD + Pause Hover)
====================================================================
تغییرات نسخه ۱۷:
  • HUD بالا: پس‌زمینه آبی-خاکستری روشن، متن تیره
  • دکمه Pause در بازی: با هاور متن/خطوط سفید + پس‌زمینه آبی
  • دکمه Pause در منو: با هاور پس‌زمینه سفیدتر (230 → 255)
====================================================================
"""

import pygame
import random
import math
import os
import array

# ====================================================================
#  مقداردهی اولیه
# ====================================================================
pygame.init()
pygame.font.init()
try:
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    AUDIO_OK = True
except Exception as e:
    print(f"[Audio] mixer init failed: {e}")
    AUDIO_OK = False

WINDOW_W, WINDOW_H = 800, 600
GAME_TOP, GAME_BOTTOM = 50, 520
FPS = 60

screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
pygame.display.set_caption("Ebb and Flow")
clock = pygame.time.Clock()

# ====================================================================
#  رنگ‌ها
# ====================================================================
LEAF_GREEN        = (76, 175, 80)
LEAF_GREEN_LIGHT  = (126, 217, 87)
LEAF_ORANGE       = (245, 166, 35)
LEAF_ORANGE_LIGHT = (255, 217, 102)
LEAF_OUTLINE      = (255, 255, 255)

WHITE      = (255, 255, 255)
BLACK      = (0, 0, 0)

# HUD بالا: آبی-خاکستری روشن (مطابق اسکرین‌شات)، متن تیره
HUD_BG     = (150, 160, 175, 235)
HUD_TEXT   = (25, 30, 40)

# نقطه‌های Meter
DOT_ON     = (40, 45, 55)
DOT_OFF    = (110, 120, 135, 220)

PAUSE_BAR  = (77, 208, 225)

POINTING_ACTIVE   = (76, 175, 80)
MOVING_ACTIVE     = (245, 166, 35)
BTN_INACTIVE      = (190, 190, 190, 210)
BTN_TEXT_INACTIVE = (60, 60, 60)

CORRECT_GREEN = (76, 224, 76)
WRONG_ORANGE  = (245, 130, 32)

MENU_ITEM_BG    = (25, 40, 60)
MENU_ITEM_HOVER = (45, 180, 235)
MENU_TEXT       = (100, 200, 245)
MENU_TEXT_HOVER = (255, 255, 255)

BG_FALLBACK = (10, 26, 46)

LEAF_W, LEAF_H = 60, 110

# ====================================================================
#  کادرهای HUD
# ====================================================================
PAUSE_RECT = pygame.Rect(0, 0, 48, 48)
PAUSE_MENU_RECT = pygame.Rect(0, 0, 150, 48)

HUD_GAP_TOP    = 5
HUD_RIGHT_PAD  = 20
HUD_ITEM_H     = 60

TIME_W  = 145
SCORE_W = 165
METER_W = 145

METER_RECT = pygame.Rect(WINDOW_W - HUD_RIGHT_PAD - METER_W, 0,
                         METER_W, HUD_ITEM_H)
SCORE_RECT = pygame.Rect(METER_RECT.left - HUD_GAP_TOP - SCORE_W, 0,
                         SCORE_W, HUD_ITEM_H)
TIME_RECT  = pygame.Rect(SCORE_RECT.left - HUD_GAP_TOP - TIME_W, 0,
                         TIME_W, HUD_ITEM_H)

HUD_GAP_BOTTOM = 10
POINT_W = 150
MOVE_W  = 150
BOTTOM_H = 60
BOTTOM_Y = WINDOW_H - BOTTOM_H

TOTAL_BOTTOM_W = POINT_W + MOVE_W + HUD_GAP_BOTTOM
BOTTOM_START_X = (WINDOW_W - TOTAL_BOTTOM_W) // 2

POINT_RECT = pygame.Rect(BOTTOM_START_X, BOTTOM_Y, POINT_W, BOTTOM_H)
MOVE_RECT  = pygame.Rect(POINT_RECT.right + HUD_GAP_BOTTOM,
                         BOTTOM_Y, MOVE_W, BOTTOM_H)

# ====================================================================
#  مسیرها
# ====================================================================
BG_CANDIDATES = [
    r"C:\Users\ASUS\Downloads\Texture237.png",
    r"C:\Users\ASUS\Downloads\TexturePNG\Texture237.png",
]

LEAF_GREEN_IMG  = r"C:\Users\ASUS\Downloads\ebb_and_flow_leaf_green.png"
LEAF_ORANGE_IMG = r"C:\Users\ASUS\Downloads\ebb_and_flow_leaf_yellow.png"
MUSIC_PATH      = r"C:\Users\ASUS\Downloads\MUSIC.mp3"

# ====================================================================
#  پس‌زمینه
# ====================================================================
def find_bg():
    for p in BG_CANDIDATES:
        if os.path.exists(p):
            return p
    return None

def load_background():
    path = find_bg()
    if not path:
        print("[BG] not found")
        return None
    try:
        from PIL import Image
        img = Image.open(path).convert("RGB")
        img.load()
        img = img.resize((WINDOW_W, WINDOW_H), Image.LANCZOS)
        raw = img.tobytes()
        surf = pygame.image.frombuffer(raw, (WINDOW_W, WINDOW_H), "RGB").copy()
        dark = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        dark.fill((0, 0, 0, 40))
        surf.blit(dark, (0, 0))
        surf = surf.convert()
        print(f"[BG] loaded OK from {path}")
        return surf
    except Exception as e:
        print(f"[BG] failed: {e}")
        return None

bg_surface = load_background()

# ====================================================================
#  برگ‌ها
# ====================================================================
def load_leaf_image(path):
    if not os.path.exists(path):
        print(f"[Leaf] not found: {path}")
        return None
    try:
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.rotate(img, 90)
        img = pygame.transform.smoothscale(img, (LEAF_W, LEAF_H))
        print(f"[Leaf] loaded {path}  size={img.get_size()}")
        return img
    except Exception as e:
        print(f"[Leaf] failed {path}: {e}")
        return None

leaf_green_img  = load_leaf_image(LEAF_GREEN_IMG)
leaf_orange_img = load_leaf_image(LEAF_ORANGE_IMG)

_leaf_rot_cache = {}
def get_rotated_leaf(base_img, direction):
    if base_img is None:
        return None
    key = (id(base_img), direction)
    if key in _leaf_rot_cache:
        return _leaf_rot_cache[key]
    if direction == "^^^^^":   angle = 0
    elif direction == ">>>>>": angle = -90
    elif direction == "vvvvv": angle = 180
    else:                       angle = 90
    rotated = pygame.transform.rotate(base_img, angle)
    _leaf_rot_cache[key] = rotated
    return rotated

# ====================================================================
#  SFX
# ====================================================================
def make_tone(freq, duration_ms, volume=0.45):
    if not AUDIO_OK:
        return None
    sample_rate = 44100
    n = int(sample_rate * duration_ms / 1000)
    buf = array.array("h")
    for i in range(n):
        t = i / sample_rate
        v = math.sin(2 * math.pi * freq * t)
        fade_start = int(n * 0.7)
        if i > fade_start:
            v *= 1.0 - (i - fade_start) / (n - fade_start)
        buf.append(int(v * volume * 32767))
    try:
        return pygame.mixer.Sound(buffer=buf.tobytes())
    except Exception as e:
        print(f"[Audio] tone failed: {e}")
        return None

SFX_CORRECT_1 = make_tone(880, 80, 0.50)
SFX_CORRECT_2 = make_tone(1320, 140, 0.45)
SFX_WRONG_1   = make_tone(220, 120, 0.55)
SFX_WRONG_2   = make_tone(160, 180, 0.50)

# ====================================================================
#  موسیقی
# ====================================================================
MUSIC_VOLUME = 0.12

music_loaded = False
if AUDIO_OK and os.path.exists(MUSIC_PATH):
    try:
        pygame.mixer.music.load(MUSIC_PATH)
        pygame.mixer.music.set_volume(MUSIC_VOLUME)
        music_loaded = True
        print(f"[Music] loaded OK from {MUSIC_PATH}  volume={MUSIC_VOLUME}")
    except Exception as e:
        print(f"[Music] load failed: {e}")
else:
    if not os.path.exists(MUSIC_PATH):
        print(f"[Music] file not found: {MUSIC_PATH}")

def start_music():
    if music_loaded:
        try: pygame.mixer.music.play(loops=-1)
        except Exception as e: print(f"[Music] play failed: {e}")

def stop_music():
    if music_loaded:
        try: pygame.mixer.music.stop()
        except Exception: pass

# ====================================================================
#  فونت‌ها
# ====================================================================
def make_font(size, bold=True):
    for name in ("Segoe UI", "Arial", "Tahoma", "Verdana"):
        try: return pygame.font.SysFont(name, size, bold=bold)
        except Exception: continue
    return pygame.font.Font(None, size)

font_hud   = make_font(22, True)
font_btn   = make_font(22, True)
font_big   = make_font(44, True)
font_mid   = make_font(28, True)
font_menu  = make_font(22, True)
font_small = make_font(15, False)

# ====================================================================
#  حالت بازی
# ====================================================================
DIRS = [">>>>>", "<<<<<", "^^^^^", "vvvvv"]

mode              = random.choice(["pointing", "moving"])
pointing_dir      = random.choice(DIRS)
moving_dir        = random.choice(DIRS)
orange_visual_dir = random.choice(DIRS)

score      = 0
time_left  = 60
multiplier = 1
meter      = 0
game_over  = False
paused     = False
sound_muted = False
music_muted = False
show_howto = False

NUM_LEAVES = 7
leaves     = []

feedback_type  = None
feedback_timer = 0

def spawn_leaves():
    global leaves
    leaves = []
    cols, rows = 3, 3
    cell_w = (WINDOW_W - 60) / cols
    cell_h = (GAME_BOTTOM - GAME_TOP - 40) / rows
    cells = [(c, r) for r in range(rows) for c in range(cols)]
    random.shuffle(cells)
    for c, r in cells[:NUM_LEAVES]:
        cx = 30 + c * cell_w + cell_w / 2
        cy = GAME_TOP + 20 + r * cell_h + cell_h / 2
        max_jx = max(0, cell_w / 2 - LEAF_W / 2 - 4)
        max_jy = max(0, cell_h / 2 - LEAF_H / 2 - 4)
        jx = random.uniform(-max_jx, max_jx)
        jy = random.uniform(-max_jy, max_jy)
        leaves.append([cx + jx - LEAF_W / 2, cy + jy - LEAF_H / 2])

# ====================================================================
#  منو
# ====================================================================
class MenuItem:
    def __init__(self, key, label_fn, action):
        self.key = key
        self.label_fn = label_fn
        self.action = action
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.hover = False
    def get_label(self): return self.label_fn()

def menu_resume():   global paused; paused = False
def menu_restart():  global paused; restart_game(); paused = False
def menu_toggle_sound(): global sound_muted; sound_muted = not sound_muted
def menu_toggle_music():
    global music_muted
    music_muted = not music_muted
    if music_muted: stop_music()
    else: start_music()
def menu_quit():     global running; running = False
def menu_howto():    global show_howto; show_howto = True
def menu_back_from_howto(): global show_howto; show_howto = False

menu_items = [
    MenuItem("resume",     lambda: "Resume",                          menu_resume),
    MenuItem("restart",    lambda: "Restart",                         menu_restart),
    MenuItem("mute_sound", lambda: "Sound Muted" if sound_muted else "Mute Sound",
             menu_toggle_sound),
    MenuItem("mute_music", lambda: "Music Muted" if music_muted else "Mute Music",
             menu_toggle_music),
    MenuItem("quit",       lambda: "Quit",                            menu_quit),
    MenuItem("howto",      lambda: "How To Play",                     menu_howto),
]

MENU_W = 380
MENU_H_ITEM = 48
MENU_GAP = 4
MENU_X = (WINDOW_W - MENU_W) // 2
MENU_Y_START = 130
MENU_TEXT_LEFT_PAD = 30

def update_menu_rects():
    for i, item in enumerate(menu_items):
        y = MENU_Y_START + i * (MENU_H_ITEM + MENU_GAP)
        item.rect = pygame.Rect(MENU_X, y, MENU_W, MENU_H_ITEM)

BACK_RECT = pygame.Rect(WINDOW_W // 2 - 80, WINDOW_H - 90, 160, 44)

def draw_checkmark(cx, cy, size=70, color=CORRECT_GREEN):
    pts = [(cx - size*0.4, cy), (cx - size*0.1, cy + size*0.3),
           (cx + size*0.4, cy - size*0.3)]
    pygame.draw.lines(screen, color, False, pts, 10)

def draw_crossmark(cx, cy, size=70, color=WRONG_ORANGE):
    off = size * 0.35
    pygame.draw.line(screen, color, (cx-off, cy-off), (cx+off, cy+off), 10)
    pygame.draw.line(screen, color, (cx+off, cy-off), (cx-off, cy+off), 10)

def draw_pause_button_in_game():
    """دکمه Pause در بازی — گوشه بالا-چپ"""
    mouse_pos = pygame.mouse.get_pos()
    hovered = PAUSE_RECT.collidepoint(mouse_pos)
    if hovered:
        btn_bg = (45, 180, 235)      # آبی روشن
        bar_color = (255, 255, 255)  # خطوط سفید
    else:
        btn_bg = (0, 0, 0)
        bar_color = PAUSE_BAR

    pygame.draw.rect(screen, btn_bg, PAUSE_RECT)
    bar_w, bar_h = 6, 24
    gap = 10
    total_w = bar_w * 2 + gap
    sx = PAUSE_RECT.centerx - total_w // 2
    sy = PAUSE_RECT.centery - bar_h // 2
    pygame.draw.rect(screen, bar_color, (sx, sy, bar_w, bar_h))
    pygame.draw.rect(screen, bar_color, (sx + bar_w + gap, sy, bar_w, bar_h))

def draw_pause_button_in_menu():
    """دکمه Pause در منو — با هاور سفیدتر می‌شود"""
    mouse_pos = pygame.mouse.get_pos()
    hovered = PAUSE_MENU_RECT.collidepoint(mouse_pos)
    bg = (255, 255, 255) if hovered else (230, 230, 230)

    pygame.draw.rect(screen, bg, PAUSE_MENU_RECT)
    pygame.draw.rect(screen, (40, 40, 40), (PAUSE_MENU_RECT.x + 14,
                                            PAUSE_MENU_RECT.y + 14, 5, 20))
    pygame.draw.rect(screen, (40, 40, 40), (PAUSE_MENU_RECT.x + 24,
                                            PAUSE_MENU_RECT.y + 14, 5, 20))
    txt = font_menu.render("Paused", True, (40, 40, 40))
    screen.blit(txt, (PAUSE_MENU_RECT.x + 42, PAUSE_MENU_RECT.y + 10))

def draw_pause_menu():
    ov = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 120))
    screen.blit(ov, (0, 0))

    draw_pause_button_in_menu()

    if show_howto:
        draw_howto_panel()
        return

    update_menu_rects()
    mouse_pos = pygame.mouse.get_pos()
    for item in menu_items:
        item.hover = item.rect.collidepoint(mouse_pos)
        bg = MENU_ITEM_HOVER if item.hover else MENU_ITEM_BG
        fg = MENU_TEXT_HOVER if item.hover else MENU_TEXT
        pygame.draw.rect(screen, bg, item.rect)
        label_txt = font_menu.render(item.get_label(), True, fg)
        screen.blit(label_txt, (item.rect.x + MENU_TEXT_LEFT_PAD,
                                item.rect.centery - label_txt.get_height() // 2))

def draw_howto_panel():
    ht_rect = pygame.Rect(60, 70, WINDOW_W - 120, WINDOW_H - 170)
    pygame.draw.rect(screen, (10, 25, 45), ht_rect)
    pygame.draw.rect(screen, MENU_ITEM_HOVER, ht_rect, 3)
    title = font_mid.render("How To Play", True, WHITE)
    screen.blit(title, (ht_rect.centerx - title.get_width() // 2, ht_rect.y + 20))
    lines = [
        "Green leaves  -  press the direction they POINT",
        "Orange leaves -  press the direction they MOVE",
        "", "Correct = 50 x multiplier",
        "Meter fills -> multiplier increases",
        "Wrong = lose meter or multiplier",
        "", "WASD or arrow keys to answer", "Space = pause",
    ]
    for i, line in enumerate(lines):
        t = font_small.render(line, True, WHITE)
        screen.blit(t, (ht_rect.x + 40, ht_rect.y + 80 + i * 28))
    mouse_pos = pygame.mouse.get_pos()
    hovered = BACK_RECT.collidepoint(mouse_pos)
    bg = MENU_ITEM_HOVER if hovered else MENU_ITEM_BG
    fg = MENU_TEXT_HOVER if hovered else MENU_TEXT
    pygame.draw.rect(screen, bg, BACK_RECT)
    bt = font_menu.render("Back", True, fg)
    screen.blit(bt, (BACK_RECT.centerx - bt.get_width() // 2,
                     BACK_RECT.centery - bt.get_height() // 2))

# ====================================================================
#  رسم HUD نیمه‌شفاف
# ====================================================================
def draw_hud_panel(rect, fill_rgba):
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    panel.fill(fill_rgba)
    screen.blit(panel, (rect.x, rect.y))

# ====================================================================
#  رسم صحنه
# ====================================================================
def draw_scene():
    if bg_surface:
        screen.blit(bg_surface, (0, 0))
    else:
        screen.fill(BG_FALLBACK)

    if not paused and not game_over:
        if mode == "pointing":
            base_img = leaf_green_img
            draw_dir = pointing_dir
        else:
            base_img = leaf_orange_img
            draw_dir = orange_visual_dir

        rotated_img = get_rotated_leaf(base_img, draw_dir) if base_img else None
        for lx, ly in leaves:
            if rotated_img:
                rect = rotated_img.get_rect(center=(lx + LEAF_W // 2,
                                                    ly + LEAF_H // 2))
                screen.blit(rotated_img, rect)

    if not paused and not game_over:
        draw_hud()
        draw_feedback()

    if paused:
        draw_pause_menu()
        return

    if game_over:
        draw_hud()
        ov = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 170))
        screen.blit(ov, (0, 0))
        t1 = font_big.render("GAME OVER", True, WHITE)
        t2 = font_mid.render(f"Final Score: {score}", True, WHITE)
        t3 = font_hud.render("Press R to restart  |  ESC to quit",
                             True, (200, 200, 200))
        screen.blit(t1, (WINDOW_W//2 - t1.get_width()//2, WINDOW_H//2 - 80))
        screen.blit(t2, (WINDOW_W//2 - t2.get_width()//2, WINDOW_H//2))
        screen.blit(t3, (WINDOW_W//2 - t3.get_width()//2, WINDOW_H//2 + 50))

def draw_feedback():
    global feedback_timer
    if feedback_timer <= 0 or feedback_type is None:
        return
    cx, cy = WINDOW_W // 2, WINDOW_H // 2
    if feedback_type == "correct":
        draw_checkmark(cx, cy, size=70, color=CORRECT_GREEN)
    else:
        draw_crossmark(cx, cy, size=70, color=WRONG_ORANGE)

# ====================================================================
#  HUD
# ====================================================================
def draw_hud():
    draw_pause_button_in_game()

    # ---------- TIME ----------
    draw_hud_panel(TIME_RECT, HUD_BG)
    lbl = font_hud.render("TIME", True, HUD_TEXT)
    val = font_hud.render(f"0:{time_left:02d}", True, HUD_TEXT)
    pad = 14
    screen.blit(lbl, (TIME_RECT.x + pad, TIME_RECT.centery - lbl.get_height()//2))
    screen.blit(val, (TIME_RECT.right - val.get_width() - pad,
                      TIME_RECT.centery - val.get_height()//2))

    # ---------- SCORE ----------
    draw_hud_panel(SCORE_RECT, HUD_BG)
    lbl = font_hud.render("SCORE", True, HUD_TEXT)
    val = font_hud.render(str(score), True, HUD_TEXT)
    screen.blit(lbl, (SCORE_RECT.x + pad, SCORE_RECT.centery - lbl.get_height()//2))
    screen.blit(val, (SCORE_RECT.right - val.get_width() - pad,
                      SCORE_RECT.centery - val.get_height()//2))

    # ---------- METER ----------
    draw_hud_panel(METER_RECT, HUD_BG)
    dot_r = 8
    dot_gap = 20
    n_dots = 4
    total_dots_w = (n_dots - 1) * dot_gap + dot_r * 2
    xN_txt = font_hud.render(f"x{multiplier}", True, HUD_TEXT)
    right_pad = 12
    xN_w = xN_txt.get_width()
    dots_start_x = METER_RECT.x + (METER_RECT.width - xN_w - right_pad - total_dots_w)//2 + dot_r
    for i in range(n_dots):
        dx = dots_start_x + i * dot_gap
        circ = pygame.Surface((dot_r*2, dot_r*2), pygame.SRCALPHA)
        pygame.draw.circle(circ, DOT_ON if i < meter else DOT_OFF,
                           (dot_r, dot_r), dot_r)
        screen.blit(circ, (dx - dot_r, METER_RECT.centery - dot_r))
    screen.blit(xN_txt, (METER_RECT.right - xN_w - right_pad,
                         METER_RECT.centery - xN_txt.get_height()//2))

    # ---------- POINTING / MOVING ----------
    if mode == "pointing":
        point_bg = POINTING_ACTIVE
        point_fg = WHITE
        move_bg  = BTN_INACTIVE
        move_fg  = BTN_TEXT_INACTIVE
    else:
        point_bg = BTN_INACTIVE
        point_fg = BTN_TEXT_INACTIVE
        move_bg  = MOVING_ACTIVE
        move_fg  = WHITE

    if isinstance(point_bg, tuple) and len(point_bg) == 4:
        p_panel = pygame.Surface((POINT_RECT.width, POINT_RECT.height),
                                 pygame.SRCALPHA)
        p_panel.fill(point_bg)
        screen.blit(p_panel, (POINT_RECT.x, POINT_RECT.y))
    else:
        pygame.draw.rect(screen, point_bg, POINT_RECT)
    txt = font_btn.render("POINTING", True, point_fg)
    screen.blit(txt, (POINT_RECT.centerx - txt.get_width()//2,
                      POINT_RECT.centery - txt.get_height()//2))

    if isinstance(move_bg, tuple) and len(move_bg) == 4:
        m_panel = pygame.Surface((MOVE_RECT.width, MOVE_RECT.height),
                                 pygame.SRCALPHA)
        m_panel.fill(move_bg)
        screen.blit(m_panel, (MOVE_RECT.x, MOVE_RECT.y))
    else:
        pygame.draw.rect(screen, move_bg, MOVE_RECT)
    txt = font_btn.render("MOVING", True, move_fg)
    screen.blit(txt, (MOVE_RECT.centerx - txt.get_width()//2,
                      MOVE_RECT.centery - txt.get_height()//2))

# ====================================================================
#  حرکت برگ‌ها
# ====================================================================
def move_leaves():
    global leaves
    if game_over or paused:
        return
    step = 2
    new_leaves = []
    for lx, ly in leaves:
        if moving_dir == ">>>>>":
            lx += step
            if lx > WINDOW_W + 20: lx = -LEAF_W - 20
        elif moving_dir == "<<<<<":
            lx -= step
            if lx < -LEAF_W - 20: lx = WINDOW_W + 20
        elif moving_dir == "^^^^^":
            ly -= step
            if ly < GAME_TOP - 20: ly = GAME_BOTTOM + 20
        elif moving_dir == "vvvvv":
            ly += step
            if ly > GAME_BOTTOM + 20: ly = GAME_TOP - 20
        new_leaves.append([lx, ly])
    leaves = new_leaves

# ====================================================================
#  امتیاز
# ====================================================================
def add_score():
    global score, multiplier, meter
    score += 50 * multiplier
    meter += 1
    if meter >= 4:
        multiplier = min(multiplier + 1, 10)
        meter = 0

def penalize():
    global multiplier, meter
    if meter > 0: meter = 0
    else: multiplier = max(multiplier - 1, 1)

# ====================================================================
#  بررسی پاسخ
# ====================================================================
def check(player_dir):
    global mode, pointing_dir, moving_dir, orange_visual_dir
    global feedback_type, feedback_timer

    if game_over or paused:
        return

    if mode == "pointing": correct = (pointing_dir == player_dir)
    else:                   correct = (moving_dir == player_dir)

    if correct:
        add_score()
        feedback_type = "correct"
        feedback_timer = 400
        if not sound_muted and SFX_CORRECT_1:
            SFX_CORRECT_1.play()
            pygame.time.set_timer(pygame.USEREVENT + 5, 90, loops=1)
    else:
        penalize()
        feedback_type = "wrong"
        feedback_timer = 400
        if not sound_muted and SFX_WRONG_1:
            SFX_WRONG_1.play()
            pygame.time.set_timer(pygame.USEREVENT + 6, 130, loops=1)

    mode              = random.choice(["pointing", "moving"])
    pointing_dir      = random.choice(DIRS)
    moving_dir        = random.choice(DIRS)
    orange_visual_dir = random.choice(DIRS)
    spawn_leaves()

# ====================================================================
#  ریست
# ====================================================================
def restart_game():
    global mode, pointing_dir, moving_dir, orange_visual_dir
    global score, time_left, multiplier, meter, game_over, paused
    global feedback_timer, feedback_type

    mode              = random.choice(["pointing", "moving"])
    pointing_dir      = random.choice(DIRS)
    moving_dir        = random.choice(DIRS)
    orange_visual_dir = random.choice(DIRS)
    score = 0
    time_left = 60
    multiplier = 1
    meter = 0
    game_over = False
    paused = False
    feedback_timer = 0
    feedback_type = None
    spawn_leaves()

# ====================================================================
#  حلقه اصلی
# ====================================================================
TIMER_EVENT  = pygame.USEREVENT + 1
SFX2_CORRECT = pygame.USEREVENT + 5
SFX2_WRONG   = pygame.USEREVENT + 6

pygame.time.set_timer(TIMER_EVENT, 1000)

spawn_leaves()
start_music()
running = True
last_frame_ms = pygame.time.get_ticks()

while running:
    now_ms = pygame.time.get_ticks()
    dt_ms = now_ms - last_frame_ms
    last_frame_ms = now_ms
    if feedback_timer > 0: feedback_timer -= dt_ms

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == TIMER_EVENT:
            if not game_over and not paused:
                if time_left > 0: time_left -= 1
                else:
                    game_over = True
                    score += 250 * multiplier
        elif event.type == SFX2_CORRECT:
            if not sound_muted and SFX_CORRECT_2: SFX_CORRECT_2.play()
        elif event.type == SFX2_WRONG:
            if not sound_muted and SFX_WRONG_2: SFX_WRONG_2.play()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not paused and not game_over:
                if PAUSE_RECT.collidepoint(event.pos):
                    paused = True
                    show_howto = False
                    continue
            if paused:
                if show_howto:
                    if BACK_RECT.collidepoint(event.pos):
                        menu_back_from_howto()
                        continue
                else:
                    if PAUSE_MENU_RECT.collidepoint(event.pos):
                        paused = False
                        continue
                    update_menu_rects()
                    for item in menu_items:
                        if item.rect.collidepoint(event.pos):
                            item.action()
                            break
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not game_over:
                    paused = not paused
                    show_howto = False
                continue
            if event.key == pygame.K_ESCAPE:
                if game_over: running = False
                elif show_howto: show_howto = False
                elif paused: paused = False
                else: paused = True
                continue
            if event.key == pygame.K_r and game_over:
                restart_game()
                continue
            if paused: continue
            if event.key in (pygame.K_UP, pygame.K_w): check("^^^^^")
            elif event.key in (pygame.K_DOWN, pygame.K_s): check("vvvvv")
            elif event.key in (pygame.K_LEFT, pygame.K_a): check("<<<<<")
            elif event.key in (pygame.K_RIGHT, pygame.K_d): check(">>>>>")

    move_leaves()
    draw_scene()
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
print("Game closed cleanly.")