"""
ReVerse - Tile Entities
Grid objeleri (Unity GameObject/Prefab benzeri)
"""
import pygame
import config
from config import *
from Scripts.Utils.Constants import *

# ============================================
# BASE TILE CLASS
# ============================================

class Tile:
    """
    Base Tile sınıfı (Unity GameObject benzeri)
    Tüm tile tipleri bundan türer
    """
    
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.rect = pygame.Rect(x, y, size, size)
        self.color = (100, 100, 100)
        self.is_solid = True  # Çarpışma var mı?
        
    def draw(self, screen, camera_offset=(0, 0)):
        """
        Tile'ı çiz (Unity OnGUI benzeri)
        
        Args:
            screen: Pygame surface
            camera_offset: Kamera kayması (x, y)
        """
        draw_x = self.rect.x - camera_offset[0]
        draw_y = self.rect.y - camera_offset[1]
        
        # Tile'ı çiz
        pygame.draw.rect(screen, self.color, (draw_x, draw_y, self.size, self.size))
        
        # Kenar lık (ince)
        pygame.draw.rect(screen, (0, 0, 0), (draw_x, draw_y, self.size, self.size), 1)
    
    def on_player_land(self, player):
        """
        Oyuncu bu tile'a bastığında çağrılır
        (Unity OnTriggerEnter benzeri)
        
        Args:
            player: Player objesi
        """
        pass
    
    def update(self, dt):
        """Frame güncellemesi (Unity Update benzeri)"""
        pass


# ============================================
# TILE TYPES
# ============================================

class SafeTile(Tile):
    """Güvenli zemin - Can götürmez"""
    
    def __init__(self, x, y, size):
        super().__init__(x, y, size)
        self.color = SAFE_TILE_COLOR


class DamageTile(Tile):
    """
    Siyah çizgili platform
    3x3 kuralını tetikler
    """
    
    def __init__(self, x, y, size):
        super().__init__(x, y, size)
        self.color = DAMAGE_TILE_COLOR
        self.stripe_spacing = 10  # Çizgi aralığı
        
        # Sprite yükle
        try:
            self.sprite = pygame.image.load("Assets/Sprites/Engel.png")
            self.sprite = pygame.transform.scale(self.sprite, (size, size))
        except:
            self.sprite = None
            print("⚠️ Engel.png yüklenemedi")
        
    def draw(self, screen, camera_offset=(0, 0)):
        draw_x = self.rect.x - camera_offset[0]
        draw_y = self.rect.y - camera_offset[1]
        
        # Sprite varsa sprite çiz
        if self.sprite:
            screen.blit(self.sprite, (draw_x, draw_y))
        else:
            # Fallback: Siyah çizgili platform
            super().draw(screen, camera_offset)
            for i in range(0, self.size, self.stripe_spacing):
                pygame.draw.line(screen, DAMAGE_STRIPE_COLOR, 
                               (draw_x + i, draw_y), 
                               (draw_x + i, draw_y + self.size), 1)
    
    def on_player_land(self, player):
        """Can götür!"""
        if config.GOD_MODE:
            print("🛡️ GOD MODE: Damage ignored")
            return
        can_continue = player.resource_manager.use_jump()
        if not can_continue:
            print("💀 Player died on damage tile!")


