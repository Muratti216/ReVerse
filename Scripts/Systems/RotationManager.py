"""
ReVerse - Rotation Manager
Dünya döndürme sistemi (90° rotasyon)
"""
import pygame
from Scripts.Utils.Constants import *

class RotationManager:
    """
    Haritayı 90° döndürme yöneticisi
    Unity Transform.Rotate benzeri
    """
    
    def __init__(self):
        self.rotation_count = 0  # Kaç kez döndürüldü (0-3)
    
    def rotate_world_90(self, level_loader):
        """
        Dünyayı 90° saat yönünde döndür
        
        Args:
            level_loader: LevelLoader objesi (tiles, collectibles, player içerir)
        """
        self.rotation_count = (self.rotation_count + 1) % 4
        
        print(f"🔄 Rotating world... (rotation count: {self.rotation_count})")
        
        # 1. Grid boyutlarını al
        from config import GRID_COLS, GRID_ROWS, GRID_SIZE
        
        # 2. Tüm PushTriangle'ların yönlerini döndür
        for tile in level_loader.tiles:
            if tile.__class__.__name__ == 'PushTriangle':
                self._rotate_triangle_direction(tile, GRID_COLS, GRID_ROWS, GRID_SIZE)
        
        print(f"✅ Reversed {len([t for t in level_loader.tiles if t.__class__.__name__ == 'PushTriangle'])} push triangles")
    
    def _rotate_triangle_direction(self, triangle, grid_cols, grid_rows, grid_size):
        """
        Üçgenin yönünü 90° döndür (saat yönünde)
        
        Args:
            triangle: PushTriangle objesi
            grid_cols: Grid sütun sayısı
            grid_rows: Grid satır sayısı
            grid_size: Grid hücre boyutu
        """
        # Yön haritası: right -> down -> left -> up -> right
        direction_map = {
            DIR_RIGHT: DIR_DOWN,
            DIR_DOWN: DIR_LEFT,
            DIR_LEFT: DIR_UP,
            DIR_UP: DIR_RIGHT
        }
        
        # Yeni yönü ayarla
        old_direction = triangle.direction
        triangle.direction = direction_map.get(old_direction, DIR_RIGHT)
        
        # Sprite'ı yeni yöne göre döndür
        try:
            base_sprite = pygame.image.load("Assets/Sprites/Ok.png")
            base_sprite = pygame.transform.smoothscale(base_sprite, (grid_size, grid_size))
            
            if triangle.direction == DIR_RIGHT:
                triangle.sprite = base_sprite
            elif triangle.direction == DIR_LEFT:
                triangle.sprite = pygame.transform.rotate(base_sprite, 180)
            elif triangle.direction == DIR_UP:
                triangle.sprite = pygame.transform.rotate(base_sprite, 90)
            elif triangle.direction == DIR_DOWN:
                triangle.sprite = pygame.transform.rotate(base_sprite, -90)
        except:
            pass
    
    def reset(self):
        """Rotasyonu sıfırla"""
        self.rotation_count = 0


# ============================================
# TEST CODE
# ============================================
if __name__ == "__main__":
    print("RotationManager test...")
    rm = RotationManager()
    print(f"Initial rotation: {rm.rotation_count}")
    
    # Test direction rotation
    test_directions = [DIR_RIGHT, DIR_DOWN, DIR_LEFT, DIR_UP]
    direction_map = {
        DIR_RIGHT: DIR_DOWN,
        DIR_DOWN: DIR_LEFT,
        DIR_LEFT: DIR_UP,
        DIR_UP: DIR_RIGHT
    }
    
    for direction in test_directions:
        new_dir = direction_map[direction]
        print(f"{direction} -> {new_dir}")
    
    print("✅ RotationManager OK!")
