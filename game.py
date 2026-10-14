"""
====================================================================
EBB AND FLOW — PYTHON RECREATION (v29.1)
====================================================================
تغییرات نسبت به v29:
  • HUD بالا شیشه‌ای‌تر (180)
  • HUD پایین رنگی یکسان با حالت 123 (خاکستری شیشه‌ای، متن سفید)
  • دکمه Pause شیشه‌ای
  • دایره‌های Meter خالی روشن‌تر برای وضوح
====================================================================
"""

import pygame
import random
import math
import os

# ====================================================================
# راه‌اندازی
# ====================================================================
pygame.init()
pygame.font.init()

try:
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    AUDIO_OK = True
except Exception:
    AUDIO_OK = False

WINDOW_W, WINDOW_H = 800, 600
GAME_TOP, GAME_BOTTOM = 50, 520
FPS = 60

screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
pygame.display.set_caption("Ebb and Flow")
clock = pygame.time.Clock()

# ====================================================================
# رنگ‌ها
# ====================================================================
LEAF_GREEN        = (76, 175, 80)
LEAF_GREEN_LIGHT  = (126, 217, 87)
LEAF_ORANGE       = (245, 166, 35)
LEAF_ORANGE_LIGHT = (255, 217, 102)
LEAF_OUTLINE      = (255, 255, 255)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

COUNTDOWN_BLUE = (36, 152, 178)

# HUD ها شیشه‌ای
HUD_BG   = (150, 160, 175, 180)
HUD_TEXT = (25, 30, 40)

# دایره‌های Meter — پر تیره، خالی روشن
DOT_ON  = (30, 35, 45)
DOT_OFF = (200, 205, 215, 230)

PAUSE_BAR = (77, 208, 225)

# دکمه فعال — رنگی، بدون شیشه
POINTING_ACTIVE   = (76, 175, 80)
MOVING_ACTIVE     = (245, 166, 35)

# دکمه غیرفعال — شیشه‌ای، متن سفید (یکسان با حالت 123)
BTN_INACTIVE      = (110, 120, 135, 180)
BTN_TEXT_INACTIVE = WHITE

COUNTDOWN_BTN_BG = (110, 120, 135, 180)
COUNTDOWN_BTN_FG = WHITE

CORRECT_GREEN = (138, 204, 66)
WRONG_RED     = (245, 130, 32)

MENU_ITEM_BG    = (25, 40, 60)
MENU_ITEM_HOVER = (45, 180, 235)
MENU_TEXT       = (100, 200, 245)
MENU_TEXT_HOVER = (255, 255, 255)

BG_FALLBACK = (10, 26, 46)

LEAF_W, LEAF_H = 60, 110

# ====================================================================
# قوانین
# ====================================================================
START_TIME       = 60
BASE_SCORE       = 50
METER_MAX        = 4
MIN_MULTIPLIER   = 1
MAX_MULTIPLIER   = 10
FINAL_BONUS_BASE = 250

COUNTDOWN_START = 3
COUNTDOWN_MS    = 1000

BONUS_MS_PER_POINT = 5
BONUS_MIN_MS       = 1500
BONUS_MAX_MS       = 20000

# ====================================================================
# کادرهای HUD
# ====================================================================
PAUSE_RECT      = pygame.Rect(0, 0, 48, 48)
PAUSE_MENU_RECT = pygame.Rect(0, 0, 150, 48)

HUD_GAP_TOP   = 5
HUD_RIGHT_PAD = 20
HUD_ITEM_H    = 60

TIME_W  = 145
SCORE_W = 165
METER_W = 145

METER_RECT = pygame.Rect(WINDOW_W - HUD_RIGHT_PAD - METER_W, 0, METER_W, HUD_ITEM_H)
SCORE_RECT = pygame.Rect(METER_RECT.left - HUD_GAP_TOP - SCORE_W, 0, SCORE_W, HUD_ITEM_H)
TIME_RECT  = pygame.Rect(SCORE_RECT.left - HUD_GAP_TOP - TIME_W, 0, TIME_W, HUD_ITEM_H)

HUD_GAP_BOTTOM = 10
POINT_W, MOVE_W, BOTTOM_H = 150, 150, 60
BOTTOM_Y = WINDOW_H - BOTTOM_H
TOTAL_BOTTOM_W = POINT_W + MOVE_W + HUD_GAP_BOTTOM
BOTTOM_START_X = (WINDOW_W - TOTAL_BOTTOM_W) // 2

POINT_RECT = pygame.Rect(BOTTOM_START_X, BOTTOM_Y, POINT_W, BOTTOM_H)
MOVE_RECT  = pygame.Rect(POINT_RECT.right + HUD_GAP_BOTTOM, BOTTOM_Y, MOVE_W, BOTTOM_H)

# ====================================================================
# مسیرها
# ====================================================================
ROOT = r"C:\Users\ASUS\Documents\GitHub\Rafiei-tayebe\out"

