"""
====================================================================
EBB AND FLOW — PYTHON RECREATION
====================================================================
بر اساس:
  • مستندات رسمی Lumosity (قوانین بازی)
  • assetهای استخراج‌شده از bundle بازی
  • اسکرین‌شات‌های واقعی بازی

داده‌های استخراج‌شده از asset:
  • leaf1Sprite  : 70.955 × 130.4    (نسبت ≈ 1:1.84)
  • LeafGreen    : #5ABE52            (متریال برگ سبز)
  • LeafOrange   : #FEC20D            (متریال برگ نارنجی)
  • پس‌زمینه      : Texture237.png      (1282×2048)
  • Shader       : Custom/Leaf (گرادیان عمودی)
  • _leafSpacingX = 9 ,  _leafSpacingY = 4.5

قوانین بازی (از مستندات Lumosity):
  • برگ سبز  → جهت اشاره (POINTING)
  • برگ نارنجی → جهت حرکت (MOVING)
  • امتیاز پاسخ درست  = 50 × Multiplier
  • Meter 5 نقطه → Multiplier +1
  • پاداش پایان بازی  = 250 × Multiplier نهایی

اجرا:
  pip install pygame-ce pillow
  python game.py
====================================================================
"""

import pygame
import random
import math
import os

# ====================================================================
#  مقداردهی اولیه
# ====================================================================
pygame.init()
pygame.font.init()

WINDOW_W, WINDOW_H = 1140, 680
GAME_TOP, GAME_BOTTOM = 70, 600
FPS = 60

screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
pygame.display.set_caption("Ebb and Flow")
clock = pygame.time.Clock()

# ====================================================================
#  رنگ‌ها — مستقیماً از متریال‌های استخراج‌شده
# ====================================================================
LEAF_GREEN        = (0x5A, 0xBE, 0x52)
LEAF_GREEN_LIGHT  = (0x8E, 0xE9, 0x67)
LEAF_ORANGE       = (0xFE, 0xC2, 0x0D)
LEAF_ORANGE_LIGHT = (0xFF, 0xD9, 0x55)
LEAF_OUTLINE      = (0xFF, 0xFF, 0xFF)

WHITE      = (0xFF, 0xFF, 0xFF)
BLACK      = (0x00, 0x00, 0x00)
HUD_BG     = (0x3A, 0x3A, 0x3A)
HUD_BG2    = (0x4A, 0x4A, 0x4A)
DOT_ON     = (0xFF, 0xFF, 0xFF)
DOT_OFF    = (0x55, 0x55, 0x55)
PAUSE_BAR  = (0x4D, 0xD0, 0xE1)

POINTING_ACTIVE   = (0x4C, 0xAF, 0x50)
MOVING_ACTIVE     = (0xF5, 0xA6, 0x23)
BTN_INACTIVE      = (0xAA, 0xAA, 0xAA)
BTN_TEXT_INACTIVE = (0x33, 0x33, 0x33)

BG_FALLBACK = (0x0A, 0x1A, 0x2E)

# ====================================================================
#  ابعاد برگ — از leaf1Sprite
# ====================================================================
LEAF_W, LEAF_H = 55, 100

# ====================================================================
#  مسیر فایل پس‌زمینه
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

# ====================================================================
#  بارگذاری پس‌زمینه
# ====================================================================
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
#  فونت‌ها
# ====================================================================
def make_font(size, bold=True):
    for name in ("Segoe UI", "Arial", "Tahoma", "Verdana"):
        try:
            return pygame.font.SysFont(name, size, bold=bold)
        except Exception:
            continue
    return pygame.font.Font(None, size)

font_hud = make_font(22, True)
font_btn = make_font(24, True)
font_big = make_font(56, True)
font_mid = make_font(36, True)

# ====================================================================
#  جهت‌ها
# ====================================================================
DIRS = [">>>>>", "<<<<<", "^^^^^", "vvvvv"]

# ====================================================================
#  حالت بازی
# ====================================================================
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

def spawn_leaves():
    global leaves
    leaves = []
    for _ in range(NUM_LEAVES):
        x = random.randint(40, WINDOW_W - LEAF_W - 40)
        y = random.randint(GAME_TOP + 40, GAME_BOTTOM - LEAF_H - 40)
        leaves.append([x, y])

