"""
ReVerse - Game Configuration
Unity benzeri global ayarlar
"""

# ============================================
# GRID SETTINGS (Grid Ayarları)
# Önce grid boyutları, sonra ekran boyutu hesaplanır
# ============================================
GRID_SIZE = 64  # Her kare 64x64 piksel
GRID_COLS = 6   # Harita genişliği (6 sütun)
GRID_ROWS = 5   # Harita yüksekliği (5 satır)

# ============================================
# SCREEN SETTINGS (Ekran Ayarları)
# Ekran boyutunu scale ile büyüt (UI için yer aç)
# ============================================
SCALE = 2.5  # Pencere büyütme çarpanı
SCREEN_WIDTH = int(GRID_SIZE * GRID_COLS * SCALE)
SCREEN_HEIGHT = int(GRID_SIZE * GRID_ROWS * SCALE)
FPS = 60
FULLSCREEN = False  # F11 ile açılabilir
VSYNC = True
HUD_HEIGHT = int(64 * SCALE)  # Üst HUD yüksekliği (Zelda-1 tarzı sabit üst şerit)

# ============================================
# GAME RULES (Oyun Kuralları)
# ============================================
MAX_MAIN_LIVES = 3        # Ana can sayısı
JUMPS_PER_LIFE = 3        # Her ana can için zıplama hakkı
STARS_TO_WIN = 2          # Kazanmak için gereken yıldız

# ============================================
# COLORS (Renkler)
# ============================================
# Background
BG_COLOR = (250, 250, 250)          # Beyaza yakın açık gri (kareli kağıt arka plan)
GRID_LINE_COLOR = (0, 0, 0)         # Siyah grid çizgileri (kareli kağıt çizgileri)
GRID_LINE_WIDTH = 1                 # İnce grid çizgileri

# Player
PLAYER_COLOR = (50, 200, 50)        # Yeşil

# Tiles
SAFE_TILE_COLOR = (250, 250, 250)   # Arka plan ile aynı (görünmez)
DAMAGE_TILE_COLOR = (50, 50, 50)    # Koyu gri
DAMAGE_STRIPE_COLOR = (0, 0, 0)     # Siyah çizgiler

# Collectibles
STAR_COLOR = (255, 255, 0)          # Sarı
KEY_COLOR = (255, 215, 0)           # Altın
DOOR_COLOR = (100, 50, 200)         # Mor
ROTATE_COLOR = (255, 50, 50)        # Kırmızı

# Triangles (İticiler)
TRIANGLE_COLOR = (255, 100, 100)    # Açık kırmızı

# UI
UI_TEXT_COLOR = (100, 100, 100)     # Gri
UI_LIFE_FULL = (50, 200, 50)        # Yeşil
UI_LIFE_EMPTY = (100, 100, 100)     # Gri

# ============================================
# PHYSICS (Fizik) - Şimdilik kullanılmıyor (turn-based sistem)
# ============================================
# GRAVITY = 0.5              # Yerçekimi (ileride platform mode için)
# JUMP_FORCE = -12           # Zıplama gücü
# MAX_FALL_SPEED = 15        # Maksimum düşme hızı
# MOVE_SPEED = 5             # Yatay hareket hızı

# Triangle Push Force
PUSH_FORCE_MULTIPLIER = 2  # Üçgen itme çarpanı (grid başına)
# Jump Animation
JUMP_ARC_HEIGHT = -20  # Zıplama animasyonu yüksekliği (piksel, negatif yukarı yönde)
# ============================================
# GAME STATES
# ============================================
STATE_SPLASH = "splash"
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_WIN = "win"
STATE_GAME_OVER = "game_over"

# ============================================
# DEBUG OPTIONS
# ============================================
SHOW_FPS = True           # FPS göster
SHOW_GRID = True          # Grid çizgilerini göster
SHOW_COLLIDERS = False    # Çarpışma kutularını göster
GOD_MODE = False          # Can sonsuz (test için)

# ============================================
# PATHS (Dosya Yolları)
# ============================================
ASSETS_PATH = "Assets/"
SPRITES_PATH = ASSETS_PATH + "Sprites/"
VIDEOS_PATH = ASSETS_PATH + "Videos/"
FONTS_PATH = ASSETS_PATH + "Fonts/"
SPLASH_VIDEO = VIDEOS_PATH + "splash.mp4"