BG_PATH = os.path.join(ROOT, "tex_scene", "game_background_238.png")

LEAF_GREEN_IMG  = r"C:\Users\ASUS\Downloads\ebb_and_flow_leaf_green.png"
LEAF_ORANGE_IMG = r"C:\Users\ASUS\Downloads\ebb_and_flow_leaf_yellow.png"

ICON_DIR = os.path.join(ROOT, "sprites_shared_assets")
SND_DIR  = os.path.join(ROOT, "sounds", "wav")

ICON_PATHS = {
    "resume":  os.path.join(ICON_DIR, "sharedAssets_resumeSprite_7302.png"),
    "restart": os.path.join(ICON_DIR, "sharedAssets_restartSprite_6898.png"),
    "quit":    os.path.join(ICON_DIR, "sharedAssets_quitSprite_6891.png"),
    "help":    os.path.join(ICON_DIR, "sharedAssets_helpSprite_754.png"),
    "sound":   os.path.join(ICON_DIR, "Soundfx_iconSprite_6307.png"),
    "music":   os.path.join(ICON_DIR, "Music_iconSprite_2749.png"),
    "nosnd":   os.path.join(ICON_DIR, "noSoundfx_iconSprite_3867.png"),
    "nomus":   os.path.join(ICON_DIR, "noMusic_iconSprite_6361.png"),
}

CHECKMARK_PATH = os.path.join(ICON_DIR, "sharedAssets_correctWebSprite_7660.png")
CROSSMARK_PATH = os.path.join(ICON_DIR, "sharedAssets_incorrectWebSprite_4960.png")

# ====================================================================
# آیکن‌ها
# ====================================================================
def load_icon_no_bg(path, size=(28, 28), tolerance=40):
    if not os.path.exists(path):
        return None
    try:
        img = pygame.image.load(path).convert_alpha()
    except Exception:
        return None

    w, h = img.get_size()
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    bg_samples = []
    for c in corners:
        r, g, b, a = img.get_at(c)
        if a > 200:
            bg_samples.append((r, g, b))

    if not bg_samples:
        return pygame.transform.smoothscale(img, size)

    br = sum(c[0] for c in bg_samples) // len(bg_samples)
    bg_c = sum(c[1] for c in bg_samples) // len(bg_samples)
    bb = sum(c[2] for c in bg_samples) // len(bg_samples)

    for x in range(w):
        for y in range(h):
            r, g, b, a = img.get_at((x, y))
            dr, dg, db = abs(r - br), abs(g - bg_c), abs(b - bb)
            total = dr + dg + db

            if total < tolerance:
                img.set_at((x, y), (0, 0, 0, 0))
            elif total < tolerance * 2:
                alpha = int(255 * (total - tolerance) / tolerance)
                img.set_at((x, y), (r, g, b, max(0, min(255, alpha))))

    return pygame.transform.smoothscale(img, size)


def load_colored_mark(path, target_color, size=(90, 90), tolerance=60):
    if not os.path.exists(path):
        return None
    try:
        img = pygame.image.load(path).convert_alpha()
    except Exception:
        return None

    w, h = img.get_size()

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    bg_samples = []
    for c in corners:
        r, g, b, a = img.get_at(c)
        if a > 200:
            bg_samples.append((r, g, b))

    if not bg_samples:
        br, bg_c, bb = 20, 25, 35
    else:
        br = sum(c[0] for c in bg_samples) // len(bg_samples)
        bg_c = sum(c[1] for c in bg_samples) // len(bg_samples)
        bb = sum(c[2] for c in bg_samples) // len(bg_samples)

    tr, tg, tb = target_color
    for x in range(w):
        for y in range(h):
            r, g, b, a = img.get_at((x, y))
            bg_dist = abs(r - br) + abs(g - bg_c) + abs(b - bb)
            brightness = (r + g + b) // 3

            if bg_dist < tolerance:
                img.set_at((x, y), (0, 0, 0, 0))
            elif brightness > 200:
                img.set_at((x, y), (tr, tg, tb, a))
            elif brightness > 150:
                factor = (brightness - 150) / 50.0
                nr = int(tr * factor + r * (1 - factor))
                ng = int(tg * factor + g * (1 - factor))
                nb = int(tb * factor + b * (1 - factor))
                img.set_at((x, y), (nr, ng, nb, a))

    return pygame.transform.smoothscale(img, size)


ICONS = {}
for key, path in ICON_PATHS.items():
    ICONS[key] = load_icon_no_bg(path, size=(28, 28))

CHECKMARK_IMG = load_colored_mark(CHECKMARK_PATH, CORRECT_GREEN, size=(90, 90))
CROSSMARK_IMG = load_colored_mark(CROSSMARK_PATH, WRONG_RED, size=(90, 90))