# ====================================================================
#  ساخت سطح برگ (بار اول برای هر ترکیب — بعد از کش استفاده می‌شود)
# ====================================================================
def make_leaf_surface(body_color, light_color, direction):
    """
    برگ قطره‌ای/قلبی با:
      - بدنه رنگ اصلی
      - خط دور سفید ضخیم
      - خط روشن وسط (شبیه گرادیان Shader Custom/Leaf)
      - دم (ساقه) در پشت
    """
    pad = 40
    w, h = LEAF_W + pad * 2, LEAF_H + pad * 2
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    cx, cy = w // 2, h // 2
    rx, ry = LEAF_W // 2, LEAF_H // 2

    # زاویه‌ی چرخش بر اساس جهت
    if direction == ">>>>>":
        rot = 0
    elif direction == "vvvvv":
        rot = math.pi / 2
    elif direction == "<<<<<":
        rot = math.pi
    else:  # ^^^^^
        rot = -math.pi / 2

    # ---------- نقاط شکل برگ ----------
    pts = []
    N = 48
    for i in range(N):
        t = i / N * 2 * math.pi
        # نوک تیز در جهت +x (بعداً چرخانده می‌شود)
        spike = 1.0 + 0.35 * max(0, math.cos(t)) ** 2
        px = rx * math.cos(t) * spike
        py = ry * math.sin(t)
        # چرخش
        rxp = px * math.cos(rot) - py * math.sin(rot)
        ryp = px * math.sin(rot) + py * math.cos(rot)
        pts.append((cx + rxp, cy + ryp))

    # بدنه
    pygame.draw.polygon(surf, body_color, pts)
    # خط دور سفید
    pygame.draw.polygon(surf, LEAF_OUTLINE, pts, 4)

    # ---------- خط روشن وسط ----------
    if direction in (">>>>>", "<<<<<"):
        pygame.draw.line(surf, light_color,
                         (cx - rx * 0.65, cy), (cx + rx * 0.65, cy), 5)
    else:
        pygame.draw.line(surf, light_color,
                         (cx, cy - ry * 0.65), (cx, cy + ry * 0.65), 5)

    # ---------- دم (ساقه) ----------
    stem_len, stem_w = 22, 9
    if direction == ">>>>>":
        rect = pygame.Rect(cx - rx - stem_len, cy - stem_w // 2, stem_len, stem_w)
    elif direction == "<<<<<":
        rect = pygame.Rect(cx + rx, cy - stem_w // 2, stem_len, stem_w)
    elif direction == "^^^^^":
        rect = pygame.Rect(cx - stem_w // 2, cy + ry, stem_w, stem_len)
    else:  # vvvvv
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
#  رسم کل صحنه
# ====================================================================
def draw_scene():
    # پس‌زمینه
    if bg_surface:
        screen.blit(bg_surface, (0, 0))
    else:
        screen.fill(BG_FALLBACK)

    # رنگ و جهت بر اساس mode
    if mode == "pointing":
        body, light = LEAF_GREEN, LEAF_GREEN_LIGHT
        direction = pointing_dir
    else:
        body, light = LEAF_ORANGE, LEAF_ORANGE_LIGHT
        direction = moving_dir

    # رسم برگ‌ها
    surf = get_leaf(body, light, direction)
    sw, sh = surf.get_size()
    off_x = (sw - LEAF_W) // 2
    off_y = (sh - LEAF_H) // 2
    for lx, ly in leaves:
        screen.blit(surf, (lx - off_x, ly - off_y))

    # HUD
    draw_hud()

    # Pause
    if paused and not game_over:
        ov = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 130))
        screen.blit(ov, (0, 0))
        txt = font_big.render("PAUSED", True, WHITE)
        screen.blit(txt, (WINDOW_W // 2 - txt.get_width() // 2,
                          WINDOW_H // 2 - txt.get_height() // 2))

    # Game Over
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

def draw_hud():
    # ---- دکمه Pause گوشه بالا چپ ----
    pygame.draw.rect(screen, BLACK, (20, 15, 40, 40))
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

    # ---- Meter (5 نقطه) + Multiplier ----
    pygame.draw.rect(screen, HUD_BG, (920, 10, 200, 50))
    for i in range(5):
        dx = 945 + i * 22
        c = DOT_ON if i < meter else DOT_OFF
        pygame.draw.circle(screen, c, (dx + 7, 35), 7)
    txt = font_hud.render(f"x{multiplier}", True, WHITE)
    screen.blit(txt, (1070, 25))

    # ---- نوار POINTING / MOVING پایین ----
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
            if lx > WINDOW_W + 20:
                lx = -LEAF_W - 20
        elif moving_dir == "<<<<<":
            lx -= step
            if lx < -LEAF_W - 20:
                lx = WINDOW_W + 20
        elif moving_dir == "^^^^^":
            ly -= step
            if ly < GAME_TOP - 20:
                ly = GAME_BOTTOM + 20
        elif moving_dir == "vvvvv":
            ly += step
            if ly > GAME_BOTTOM + 20:
                ly = GAME_TOP - 20
        new_leaves.append([lx, ly])
    leaves = new_leaves

# ====================================================================
#  امتیازدهی
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
    if game_over or paused:
        return

    if mode == "pointing":
        correct = (pointing_dir == player_dir)
    else:
        correct = (moving_dir == player_dir)

    if correct:
        add_score()
    else:
        penalize()

    # سؤال جدید
    mode = random.choice(["pointing", "moving"])
    pointing_dir = random.choice(DIRS)
    moving_dir = random.choice(DIRS)
    spawn_leaves()

# ====================================================================
#  ریست بازی
# ====================================================================
def restart_game():
    global mode, pointing_dir, moving_dir
    global score, time_left, multiplier, meter, game_over, paused

    mode = random.choice(["pointing", "moving"])
    pointing_dir = random.choice(DIRS)
    moving_dir = random.choice(DIRS)

    score = 0
    time_left = 60
    multiplier = 1
    meter = 0
    game_over = False
    paused = False

    spawn_leaves()

# ====================================================================
#  حلقه‌ی اصلی
# ====================================================================
TIMER_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(TIMER_EVENT, 1000)

spawn_leaves()
running = True

while running:
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

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over:
                restart_game()
            elif event.key in (pygame.K_SPACE, pygame.K_ESCAPE):
                if not game_over:
                    paused = not paused
                elif event.key == pygame.K_ESCAPE:
                    running = False
            elif event.key in (pygame.K_UP, pygame.K_w):
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