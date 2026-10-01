"""
====================================================================
EBB AND FLOW — PYTHON RECREATION (v3 — Fixed Directions + Mouse Pause)
====================================================================
تغییرات نسخه ۳:
  • جهت برگ نارنجی = جهت حرکت (moving_dir) — مطابق قوانین Lumosity
  • جهت برگ سبز  = جهت اشاره (pointing_dir) — مطابق قوانین Lumosity
  • دکمه Pause با موس هم کار می‌کند (کلیک روی دکمه)
  • خطاهای جهتی برطرف شد
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

WINDOW_W, WINDOW_H = 1140, 680
GAME_TOP, GAME_BOTTOM = 70, 600
FPS = 60

screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
pygame.display.set_caption("Ebb and Flow")
clock = pygame.time.Clock()

# ====================================================================
#  رنگ‌ها
# ====================================================================
LEAF_GREEN        = (0x5A, 0xBE, 0x52)
LEAF_GREEN_LIGHT  = (0x8E, 0xE9, 0x67)
LEAF_ORANGE       = (0xFE, 0xC2, 0x0D)
LEAF_ORANGE_LIGHT = (0xFF, 0xD9, 0x55)
LEAF_OUTLINE      = (0xFF, 0xFF, 0xFF)

WHITE      = (0xFF, 0xFF, 0xFF)
BLACK      = (0x00, 0x00, 0x00)
HUD_BG     = (0x3A, 0x3A, 0x3A)
DOT_ON     = (0xFF, 0xFF, 0xFF)
DOT_OFF    = (0x55, 0x55, 0x55)
PAUSE_BAR  = (0x4D, 0xD0, 0xE1)

POINTING_ACTIVE   = (0x4C, 0xAF, 0x50)
MOVING_ACTIVE     = (0xF5, 0xA6, 0x23)
BTN_INACTIVE      = (0xAA, 0xAA, 0xAA)
BTN_TEXT_INACTIVE = (0x33, 0x33, 0x33)

CORRECT_GREEN = (0x4C, 0xE0, 0x4C)
WRONG_RED     = (0xFF, 0x44, 0x44)

BG_FALLBACK = (0x0A, 0x1A, 0x2E)

LEAF_W, LEAF_H = 55, 100

# دکمه Pause
PAUSE_RECT = pygame.Rect(20, 15, 40, 40)

# ====================================================================
#  پس‌زمینه
# ====================================================================
BG_CANDIDATES = [
    r"C:\Users\ASUS\Downloads\Texture237.png",
    r"C:\Users\ASUS\Downloads\TexturePNG\Texture237.png",
]

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
        dark.fill((0, 0, 0, 55))
        surf.blit(dark, (0, 0))
        surf = surf.convert()
        print(f"[BG] loaded OK from {path}")
        return surf
    except Exception as e:
        print(f"[BG] failed: {e}")
        return None

bg_surface = load_background()

# ====================================================================
#  صدای مصنوعی
# ====================================================================
def make_tone(freq, duration_ms, volume=0.35, wave="sine"):
    if not AUDIO_OK:
        return None
    sample_rate = 44100
    n_samples = int(sample_rate * duration_ms / 1000)
    buf = array.array("h")
    for i in range(n_samples):
        t = i / sample_rate
        if wave == "sine":
            v = math.sin(2 * math.pi * freq * t)
        elif wave == "square":
            v = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
        else:
            v = math.sin(2 * math.pi * freq * t)
        fade_start = int(n_samples * 0.7)
        if i > fade_start:
            v *= 1.0 - (i - fade_start) / (n_samples - fade_start)
        buf.append(int(v * volume * 32767))
    try:
        return pygame.mixer.Sound(buffer=buf.tobytes())
    except Exception as e:
        print(f"[Audio] tone {freq}Hz failed: {e}")
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

font_hud  = make_font(22, True)
font_btn  = make_font(24, True)
font_big  = make_font(56, True)
font_mid  = make_font(36, True)
font_feed = make_font(64, True)

# ====================================================================
#  حالت بازی
# ====================================================================
DIRS = [">>>>>", "<<<<<", "^^^^^", "vvvvv"]

mode          = random.choice(["pointing", "moving"])
pointing_dir  = random.choice(DIRS)
moving_dir    = random.choice(DIRS)

score      = 0
time_left  = 60
multiplier = 1
meter      = 0
game_over  = False
paused     = False

NUM_LEAVES = 9
leaves     = []

feedback_text  = ""
feedback_color = WHITE
feedback_timer = 0

# ====================================================================
#  حرکت: هر برگ با سرعت و فاز خودش (شبیه بازی اصلی)
# ====================================================================
def spawn_leaves():
    """همهٔ برگ‌ها با یه جهت حرکت مشترک، ولی در مکان‌های تصادفی"""
    global leaves
    leaves = []
    for _ in range(NUM_LEAVES):
        x = random.randint(40, WINDOW_W - LEAF_W - 40)
        y = random.randint(GAME_TOP + 40, GAME_BOTTOM - LEAF_H - 40)
        leaves.append([x, y])

# ====================================================================
#  ساخت سطح برگ
# ====================================================================
def make_leaf_surface(body_color, light_color, direction):
    pad = 40
    w, h = LEAF_W + pad * 2, LEAF_H + pad * 2
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    cx, cy = w // 2, h // 2
    rx, ry = LEAF_W // 2, LEAF_H // 2

    if direction == ">>>>>":   rot = 0
    elif direction == "vvvvv": rot = math.pi / 2
    elif direction == "<<<<<": rot = math.pi
    else:                       rot = -math.pi / 2

    pts = []
    N = 48
    for i in range(N):
        t = i / N * 2 * math.pi
        spike = 1.0 + 0.35 * max(0, math.cos(t)) ** 2
        px = rx * math.cos(t) * spike
        py = ry * math.sin(t)
        rxp = px * math.cos(rot) - py * math.sin(rot)
        ryp = px * math.sin(rot) + py * math.cos(rot)
        pts.append((cx + rxp, cy + ryp))

    pygame.draw.polygon(surf, body_color, pts)
    pygame.draw.polygon(surf, LEAF_OUTLINE, pts, 4)

    if direction in (">>>>>", "<<<<<"):
        pygame.draw.line(surf, light_color,
                         (cx - rx * 0.65, cy), (cx + rx * 0.65, cy), 5)
    else:
        pygame.draw.line(surf, light_color,
                         (cx, cy - ry * 0.65), (cx, cy + ry * 0.65), 5)

    stem_len, stem_w = 22, 9
    if direction == ">>>>>":
        rect = pygame.Rect(cx - rx - stem_len, cy - stem_w // 2, stem_len, stem_w)
    elif direction == "<<<<<":
        rect = pygame.Rect(cx + rx, cy - stem_w // 2, stem_len, stem_w)
    elif direction == "^^^^^":
        rect = pygame.Rect(cx - stem_w // 2, cy + ry, stem_w, stem_len)
    else:
        rect = pygame.Rect(cx - stem_w // 2, cy - ry - stem_len, stem_w, stem_len)
    pygame.draw.rect(surf, body_color, rect)
    pygame.draw.rect(surf, LEAF_OUTLINE, rect, 2)

    return surf

_leaf_cache = {}
def get_leaf(body_color, light_color, direction):
    key = (body_color, light_color, direction)
    if key not in _leaf_cache:
        _leaf_cache[key] = make_leaf_surface(body_color, light_color, direction)
    return _leaf_cache[key]

# ====================================================================
#  رسم صحنه
# ====================================================================
def draw_scene():
    if bg_surface:
        screen.blit(bg_surface, (0, 0))
    else:
        screen.fill(BG_FALLBACK)

    # ------- قانون Lumosity -------
    # سبز → برگ باید در جهت «اشاره» رسم شود
    # نارنجی → برگ باید در جهت «حرکت» رسم شود
    if mode == "pointing":
        body, light = LEAF_GREEN, LEAF_GREEN_LIGHT
        draw_dir = pointing_dir          # ← جهت اشاره
    else:
        body, light = LEAF_ORANGE, LEAF_ORANGE_LIGHT
        draw_dir = moving_dir            # ← جهت حرکت

    # رسم برگ‌ها
    surf = get_leaf(body, light, draw_dir)
    sw, sh = surf.get_size()
    off_x = (sw - LEAF_W) // 2
    off_y = (sh - LEAF_H) // 2
    for lx, ly in leaves:
        screen.blit(surf, (lx - off_x, ly - off_y))

    draw_hud()
    draw_feedback()

    if paused and not game_over:
        ov = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 130))
        screen.blit(ov, (0, 0))
        txt = font_big.render("PAUSED", True, WHITE)
        screen.blit(txt, (WINDOW_W // 2 - txt.get_width() // 2,
                          WINDOW_H // 2 - txt.get_height() // 2))
        hint = font_hud.render("Press SPACE to resume or click pause button", True, (200, 200, 200))
        screen.blit(hint, (WINDOW_W // 2 - hint.get_width() // 2,
                           WINDOW_H // 2 + 50))

    if game_over:
        ov = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 170))
        screen.blit(ov, (0, 0))
        t1 = font_big.render("GAME OVER", True, WHITE)
        t2 = font_mid.render(f"Final Score: {score}", True, WHITE)
        t3 = font_hud.render("Press R to restart  |  ESC to quit", True, (200, 200, 200))
        screen.blit(t1, (WINDOW_W // 2 - t1.get_width() // 2, WINDOW_H // 2 - 90))
        screen.blit(t2, (WINDOW_W // 2 - t2.get_width() // 2, WINDOW_H // 2 + 10))
        screen.blit(t3, (WINDOW_W // 2 - t3.get_width() // 2, WINDOW_H // 2 + 70))

def draw_feedback():
    global feedback_timer
    if feedback_timer <= 0:
        return
    txt = font_feed.render(feedback_text, True, feedback_color)
    sh = font_feed.render(feedback_text, True, (0, 0, 0))
    x = WINDOW_W // 2 - txt.get_width() // 2
    y = WINDOW_H // 2 - txt.get_height() // 2
    screen.blit(sh, (x + 3, y + 3))
    screen.blit(txt, (x, y))

def draw_hud():
    # ---- دکمه Pause ----
    # اگه موس روشه، رنگ روشن‌تر
    mouse_pos = pygame.mouse.get_pos()
    hovered = PAUSE_RECT.collidepoint(mouse_pos)
    btn_bg = (0x22, 0x22, 0x22) if hovered else BLACK
    pygame.draw.rect(screen, btn_bg, PAUSE_RECT)
    pygame.draw.rect(screen, PAUSE_BAR, (30, 25, 5, 20))
    pygame.draw.rect(screen, PAUSE_BAR, (45, 25, 5, 20))

    # ---- TIME ----
    pygame.draw.rect(screen, HUD_BG, (510, 10, 170, 50))
    txt = font_hud.render(f"TIME    0:{time_left:02d}", True, WHITE)
    screen.blit(txt, (525, 25))

    # ---- SCORE ----
    pygame.draw.rect(screen, HUD_BG, (690, 10, 220, 50))
    txt = font_hud.render(f"SCORE    {score}", True, WHITE)
    screen.blit(txt, (705, 25))

    # ---- Meter ----
    pygame.draw.rect(screen, HUD_BG, (920, 10, 200, 50))
    for i in range(5):
        dx = 945 + i * 22
        c = DOT_ON if i < meter else DOT_OFF
        pygame.draw.circle(screen, c, (dx + 7, 35), 7)
    txt = font_hud.render(f"x{multiplier}", True, WHITE)
    screen.blit(txt, (1070, 25))

    # ---- POINTING / MOVING ----
    px1, py1, px2, py2 = 360, 610, 560, 670
    mx1, my1, mx2, my2 = 560, 610, 760, 670

    p_bg = POINTING_ACTIVE if mode == "pointing" else BTN_INACTIVE
    m_bg = MOVING_ACTIVE if mode == "moving" else BTN_INACTIVE
    p_fg = WHITE if mode == "pointing" else BTN_TEXT_INACTIVE
    m_fg = WHITE if mode == "moving" else BTN_TEXT_INACTIVE

    pygame.draw.rect(screen, p_bg, (px1, py1, px2 - px1, py2 - py1))
    txt = font_btn.render("POINTING", True, p_fg)
    screen.blit(txt, ((px1 + px2) // 2 - txt.get_width() // 2,
                      (py1 + py2) // 2 - txt.get_height() // 2))

    pygame.draw.rect(screen, m_bg, (mx1, my1, mx2 - mx1, my2 - my1))
    txt = font_btn.render("MOVING", True, m_fg)
    screen.blit(txt, ((mx1 + mx2) // 2 - txt.get_width() // 2,
                      (my1 + my2) // 2 - txt.get_height() // 2))

# ====================================================================
#  حرکت برگ‌ها
# ====================================================================
def move_leaves():
    global leaves
    if game_over or paused:
        return
    step = 3
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
    if meter >= 5:
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
    global mode, pointing_dir, moving_dir
    global feedback_text, feedback_color, feedback_timer

    if game_over or paused:
        return

    if mode == "pointing":
        correct = (pointing_dir == player_dir)
    else:
        correct = (moving_dir == player_dir)

    if correct:
        add_score()
        feedback_text = "Correct!"
        feedback_color = CORRECT_GREEN
        feedback_timer = 500
        if SFX_CORRECT_1: SFX_CORRECT_1.play()
        pygame.time.set_timer(pygame.USEREVENT + 5, 90, loops=1)
    else:
        penalize()
        feedback_text = "Wrong!"
        feedback_color = WRONG_RED
        feedback_timer = 500
        if SFX_WRONG_1: SFX_WRONG_1.play()
        pygame.time.set_timer(pygame.USEREVENT + 6, 130, loops=1)

    # سؤال جدید
    mode = random.choice(["pointing", "moving"])
    pointing_dir = random.choice(DIRS)
    moving_dir = random.choice(DIRS)
    spawn_leaves()

# ====================================================================
#  ریست
# ====================================================================
def restart_game():
    global mode, pointing_dir, moving_dir
    global score, time_left, multiplier, meter, game_over, paused
    global feedback_timer

    mode = random.choice(["pointing", "moving"])
    pointing_dir = random.choice(DIRS)
    moving_dir = random.choice(DIRS)

    score = 0
    time_left = 60
    multiplier = 1
    meter = 0
    game_over = False
    paused = False
    feedback_timer = 0

    spawn_leaves()

# ====================================================================
#  حلقهٔ اصلی
# ====================================================================
TIMER_EVENT = pygame.USEREVENT + 1
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
            if SFX_CORRECT_2: SFX_CORRECT_2.play()

        elif event.type == SFX2_WRONG:
            if SFX_WRONG_2: SFX_WRONG_2.play()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # کلیک روی دکمه Pause
            if PAUSE_RECT.collidepoint(event.pos):
                if not game_over:
                    paused = not paused

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not game_over:
                    paused = not paused
                continue

            if event.key == pygame.K_ESCAPE:
                if game_over:
                    running = False
                else:
                    paused = not paused
                continue

            if event.key == pygame.K_r and game_over:
                restart_game()
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