"""
ReVerse - Game Constants
Değişmeyen sabitler ve yardımcı fonksiyonlar
"""

# ============================================
# TILE TYPES (Karo Tipleri)
# ============================================
TILE_EMPTY = "."
TILE_DAMAGE = "X"
TILE_START = "S"
TILE_DOOR = "D"
TILE_KEY = "K"
TILE_STAR = "*"
TILE_ROTATE = "R"
TILE_PUSH_RIGHT = ">"
TILE_PUSH_LEFT = "<"
TILE_PUSH_UP = "^"
TILE_PUSH_DOWN = "v"

# ============================================
# DIRECTIONS (Yönler)
# ============================================
DIR_RIGHT = "right"
DIR_LEFT = "left"
DIR_UP = "up"
DIR_DOWN = "down"

# ============================================
# INPUT KEYS (Klavye Tuşları)
# ============================================
KEY_LEFT = "a"
KEY_RIGHT = "d"
KEY_JUMP = "space"
KEY_RESTART = "r"
KEY_PAUSE = "escape"
KEY_QUIT = "q"

# ============================================
# LEGEND (Sembol Açıklamaları)
# ============================================
LEGEND = {
    TILE_EMPTY: "Empty (Safe Ground)",
    TILE_DAMAGE: "Black Block (Damage Platform)",
    TILE_START: "Start Position",
    TILE_DOOR: "Door (Exit)",
    TILE_KEY: "Key",
    TILE_STAR: "Star (Collectible)",
    TILE_ROTATE: "Rotate Symbol",
    TILE_PUSH_RIGHT: "Push Right (Triangle)",
    TILE_PUSH_LEFT: "Push Left (Triangle)",
    TILE_PUSH_UP: "Push Up (Triangle)",
    TILE_PUSH_DOWN: "Push Down (Triangle)"
}

# ============================================
# HELPER FUNCTIONS (Yardımcı Fonksiyonlar)
# ============================================

def get_grid_position(pixel_x, pixel_y, grid_size):
    """Piksel koordinatını grid koordinatına çevir"""
    return pixel_x // grid_size, pixel_y // grid_size

def get_pixel_position(grid_x, grid_y, grid_size):
    """Grid koordinatını piksel koordinatına çevir"""
    return grid_x * grid_size, grid_y * grid_size

def is_valid_grid_position(grid_x, grid_y, max_cols, max_rows):
    """Grid pozisyonu geçerli mi kontrol et"""
    return 0 <= grid_x < max_cols and 0 <= grid_y < max_rows

def clamp(value, min_value, max_value):
    """Değeri min-max arasında sınırla"""
    return max(min_value, min(value, max_value))