# ====================================================================
# پس‌زمینه
# ====================================================================
def load_background():
    if not os.path.exists(BG_PATH):
        return None
    try:
        img = pygame.image.load(BG_PATH).convert()
        return pygame.transform.smoothscale(img, (WINDOW_W, WINDOW_H))
    except Exception:
        return None

bg_surface = load_background()

# ====================================================================
# برگ‌ها
# ====================================================================
def load_leaf_image(path):
    if not os.path.exists(path):
        return None
    try:
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.rotate(img, 90)
        return pygame.transform.smoothscale(img, (LEAF_W, LEAF_H))
    except Exception:
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
    if direction == "^^^^^":
        angle = 0
    elif direction == ">>>>>":
        angle = -90
    elif direction == "vvvvv":
        angle = 180
    else:
        angle = 90
    rotated = pygame.transform.rotate(base_img, angle)
    _leaf_rot_cache[key] = rotated
    return rotated

# ====================================================================
# صداها
# ====================================================================
SND = {}

SOUND_FILES = {
    "answerCorrect":         "shared_answerCorrect.wav",
    "answerCorrectX2":       "shared_answerCorrectX2.wav",
    "answerCorrectX3":       "shared_answerCorrectX3.wav",
    "answerCorrectX4":       "shared_answerCorrectX4.wav",
    "answerWrong":           "shared_answerWrong.wav",
    "counterCountLoopable":  "shared_counterCount_loopable.wav",
    "counterEnd":            "shared_counterEnd.wav",
    "gameStart":             "shared_gameStart.wav",
    "gameEnd":               "shared_gameEnd.wav",
    "timer":                 "shared_timer.wav",
    "countdown":             "shared_countdown.wav",
    "windBlow":              "scene_windBlow.wav",
    "WaterStreamActualLoop": "scene_WaterStreamActualLoop.wav",
}

if AUDIO_OK:
    for key, fn in SOUND_FILES.items():
        path = os.path.join(SND_DIR, fn)
        if os.path.exists(path):
            try:
                SND[key] = pygame.mixer.Sound(path)
            except Exception:
                pass

sound_muted = False
music_muted = False

_loop_channels = {}

def play_sfx(name, volume=None):
    if sound_muted or name not in SND:
        return None
    snd = SND[name]
    if volume is not None:
        snd.set_volume(volume)
    snd.play()
    return snd

def stop_sfx(name):
    if name in SND:
        try:
            SND[name].stop()
        except Exception:
            pass

def play_loop(name, volume=0.8):
    if sound_muted or name not in SND:
        return
    try:
        stop_loop(name)
        snd = SND[name]
        snd.set_volume(volume)
        ch = snd.play(loops=-1)
        _loop_channels[name] = ch
    except Exception:
        pass

def stop_loop(name):
    if name in _loop_channels:
        try:
            _loop_channels[name].stop()
        except Exception:
            pass
        _loop_channels.pop(name, None)
    if name in SND:
        try:
            SND[name].stop()
        except Exception:
            pass

# ====================================================================
# موسیقی
# ====================================================================
MUSIC_VOLUME = 0.85
music_playing = False

def start_music():
    global music_playing
    if sound_muted or "WaterStreamActualLoop" not in SND:
        return
    try:
        SND["WaterStreamActualLoop"].set_volume(MUSIC_VOLUME)
        SND["WaterStreamActualLoop"].play(loops=-1)
        music_playing = True
    except Exception:
        pass

def stop_music():
    global music_playing
    if "WaterStreamActualLoop" in SND:
        try:
            SND["WaterStreamActualLoop"].stop()
            music_playing = False
        except Exception:
            pass

# ====================================================================
# فونت‌ها
# ====================================================================
def make_font(size, bold=True):
    for name in ("Segoe UI", "Arial", "Tahoma", "Verdana"):
        try:
            return pygame.font.SysFont(name, size, bold=bold)
        except Exception:
            continue
    return pygame.font.Font(None, size)

font_hud   = make_font(22, True)
font_btn   = make_font(22, True)
font_big   = make_font(44, True)
font_mid   = make_font(28, True)
font_menu  = make_font(22, True)
font_small = make_font(15, False)
font_bonus = make_font(40, True)
font_countdown = make_font(72, True)

# ====================================================================
# حالت بازی
# ====================================================================
DIRS = [">>>>>", "<<<<<", "^^^^^", "vvvvv"]

mode              = random.choice(["pointing", "moving"])
pointing_dir      = random.choice(DIRS)
moving_dir        = random.choice(DIRS)
orange_visual_dir = random.choice(DIRS)

score        = 0
time_left    = START_TIME
multiplier   = MIN_MULTIPLIER
meter        = 0
final_bonus  = 0

game_over    = False
paused       = False
show_howto   = False

countdown_active  = True
countdown_number  = COUNTDOWN_START
countdown_elapsed = 0
countdown_last_played = None

NUM_LEAVES = 7
leaves = []

feedback_type  = None
feedback_timer = 0