class PushTriangle(Tile):
    """
    İtici üçgen platform
    Oyuncuyu belirli yöne iter
    """
    
    def __init__(self, x, y, size, direction):
        super().__init__(x, y, size)
        self.direction = direction  # "right", "left", "up", "down"
        self.color = TRIANGLE_COLOR
        self.push_force = PUSH_FORCE_MULTIPLIER
        self.is_solid = True
        
        # Sprite yükle ve yöne göre döndür (BombeliOk.png artık Ok.png için ayrıldı)
        try:
            base_sprite = pygame.image.load("Assets/Sprites/Ok.png").convert_alpha()
            base_sprite = pygame.transform.smoothscale(base_sprite, (size, size))
            
            # Yöne göre döndür
            if direction == DIR_RIGHT:
                self.sprite = base_sprite  # Varsayılan sağa baksın
            elif direction == DIR_LEFT:
                self.sprite = pygame.transform.rotate(base_sprite, 180)
            elif direction == DIR_UP:
                self.sprite = pygame.transform.rotate(base_sprite, 90)
            elif direction == DIR_DOWN:
                self.sprite = pygame.transform.rotate(base_sprite, -90)
        except:
            self.sprite = None
            print("⚠️ Ok.png yüklenemedi")
        
    def draw(self, screen, camera_offset=(0, 0)):
        draw_x = self.rect.x - camera_offset[0]
        draw_y = self.rect.y - camera_offset[1]
        
        # Sprite varsa sprite çiz
        if self.sprite:
            screen.blit(self.sprite, (draw_x, draw_y))
        else:
            # Fallback: Üçgen çiz
            pygame.draw.rect(screen, (30, 30, 30), (draw_x, draw_y, self.size, self.size))
            center = (draw_x + self.size // 2, draw_y + self.size // 2)
            points = self._get_triangle_points(center)
            pygame.draw.polygon(screen, self.color, points)
            pygame.draw.polygon(screen, (0, 0, 0), points, 1)
            pygame.draw.rect(screen, (0, 0, 0), (draw_x, draw_y, self.size, self.size), 1)
    
    def _get_triangle_points(self, center):
        """
        Yöne göre üçgen noktalarını hesapla
        
        Args:
            center: (x, y) merkez nokta
            
        Returns:
            list: [(x1,y1), (x2,y2), (x3,y3)]
        """
        cx, cy = center
        half = self.size // 2 - 10  # Kenarlardan biraz içerde
        
        if self.direction == DIR_RIGHT:
            return [
                (cx - half, cy - half),
                (cx - half, cy + half),
                (cx + half, cy)
            ]
        elif self.direction == DIR_LEFT:
            return [
                (cx + half, cy - half),
                (cx + half, cy + half),
                (cx - half, cy)
            ]
        elif self.direction == DIR_UP:
            return [
                (cx - half, cy + half),
                (cx + half, cy + half),
                (cx, cy - half)
            ]
        else:  # DIR_DOWN
            return [
                (cx - half, cy - half),
                (cx + half, cy - half),
                (cx, cy + half)
            ]
    
    def on_player_land(self, player):
        """Oyuncuyu ok ucunun baktığı yönün 1 önüne anında yerleştir."""
        if self.direction is None:
            return
        dir_map = {
            DIR_RIGHT: (1, 0),
            DIR_LEFT: (-1, 0),
            DIR_UP: (0, -1),
            DIR_DOWN: (0, 1)
        }
        dx, dy = dir_map.get(self.direction, (0, 0))
        # Bu üçgenin grid koordinatı
        gx = self.x // GRID_SIZE
        gy = self.y // GRID_SIZE
        target_gx = gx + dx
        target_gy = gy + dy
        # Sınırlar içinde tut
        target_gx = max(0, min(target_gx, GRID_COLS - 1))
        target_gy = max(0, min(target_gy, GRID_ROWS - 1))
        # Oyuncuyu anında taşı
        player.grid_x = target_gx
        player.grid_y = target_gy
        player.x = target_gx * GRID_SIZE
        player.y = target_gy * GRID_SIZE
        player.rect.x = player.x
        player.rect.y = player.y
        print(f"🏹 Snapped player in front of {self.direction} arrow to ({target_gx},{target_gy})")
    
    def reverse_direction(self):
        """
        Yönü tersine çevir (Rotation için)
        """
        if self.direction is None:
            return
            
        reverse_map = {
            DIR_RIGHT: DIR_LEFT,
            DIR_LEFT: DIR_RIGHT,
            DIR_UP: DIR_DOWN,
            DIR_DOWN: DIR_UP
        }
        self.direction = reverse_map.get(self.direction, self.direction)


# ============================================
# TILE FACTORY
# ============================================

class TileFactory:
    """
    Tile objesi oluşturma fabrikası
    Unity Instantiate benzeri
    """
    
    @staticmethod
    def create_tile(tile_type, x, y, size):
        """
        Tile tipine göre obje oluştur
        
        Args:
            tile_type (str): Tile tipi (TILE_EMPTY, TILE_DAMAGE, vs.)
            x (int): X pozisyonu
            y (int): Y pozisyonu
            size (int): Tile boyutu
            
        Returns:
            Tile: Oluşturulan tile objesi veya None
        """
        if tile_type == TILE_EMPTY:
            return SafeTile(x, y, size)
        
        elif tile_type == TILE_DAMAGE:
            return DamageTile(x, y, size)
        
        elif tile_type == TILE_PUSH_RIGHT:
            return PushTriangle(x, y, size, DIR_RIGHT)
        
        elif tile_type == TILE_PUSH_LEFT:
            return PushTriangle(x, y, size, DIR_LEFT)
        
        elif tile_type == TILE_PUSH_UP:
            return PushTriangle(x, y, size, DIR_UP)
        
        elif tile_type == TILE_PUSH_DOWN:
            return PushTriangle(x, y, size, DIR_DOWN)
        
        # Başlangıç, kapı, anahtar, yıldız, döndürme sembolü için
        # ayrı objeler Entities.Collectible içinde oluşturuluyor.
        # Bu hücrelere zemin yerleştirmiyoruz (çarpışmayı önlemek için)
        elif tile_type in [TILE_START, TILE_DOOR, TILE_KEY, TILE_STAR, TILE_ROTATE]:
            return None
        
        return None
