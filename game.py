"""
====================================================================
EBB AND FLOW — PYTHON RECREATION (v9 — 800×600 + Pause Menu)
====================================================================
تغییرات نسخه ۹:
  • ابعاد پنجره: 800 × 600
  • Meter: ۴ نقطه (نه ۵)
  • بازخورد بصری: تیک سبز / ضربدر نارنجی (نه متن)
  • منوی Pause کامل با ۶ گزینه و hover effect
  • اندازه‌های HUD متناسب با 800×600
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
    pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
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
HUD_BG     = (58, 58, 58)
DOT_ON     = (255, 255, 255)
DOT_OFF    = (85, 85, 85)
PAUSE_BAR  = (77, 208, 225)

POINTING_ACTIVE   = (76, 175, 80)
MOVING_ACTIVE     = (245, 166, 35)
BTN_INACTIVE      = (170, 170, 170)
BTN_TEXT_INACTIVE = (51, 51, 51)

CORRECT_GREEN = (76, 224, 76)
WRONG_ORANGE  = (245, 130, 32)

MENU_BG         = (15, 30, 50)
MENU_ITEM_BG    = (25, 40, 60)
MENU_ITEM_HOVER = (45, 180, 235)
MENU_TEXT       = (100, 200, 245)
MENU_TEXT_HOVER = (255, 255, 255)

BG_FALLBACK = (10, 26, 46)

# ====================================================================
#  اندازه برگ — از leaf1Sprite (70.955 × 130.4)
# ====================================================================
LEAF_W, LEAF_H = 60, 110

# ====================================================================
#  کادرها (متناسب با 800×600)
# ====================================================================
PAUSE_RECT  = pygame.Rect(8, 8, 44, 44)
TIME_RECT   = pygame.Rect(360, 0, 140, 60)
SCORE_RECT  = pygame.Rect(500, 0, 160, 60)
METER_RECT  = pygame.Rect(660, 0, 140, 60)

POINT_RECT  = pygame.Rect(250, 530, 150, 60)
MOVE_RECT   = pygame.Rect(400, 530, 150, 60)

# ====================================================================
#  مسیرها
# ====================================================================
BG_CANDIDATES = [
    r"C:\Users\ASUS\Downloads\Texture237.png",
    r"C:\Users\ASUS\Downloads\TexturePNG\Texture237.png",
]

LEAF_GREEN_IMG  = r"C:\Users\ASUS\Downloads\ebb_and_flow_leaf_green.png"
LEAF_ORANGE_IMG = r"C:\Users\ASUS\Downloads\ebb_and_flow_leaf_yellow.png"

# ====================================================================
#  بارگذاری پس‌زمینه
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
#  بارگذاری برگ
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
#  صدای مصنوعی
# ====================================================================
def make_tone(freq, duration_ms, volume=0.30):
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

SFX_CORRECT_1 = make_tone(880, 80, 0.30)
SFX_CORRECT_2 = make_tone(1320, 140, 0.28)
SFX_WRONG_1   = make_tone(220, 120, 0.35)
SFX_WRONG_2   = make_tone(160, 180, 0.32)

# ====================================================================
#  فونت‌ها
# ====================================================================
def make_font(size, bold=True):
    for name in ("Segoe UI", "Arial", "Tahoma", "Verdana"):
        try:
            return pygame.font.SysFont(name, size, bold=bold)
        except Exception:
            continue
    return pygame.font.Font(None, size)

font_hud   = make_font(18, True)
font_btn   = make_font(20, True)
font_big   = make_font(44, True)
font_mid   = make_font(28, True)
font_menu  = make_font(24, True)
font_small = make_font(16, False)

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
muted      = False
show_howto = False

NUM_LEAVES = 7
leaves     = []

# feedback: None | "correct" | "wrong"
feedback_type  = None
feedback_timer = 0

def spawn_leaves():
    global leaves
    leaves = []
    for _ in range(NUM_LEAVES):
        x = random.randint(30, WINDOW_W - LEAF_W - 30)
        y = random.randint(GAME_TOP + 30, GAME_BOTTOM - LEAF_H - 30)
        leaves.append([x, y])

# ====================================================================
#  منوی Pause
# ====================================================================
class MenuItem:
    def __init__(self, key, label, action):
        self.key = key
        self.label = label
        self.action = action
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.hover = False

def menu_resume():
    global paused
    paused = False

def menu_restart():
    global paused
    restart_game()
    paused = False

def menu_mute_sound():
    global muted
    muted = not muted

def menu_mute_music():
    global muted
    muted = not muted

def menu_quit():
    global running
    running = False

def menu_howto():
    global show_howto
    show_howto = not show_howto

menu_items = [
    MenuItem("resume",     "Resume",     menu_resume),
    MenuItem("restart",    "Restart",    menu_restart),
    MenuItem("mute_sound", "Mute Sound", menu_mute_sound),
    MenuItem("mute_music", "Mute Music", menu_mute_music),
    MenuItem("quit",       "Quit",       menu_quit),
    MenuItem("howto",      "How To Play", menu_howto),
]

# ابعاد منو
MENU_W = 400
MENU_H_ITEM = 50
MENU_GAP = 4
MENU_X = (WINDOW_W - MENU_W) // 2
MENU_Y_START = 120

def update_menu_rects():
    for i, item in enumerate(menu_items):
        y = MENU_Y_START + i * (MENU_H_ITEM + MENU_GAP)
        item.rect = pygame.Rect(MENU_X, y, MENU_W, MENU_H_ITEM)

# ====================================================================
#  رسم تیک و ضربدر
# ====================================================================
def draw_checkmark(cx, cy, size=60, color=(76, 224, 76)):
    """تیک سبز — دو خط مورب"""
    pts = [
        (cx - size * 0.4, cy),
        (cx - size * 0.1, cy + size * 0.3),
        (cx + size * 0.4, cy - size * 0.3),
    ]
    pygame.draw.lines(screen, color, False, pts, 8)

def draw_crossmark(cx, cy, size=60, color=(245, 130, 32)):
    """ضربدر نارنجی — دو خط مورب"""
    off = size * 0.35
    pygame.draw.line(screen, color, (cx - off, cy - off), (cx + off, cy + off), 8)
    pygame.draw.line(screen, color, (cx + off, cy - off), (cx - off, cy + off), 8)

# ====================================================================
#  رسم منوی Pause
# ====================================================================
def draw_pause_menu():
    # پس‌زمینه نیمه‌تاریک
    ov = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 170))
    screen.blit(ov, (0, 0))

    # کادر بالا چپ "Paused"
    paused_rect = pygame.Rect(0, 0, 140, 44)
    pygame.draw.rect(screen, (230, 230, 230), paused_rect)
    # دو خط تیره (آیکن Pause)
    pygame.draw.rect(screen, (40, 40, 40), (14, 12, 5, 20))
    pygame.draw.rect(screen, (40, 40, 40), (24, 12, 5, 20))
    txt = font_menu.render("Paused", True, (40, 40, 40))
    screen.blit(txt, (40, 8))

    update_menu_rects()
    mouse_pos = pygame.mouse.get_pos()

    for item in menu_items:
        item.hover = item.rect.collidepoint(mouse_pos)
        bg = MENU_ITEM_HOVER if item.hover else MENU_ITEM_BG
        fg = MENU_TEXT_HOVER if item.hover else MENU_TEXT
        pygame.draw.rect(screen, bg, item.rect)

        # آیکن ساده بر اساس نوع
        icon_x = item.rect.x + 30
        icon_y = item.rect.centery
        if item.key == "resume":
            pygame.draw.polygon(screen, fg,
                                [(icon_x - 6, icon_y - 8),
                                 (icon_x - 6, icon_y + 8),
                                 (icon_x + 8, icon_y)])
        elif item.key == "restart":
            pygame.draw.circle(screen, fg, (icon_x, icon_y), 8, 3)
            pygame.draw.polygon(screen, fg,
                                [(icon_x + 4, icon_y - 10),
                                 (icon_x + 10, icon_y - 6),
                                 (icon_x + 4, icon_y - 2)])
        elif item.key == "mute_sound":
            pygame.draw.circle(screen, fg, (icon_x, icon_y), 8, 2)
            pygame.draw.line(screen, fg, (icon_x - 4, icon_y - 4),
                             (icon_x + 4, icon_y + 4), 2)
            pygame.draw.line(screen, fg, (icon_x + 4, icon_y - 4),
                             (icon_x - 4, icon_y + 4), 2)
        elif item.key == "mute_music":
            pygame.draw.circle(screen, fg, (icon_x, icon_y), 8, 2)
            pygame.draw.line(screen, fg, (icon_x + 2, icon_y + 5),
                             (icon_x + 2, icon_y - 6), 2)
        elif item.key == "quit":
            pygame.draw.line(screen, fg, (icon_x - 7, icon_y - 7),
                             (icon_x + 7, icon_y + 7), 3)
            pygame.draw.line(screen, fg, (icon_x + 7, icon_y - 7),
                             (icon_x - 7, icon_y + 7), 3)
        elif item.key == "howto":
            pygame.draw.circle(screen, fg, (icon_x, icon_y), 9, 2)
            txt_q = font_hud.render("?", True, fg)
            screen.blit(txt_q, (icon_x - txt_q.get_width() // 2,
                                icon_y - txt_q.get_height() // 2))

        # متن
        label_txt = font_menu.render(item.label, True, fg)
        screen.blit(label_txt, (item.rect.x + 70,
                                item.rect.centery - label_txt.get_height() // 2))

    # اگه How To Play فعاله، یه پنل توضیح نشون بده
    if show_howto:
        ht_rect = pygame.Rect(80, 80, WINDOW_W - 160, WINDOW_H - 160)
        pygame.draw.rect(screen, (10, 25, 45), ht_rect)
        pygame.draw.rect(screen, MENU_ITEM_HOVER, ht_rect, 3)
        title = font_mid.render("How To Play", True, WHITE)
        screen.blit(title, (ht_rect.centerx - title.get_width() // 2,
                            ht_rect.y + 20))
        lines = [
            "Green leaves  →  press the direction they POINT",
            "Orange leaves →  press the direction they MOVE",
            "",
            "Correct = 50 × multiplier",
            "Meter fills → multiplier increases",
            "Wrong = lose meter or multiplier",
            "",
            "WASD or arrow keys to answer",
            "Space to pause",
        ]
        for i, line in enumerate(lines):
            t = font_small.render(line, True, WHITE)
            screen.blit(t, (ht_rect.x + 30, ht_rect.y + 80 + i * 26))
        hint = font_small.render("Press How To Play again to close",
                                 True, (180, 180, 180))
        screen.blit(hint, (ht_rect.centerx - hint.get_width() // 2,
                           ht_rect.bottom - 30))

# ====================================================================
#  رسم صحنه
# ====================================================================
def draw_scene():
    if bg_surface:
        screen.blit(bg_surface, (0, 0))
    else:
        screen.fill(BG_FALLBACK)

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

    draw_hud()
    draw_feedback()

    if paused:
        draw_pause_menu()
        return

    if game_over:
        ov = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 170))
        screen.blit(ov, (0, 0))
        t1 = font_big.render("GAME OVER", True, WHITE)
        t2 = font_mid.render(f"Final Score: {score}", True, WHITE)
        t3 = font_hud.render("Press R to restart  |  ESC to quit",
                             True, (200, 200, 200))
        screen.blit(t1, (WINDOW_W // 2 - t1.get_width() // 2, WINDOW_H // 2 - 80))
        screen.blit(t2, (WINDOW_W // 2 - t2.get_width() // 2, WINDOW_H // 2))
        screen.blit(t3, (WINDOW_W // 2 - t3.get_width() // 2, WINDOW_H // 2 + 50))

def draw_feedback():
    global feedback_timer
    if feedback_timer <= 0 or feedback_type is None:
        return
    cx = WINDOW_W // 2
    cy = WINDOW_H // 2
    if feedback_type == "correct":
        draw_checkmark(cx, cy, size=70, color=CORRECT_GREEN)
    else:
        draw_crossmark(cx, cy, size=70, color=WRONG_ORANGE)

# ====================================================================
#  HUD
# ====================================================================
def draw_hud():
    # دکمه Pause
    mouse_pos = pygame.mouse.get_pos()
    hovered = PAUSE_RECT.collidepoint(mouse_pos)
    btn_bg = (34, 34, 34) if hovered else BLACK
    pygame.draw.rect(screen, btn_bg, PAUSE_RECT)
    bar_w, bar_h = 5, 22
    gap = 8
    total_w = bar_w * 2 + gap
    sx = PAUSE_RECT.centerx - total_w // 2
    sy = PAUSE_RECT.centery - bar_h // 2
    pygame.draw.rect(screen, PAUSE_BAR, (sx, sy, bar_w, bar_h))
    pygame.draw.rect(screen, PAUSE_BAR, (sx + bar_w + gap, sy, bar_w, bar_h))

    # TIME
    pygame.draw.rect(screen, HUD_BG, TIME_RECT)
    lbl = font_hud.render("TIME", True, WHITE)
    val = font_hud.render(f"0:{time_left:02d}", True, WHITE)
    pad = 12
    screen.blit(lbl, (TIME_RECT.x + pad, TIME_RECT.centery - lbl.get_height() // 2))
    screen.blit(val, (TIME_RECT.right - val.get_width() - pad,
                      TIME_RECT.centery - val.get_height() // 2))

    # SCORE
    pygame.draw.rect(screen, HUD_BG, SCORE_RECT)
    lbl = font_hud.render("SCORE", True, WHITE)
    val = font_hud.render(str(score), True, WHITE)
    screen.blit(lbl, (SCORE_RECT.x + pad, SCORE_RECT.centery - lbl.get_height() // 2))
    screen.blit(val, (SCORE_RECT.right - val.get_width() - pad,
                      SCORE_RECT.centery - val.get_height() // 2))

    # Meter — ۴ نقطه
    pygame.draw.rect(screen, HUD_BG, METER_RECT)
    dot_r = 7
    dot_gap = 18
    n_dots = 4
    total_dots_w = (n_dots - 1) * dot_gap + dot_r * 2
    # xN عرض تقریبی
    xN_txt = font_hud.render(f"x{multiplier}", True, WHITE)
    right_pad = 10
    xN_w = xN_txt.get_width()
    dots_start_x = METER_RECT.x + (METER_RECT.width - xN_w - right_pad - total_dots_w) // 2 + dot_r
    for i in range(n_dots):
        dx = dots_start_x + i * dot_gap
        c = DOT_ON if i < meter else DOT_OFF
        pygame.draw.circle(screen, c, (dx, METER_RECT.centery), dot_r)
    screen.blit(xN_txt, (METER_RECT.right - xN_w - right_pad,
                         METER_RECT.centery - xN_txt.get_height() // 2))

    # POINTING / MOVING
    p_bg = POINTING_ACTIVE if mode == "pointing" else BTN_INACTIVE
    m_bg = MOVING_ACTIVE if mode == "moving" else BTN_INACTIVE
    p_fg = WHITE if mode == "pointing" else BTN_TEXT_INACTIVE
    m_fg = WHITE if mode == "moving" else BTN_TEXT_INACTIVE

    pygame.draw.rect(screen, p_bg, POINT_RECT)
    txt = font_btn.render("POINTING", True, p_fg)
    screen.blit(txt, (POINT_RECT.centerx - txt.get_width() // 2,
                      POINT_RECT.centery - txt.get_height() // 2))

    pygame.draw.rect(screen, m_bg, MOVE_RECT)
    txt = font_btn.render("MOVING", True, m_fg)
    screen.blit(txt, (MOVE_RECT.centerx - txt.get_width() // 2,
                      MOVE_RECT.centery - txt.get_height() // 2))

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
    if meter >= 4:          # ← ۴ نقطه
        multiplier = min(multiplier + 1, 10)
        meter = 0

def penalize():
    global multiplier, meter
    if meter > 0:
        meter = 0
    else:
        multiplier = max(multiplier - 1, 1)

# ====================================================================
#  بررسی پاسخ
# ====================================================================
def check(player_dir):
    global mode, pointing_dir, moving_dir, orange_visual_dir
    global feedback_type, feedback_timer

    if game_over or paused:
        return

    if mode == "pointing":
        correct = (pointing_dir == player_dir)
    else:
        correct = (moving_dir == player_dir)

    if correct:
        add_score()
        feedback_type = "correct"
        feedback_timer = 400
        if not muted and SFX_CORRECT_1:
            SFX_CORRECT_1.play()
            pygame.time.set_timer(pygame.USEREVENT + 5, 90, loops=1)
    else:
        penalize()
        feedback_type = "wrong"
        feedback_timer = 400
        if not muted and SFX_WRONG_1:
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
#  حلقهٔ اصلی
# ====================================================================
TIMER_EVENT  = pygame.USEREVENT + 1
SFX2_CORRECT = pygame.USEREVENT + 5
SFX2_WRONG   = pygame.USEREVENT + 6

pygame.time.set_timer(TIMER_EVENT, 1000)

spawn_leaves()
running = True
last_frame_ms = pygame.time.get_ticks()

while running:
    now_ms = pygame.time.get_ticks()
    dt_ms = now_ms - last_frame_ms
    last_frame_ms = now_ms

    if feedback_timer > 0:
        feedback_timer -= dt_ms

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == TIMER_EVENT:
            if not game_over and not paused:
                if time_left > 0:
                    time_left -= 1
                else:
                    game_over = True
                    score += 250 * multiplier

        elif event.type == SFX2_CORRECT:
            if not muted and SFX_CORRECT_2:
                SFX_CORRECT_2.play()

        elif event.type == SFX2_WRONG:
            if not muted and SFX_WRONG_2:
                SFX_WRONG_2.play()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if PAUSE_RECT.collidepoint(event.pos):
                if not game_over:
                    paused = not paused
                    continue
            # کلیک روی آیتم‌های منو
            if paused:
                update_menu_rects()
                for item in menu_items:
                    if item.rect.collidepoint(event.pos):
                        item.action()
                        break

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not game_over:
                    paused = not paused
                continue

            if event.key == pygame.K_ESCAPE:
                if game_over:
                    running = False
                elif paused:
                    paused = False
                else:
                    paused = True
                continue

            if event.key == pygame.K_r and game_over:
                restart_game()
                continue

            if paused:
                continue

            if event.key in (pygame.K_UP, pygame.K_w):
                check("^^^^^")
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                check("vvvvv")
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                check("<<<<<")
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                check(">>>>>")

    move_leaves()
    draw_scene()
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
print("Game closed cleanly.")