bonus_elapsed_ms = 0
bonus_total_ms = BONUS_MAX_MS
bonus_loop_started = False
bonus_end_played = False

score_without_bonus = 0

WIND_START_MS = 3000
pending_gamestart_at = None
pending_music_at = None

# ====================================================================
# رویدادها
# ====================================================================
TIMER_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(TIMER_EVENT, 1000)

# ====================================================================
# توابع صوتی شروع
# ====================================================================
def start_game_audio():
    global pending_gamestart_at, pending_music_at
    if sound_muted:
        return
    play_sfx("windBlow", 0.85)
    now = pygame.time.get_ticks()
    pending_gamestart_at = now + WIND_START_MS
    pending_music_at = now + WIND_START_MS


def cancel_startup_audio():
    global pending_gamestart_at, pending_music_at
    stop_sfx("windBlow")
    stop_music()
    pending_gamestart_at = None
    pending_music_at = None


def stop_all_audio():
    stop_music()
    stop_loop("counterCountLoopable")
    for key in list(SND.keys()):
        try:
            SND[key].stop()
        except Exception:
            pass

# ====================================================================
# محاسبه طول انیمیشن بونوس
# ====================================================================
def compute_bonus_duration_ms(bonus_points):
    ms = bonus_points * BONUS_MS_PER_POINT
    return max(BONUS_MIN_MS, min(BONUS_MAX_MS, ms))

# ====================================================================
# ساخت برگ‌ها
# ====================================================================
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
# منو
# ====================================================================
class MenuItem:
    def __init__(self, key, label_fn, action, icon_key=None):
        self.key = key
        self.label_fn = label_fn
        self.action = action
        self.icon_key = icon_key
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.hover = False
    def get_label(self):
        return self.label_fn()

def menu_resume():
    global paused
    paused = False

def menu_restart():
    global paused
    restart_game()
    paused = False

def menu_toggle_sound():
    global sound_muted
    sound_muted = not sound_muted
    if sound_muted:
        stop_all_audio()

def menu_toggle_music():
    global music_muted
    music_muted = not music_muted
    if music_muted:
        stop_music()
    else:
        start_music()

def menu_quit():
    global running
    running = False

def menu_howto():
    global show_howto
    show_howto = True

def menu_back_from_howto():
    global show_howto
    show_howto = False

def label_resume(): return "Resume"
def label_restart(): return "Restart"
def label_sound():  return "Sound Muted" if sound_muted else "Mute Sound"
def label_music():  return "Music Muted" if music_muted else "Mute Music"
def label_quit():   return "Quit"
def label_howto():  return "How To Play"

menu_items = [
    MenuItem("resume",     label_resume,  menu_resume,        "resume"),
    MenuItem("restart",    label_restart, menu_restart,       "restart"),
    MenuItem("mute_sound", label_sound,   menu_toggle_sound,  "sound"),
    MenuItem("mute_music", label_music,   menu_toggle_music,  "music"),
    MenuItem("quit",       label_quit,    menu_quit,          "quit"),
    MenuItem("howto",      label_howto,   menu_howto,         "help"),
]

MENU_W       = 380
MENU_H_ITEM  = 48
MENU_GAP     = 4
MENU_X       = (WINDOW_W - MENU_W) // 2
MENU_Y_START = 130
MENU_TEXT_LEFT_PAD = 56
MENU_ICON_PAD      = 14

def update_menu_rects():
    for i, item in enumerate(menu_items):
        y = MENU_Y_START + i * (MENU_H_ITEM + MENU_GAP)
        item.rect = pygame.Rect(MENU_X, y, MENU_W, MENU_H_ITEM)

BACK_RECT = pygame.Rect(WINDOW_W // 2 - 80, WINDOW_H - 90, 160, 44)

def get_icon_for(item):
    if item.key == "mute_sound":
        return ICONS.get("nosnd") if sound_muted else ICONS.get("sound")
    if item.key == "mute_music":
        return ICONS.get("nomus") if music_muted else ICONS.get("music")
    return ICONS.get(item.icon_key)

# ====================================================================
# بازخورد بصری
# ====================================================================
def draw_checkmark(cx, cy, size=90, color=CORRECT_GREEN):
    if CHECKMARK_IMG:
        rect = CHECKMARK_IMG.get_rect(center=(cx, cy))
        screen.blit(CHECKMARK_IMG, rect)
        return
    pts = [
        (cx - size * 0.4, cy),
        (cx - size * 0.1, cy + size * 0.3),
        (cx + size * 0.4, cy - size * 0.3),
    ]
    pygame.draw.lines(screen, color, False, pts, 12)

def draw_crossmark(cx, cy, size=90, color=WRONG_RED):
    if CROSSMARK_IMG:
        rect = CROSSMARK_IMG.get_rect(center=(cx, cy))
        screen.blit(CROSSMARK_IMG, rect)
        return
    off = size * 0.35
    pygame.draw.line(screen, color, (cx - off, cy - off), (cx + off, cy + off), 12)
    pygame.draw.line(screen, color, (cx + off, cy - off), (cx - off, cy + off), 12)

# ====================================================================
# دکمه Pause — شیشه‌ای
# ====================================================================
def draw_pause_button_in_game(active=True):
    hovered = PAUSE_RECT.collidepoint(pygame.mouse.get_pos())

    if hovered:
        btn_bg = (45, 180, 235, 220)
    else:
        btn_bg = (0, 0, 0, 130)

    panel = pygame.Surface((PAUSE_RECT.width, PAUSE_RECT.height), pygame.SRCALPHA)
    panel.fill(btn_bg)
    screen.blit(panel, (PAUSE_RECT.x, PAUSE_RECT.y))

    bar_color = WHITE if hovered else PAUSE_BAR

    bar_w, bar_h, gap = 6, 24, 10
    total_w = bar_w * 2 + gap
    sx = PAUSE_RECT.centerx - total_w // 2
    sy = PAUSE_RECT.centery - bar_h // 2

    pygame.draw.rect(screen, bar_color, (sx, sy, bar_w, bar_h))
    pygame.draw.rect(screen, bar_color, (sx + bar_w + gap, sy, bar_w, bar_h))

def draw_pause_button_in_menu():
    hovered = PAUSE_MENU_RECT.collidepoint(pygame.mouse.get_pos())
    bg = WHITE if hovered else (230, 230, 230)
    pygame.draw.rect(screen, bg, PAUSE_MENU_RECT)

    pygame.draw.rect(screen, (40, 40, 40),
                     (PAUSE_MENU_RECT.x + 14, PAUSE_MENU_RECT.y + 14, 5, 20))
    pygame.draw.rect(screen, (40, 40, 40),
                     (PAUSE_MENU_RECT.x + 24, PAUSE_MENU_RECT.y + 14, 5, 20))

    txt = font_menu.render("Paused", True, (40, 40, 40))
    screen.blit(txt, (PAUSE_MENU_RECT.x + 42, PAUSE_MENU_RECT.y + 10))

# ====================================================================
# منوی Pause
# ====================================================================
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

        ic = get_icon_for(item)
        if ic:
            icon_rect = ic.get_rect(
                midleft=(item.rect.x + MENU_ICON_PAD, item.rect.centery))
            screen.blit(ic, icon_rect)

        label_txt = font_menu.render(item.get_label(), True, fg)
        screen.blit(label_txt, (
            item.rect.x + MENU_TEXT_LEFT_PAD,
            item.rect.centery - label_txt.get_height() // 2,
        ))

def draw_howto_panel():
    ht_rect = pygame.Rect(60, 70, WINDOW_W - 120, WINDOW_H - 170)
    pygame.draw.rect(screen, (10, 25, 45), ht_rect)
    pygame.draw.rect(screen, MENU_ITEM_HOVER, ht_rect, 3)

    title = font_mid.render("How To Play", True, WHITE)
    screen.blit(title, (ht_rect.centerx - title.get_width() // 2, ht_rect.y + 20))

    lines = [
        "Green leaves  - press the direction they POINT",
        "Orange leaves - press the direction they MOVE",
        "",
        "Correct = 50 x multiplier",
        "4 correct answers = multiplier +1",
        "Wrong with meter = meter reset",
        "Wrong with empty meter = multiplier -1",
        "Final Bonus = 250 x multiplier",
        "",
        "WASD or arrow keys to answer",
        "Space = pause",
    ]
    for i, line in enumerate(lines):
        t = font_small.render(line, True, WHITE)
        screen.blit(t, (ht_rect.x + 40, ht_rect.y + 80 + i * 28))

    hovered = BACK_RECT.collidepoint(pygame.mouse.get_pos())
    bg = MENU_ITEM_HOVER if hovered else MENU_ITEM_BG
    fg = MENU_TEXT_HOVER if hovered else MENU_TEXT
    pygame.draw.rect(screen, bg, BACK_RECT)

    bt = font_menu.render("Back", True, fg)
    screen.blit(bt, (BACK_RECT.centerx - bt.get_width() // 2,
                     BACK_RECT.centery - bt.get_height() // 2))

# ====================================================================
# HUD
# ====================================================================
def draw_hud_panel(rect, fill_rgba):
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    panel.fill(fill_rgba)
    screen.blit(panel, (rect.x, rect.y))

def draw_hud_top_only(time_override=None, score_override=None,
                      meter_override=None, multiplier_override=None):
    shown_time  = time_left if time_override is None else time_override
    shown_score = score if score_override is None else score_override
    shown_meter = meter if meter_override is None else meter_override
    shown_mult  = multiplier if multiplier_override is None else multiplier_override

    draw_hud_panel(TIME_RECT, HUD_BG)
    lbl = font_hud.render("TIME", True, HUD_TEXT)
    val = font_hud.render(f"0:{shown_time:02d}", True, HUD_TEXT)
    pad = 14
    screen.blit(lbl, (TIME_RECT.x + pad, TIME_RECT.centery - lbl.get_height() // 2))
    screen.blit(val, (TIME_RECT.right - val.get_width() - pad,
                      TIME_RECT.centery - val.get_height() // 2))

    draw_hud_panel(SCORE_RECT, HUD_BG)
    lbl = font_hud.render("SCORE", True, HUD_TEXT)
    val = font_hud.render(str(shown_score), True, HUD_TEXT)
    screen.blit(lbl, (SCORE_RECT.x + pad, SCORE_RECT.centery - lbl.get_height() // 2))
    screen.blit(val, (SCORE_RECT.right - val.get_width() - pad,
                      SCORE_RECT.centery - val.get_height() // 2))

    draw_hud_panel(METER_RECT, HUD_BG)
    dot_r, dot_gap = 8, 20
    n_dots = METER_MAX
    total_dots_w = (n_dots - 1) * dot_gap + dot_r * 2
    xN_txt = font_hud.render(f"x{shown_mult}", True, HUD_TEXT)
    right_pad = 12
    xN_w = xN_txt.get_width()
    dots_start_x = METER_RECT.x + (METER_RECT.width - xN_w - right_pad - total_dots_w) // 2 + dot_r

    for i in range(n_dots):
        dx = dots_start_x + i * dot_gap
        circ = pygame.Surface((dot_r * 2, dot_r * 2), pygame.SRCALPHA)
        color = DOT_ON if i < shown_meter else DOT_OFF
        pygame.draw.circle(circ, color, (dot_r, dot_r), dot_r)
        screen.blit(circ, (dx - dot_r, METER_RECT.centery - dot_r))

    screen.blit(xN_txt, (METER_RECT.right - xN_w - right_pad,
                         METER_RECT.centery - xN_txt.get_height() // 2))

def draw_hud_bottom():
    if mode == "pointing":
        # POINTING فعال — رنگی، بدون شیشه
        pygame.draw.rect(screen, POINTING_ACTIVE, POINT_RECT)
        pt_fg = WHITE
        # MOVING غیرفعال — شیشه‌ای
        panel = pygame.Surface((MOVE_RECT.width, MOVE_RECT.height), pygame.SRCALPHA)
        panel.fill(BTN_INACTIVE)
        screen.blit(panel, (MOVE_RECT.x, MOVE_RECT.y))
        mv_fg = BTN_TEXT_INACTIVE
    else:
        # POINTING غیرفعال — شیشه‌ای
        panel = pygame.Surface((POINT_RECT.width, POINT_RECT.height), pygame.SRCALPHA)
        panel.fill(BTN_INACTIVE)
        screen.blit(panel, (POINT_RECT.x, POINT_RECT.y))
        pt_fg = BTN_TEXT_INACTIVE
        # MOVING فعال — رنگی
        pygame.draw.rect(screen, MOVING_ACTIVE, MOVE_RECT)
        mv_fg = WHITE

    txt = font_btn.render("POINTING", True, pt_fg)
    screen.blit(txt, (POINT_RECT.centerx - txt.get_width() // 2,
                      POINT_RECT.centery - txt.get_height() // 2))

    txt = font_btn.render("MOVING", True, mv_fg)
    screen.blit(txt, (MOVE_RECT.centerx - txt.get_width() // 2,
                      MOVE_RECT.centery - txt.get_height() // 2))

def draw_hud_bottom_countdown():
    for rect, label in ((POINT_RECT, "POINTING"), (MOVE_RECT, "MOVING")):
        panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        panel.fill(COUNTDOWN_BTN_BG)
        screen.blit(panel, (rect.x, rect.y))

        txt = font_btn.render(label, True, COUNTDOWN_BTN_FG)
        screen.blit(txt, (rect.centerx - txt.get_width() // 2,
                          rect.centery - txt.get_height() // 2))

def draw_hud():
    draw_pause_button_in_game(active=True)
    draw_hud_top_only()
    draw_hud_bottom()

# ====================================================================
# Feedback
# ====================================================================
def draw_feedback():
    if feedback_timer <= 0 or feedback_type is None:
        return
    cx, cy = WINDOW_W // 2, WINDOW_H // 2
    if feedback_type == "correct":
        draw_checkmark(cx, cy)
    else:
        draw_crossmark(cx, cy)

# ====================================================================
# شمارش معکوس
# ====================================================================
def draw_countdown_circle():
    cx = WINDOW_W // 2
    cy = WINDOW_H // 2
    r  = 60

    pygame.draw.circle(screen, COUNTDOWN_BLUE, (cx, cy), r)

    txt = font_countdown.render(str(countdown_number), True, WHITE)
    screen.blit(txt, (cx - txt.get_width() // 2, cy - txt.get_height() // 2))

def update_countdown(dt_ms):
    global countdown_elapsed, countdown_number, countdown_last_played, countdown_active

    if not countdown_active:
        return False

    countdown_elapsed += dt_ms

    if countdown_last_played != countdown_number:
        if not sound_muted:
            play_sfx("countdown", 0.9)
        countdown_last_played = countdown_number

    if countdown_elapsed >= COUNTDOWN_MS:
        countdown_elapsed = 0
        countdown_number -= 1

        if countdown_number < 1:
            countdown_active = False
            countdown_number = 0
            return True

    return False

# ====================================================================
# صفحه پایان
# ====================================================================
def draw_end_screen():
    progress = min(1.0, bonus_elapsed_ms / bonus_total_ms)
    displayed_extra = int(final_bonus * progress)
    shown_score = score_without_bonus + displayed_extra

    draw_hud_top_only(score_override=shown_score)

    circle_cx = WINDOW_W // 2
    circle_cy = WINDOW_H // 2 - 80
    circle_r  = 60

    pygame.draw.circle(screen, (200, 200, 200), (circle_cx, circle_cy), circle_r)
    pygame.draw.circle(screen, (160, 160, 160), (circle_cx, circle_cy), circle_r, 3)

    mult_txt = font_big.render(f"x{multiplier}", True, (30, 30, 30))
    screen.blit(mult_txt, (circle_cx - mult_txt.get_width() // 2,
                           circle_cy - mult_txt.get_height() // 2))

    bonus_lbl = font_big.render("Score Bonus", True, WHITE)
    screen.blit(bonus_lbl, (WINDOW_W // 2 - bonus_lbl.get_width() // 2,
                            WINDOW_H // 2 + 10))

    bonus_num = font_bonus.render(str(final_bonus), True, WHITE)
    screen.blit(bonus_num, (WINDOW_W // 2 - bonus_num.get_width() // 2,
                            WINDOW_H // 2 + 70))

    if bonus_elapsed_ms >= bonus_total_ms:
        hint = font_small.render("Press R to restart  |  ESC to quit",
                                 True, (200, 200, 200))
        screen.blit(hint, (WINDOW_W // 2 - hint.get_width() // 2,
                           WINDOW_H - 40))

# ====================================================================
# صحنه
# ====================================================================
def draw_scene():
    if bg_surface:
        screen.blit(bg_surface, (0, 0))
    else:
        screen.fill(BG_FALLBACK)

    if countdown_active and not paused and not game_over:
        draw_pause_button_in_game(active=False)
        draw_hud_top_only(time_override=START_TIME,
                          score_override=0,
                          meter_override=0,
                          multiplier_override=1)
        draw_hud_bottom_countdown()
        draw_countdown_circle()
        return

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
                rect = rotated_img.get_rect(center=(lx + LEAF_W // 2, ly + LEAF_H // 2))
                screen.blit(rotated_img, rect)

    if not paused and not game_over:
        draw_hud()
        draw_feedback()

    if paused:
        draw_pause_menu()
        return

    if game_over:
        draw_end_screen()

# ====================================================================
# حرکت برگ‌ها
# ====================================================================
def move_leaves():
    global leaves
    if game_over or paused or countdown_active:
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
# امتیازدهی
# ====================================================================
def add_score():
    global score, multiplier, meter
    score += BASE_SCORE * multiplier
    meter += 1
    upgraded_to = None
    if meter >= METER_MAX:
        meter = 0
        if multiplier < MAX_MULTIPLIER:
            multiplier += 1
            upgraded_to = multiplier
    return upgraded_to

def penalize():
    global multiplier, meter
    if meter > 0:
        meter = 0
    else:
        multiplier = max(multiplier - 1, MIN_MULTIPLIER)

# ====================================================================
# پایان بازی
# ====================================================================
score_without_bonus = 0

def calculate_final_bonus():
    global final_bonus
    final_bonus = FINAL_BONUS_BASE * multiplier
    return final_bonus

def finish_game():
    global game_over, score, score_without_bonus
    global bonus_elapsed_ms, bonus_loop_started, bonus_end_played, bonus_total_ms

    if game_over:
        return
    game_over = True

    stop_loop("counterCountLoopable")

    calculate_final_bonus()
    score_without_bonus = score

    bonus_total_ms = compute_bonus_duration_ms(final_bonus)

    bonus_elapsed_ms = 0
    bonus_loop_started = False
    bonus_end_played = False

    stop_music()

    if not sound_muted:
        play_sfx("gameEnd", 0.85)

# ====================================================================
# انیمیشن بونوس
# ====================================================================
def update_bonus_animation(dt_ms):
    global bonus_elapsed_ms, bonus_loop_started, bonus_end_played

    if not game_over:
        return

    prev_ms = bonus_elapsed_ms
    bonus_elapsed_ms += dt_ms

    if not bonus_loop_started and not sound_muted:
        play_loop("counterCountLoopable", 0.8)
        bonus_loop_started = True

    if (not bonus_end_played
        and prev_ms < bonus_total_ms <= bonus_elapsed_ms):
        stop_loop("counterCountLoopable")
        if not sound_muted:
            play_sfx("counterEnd", 0.9)
        bonus_end_played = True

# ====================================================================
# بررسی پاسخ
# ====================================================================
def check(player_dir):
    global mode, pointing_dir, moving_dir, orange_visual_dir
    global feedback_type, feedback_timer

    if game_over or paused or countdown_active:
        return

    correct = (pointing_dir == player_dir) if mode == "pointing" else (moving_dir == player_dir)

    if correct:
        upgraded_to = add_score()
        feedback_type = "correct"
        feedback_timer = 400

        if not sound_muted:
            if upgraded_to == 2:
                play_sfx("answerCorrectX2", 1.0)
            elif upgraded_to == 3:
                play_sfx("answerCorrectX3", 1.0)
            elif upgraded_to is not None and upgraded_to >= 4:
                play_sfx("answerCorrectX4", 1.0)
            else:
                play_sfx("answerCorrect", 0.9)
    else:
        penalize()
        feedback_type = "wrong"
        feedback_timer = 400
        if not sound_muted:
            play_sfx("answerWrong", 1.0)

    mode = random.choice(["pointing", "moving"])
    pointing_dir = random.choice(DIRS)
    moving_dir = random.choice(DIRS)
    orange_visual_dir = random.choice(DIRS)
    spawn_leaves()

# ====================================================================
# ریست
# ====================================================================
def restart_game():
    global mode, pointing_dir, moving_dir, orange_visual_dir
    global score, time_left, multiplier, meter, final_bonus
    global game_over, paused
    global feedback_timer, feedback_type
    global bonus_elapsed_ms, bonus_loop_started, bonus_end_played, bonus_total_ms
    global score_without_bonus
    global countdown_active, countdown_number, countdown_elapsed, countdown_last_played
    global pending_gamestart_at, pending_music_at

    stop_loop("counterCountLoopable")

    mode = random.choice(["pointing", "moving"])
    pointing_dir = random.choice(DIRS)
    moving_dir = random.choice(DIRS)
    orange_visual_dir = random.choice(DIRS)

    score = 0
    time_left = START_TIME
    multiplier = MIN_MULTIPLIER
    meter = 0
    final_bonus = 0
    score_without_bonus = 0

    game_over = False
    paused = False
    feedback_timer = 0
    feedback_type = None

    bonus_elapsed_ms = 0
    bonus_total_ms = BONUS_MAX_MS
    bonus_loop_started = False
    bonus_end_played = False

    countdown_active = True
    countdown_number = COUNTDOWN_START
    countdown_elapsed = 0
    countdown_last_played = None

    pending_gamestart_at = None
    pending_music_at = None

    spawn_leaves()

# ====================================================================
# شروع
# ====================================================================
spawn_leaves()

running = True
last_frame_ms = pygame.time.get_ticks()

# ====================================================================
# حلقه اصلی
# ====================================================================
while running:
    now_ms = pygame.time.get_ticks()
    dt_ms = now_ms - last_frame_ms
    last_frame_ms = now_ms

    if feedback_timer > 0:
        feedback_timer -= dt_ms

    update_bonus_animation(dt_ms)

    if countdown_active:
        just_finished = update_countdown(dt_ms)
        if just_finished:
            start_game_audio()

    if (pending_gamestart_at is not None
        and not paused
        and not countdown_active
        and not game_over
        and pygame.time.get_ticks() >= pending_gamestart_at):
        if not sound_muted:
            play_sfx("gameStart", 0.85)
        pending_gamestart_at = None

    if (pending_music_at is not None
        and not paused
        and not game_over
        and pygame.time.get_ticks() >= pending_music_at):
        start_music()
        pending_music_at = None

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == TIMER_EVENT:
            if not game_over and not paused and not countdown_active:
                if time_left > 0:
                    time_left -= 1
                    if 1 <= time_left <= 5:
                        if not sound_muted:
                            play_sfx("timer", 0.75)
                else:
                    finish_game()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if countdown_active:
                continue

            if not paused and not game_over:
                if PAUSE_RECT.collidepoint(event.pos):
                    paused = True
                    show_howto = False
                    cancel_startup_audio()
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
                if not game_over and not countdown_active:
                    paused = not paused
                    show_howto = False
                    if paused:
                        cancel_startup_audio()
                continue

            if event.key == pygame.K_ESCAPE:
                if game_over:
                    running = False
                elif show_howto:
                    show_howto = False
                elif paused:
                    paused = False
                elif not countdown_active:
                    paused = True
                    cancel_startup_audio()
                continue

            if event.key == pygame.K_r and game_over:
                restart_game()
                continue

            if paused or countdown_active:
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