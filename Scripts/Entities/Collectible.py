"""
ReVerse - Collectible Entities
Toplanabilir objeler (Unity Pickup benzeri)
"""
import pygame
import math
from config import *
from Scripts.Utils.Constants import *

# ============================================
# BASE COLLECTIBLE CLASS
# ============================================

class Collectible:
    """
    Base toplanabilir sınıf
    Tüm collectible objeler bundan türer
    """
    
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        # Collision box biraz küçük ama görsel tam kare
        padding = size // 8
        self.rect = pygame.Rect(x + padding, y + padding, size - 2*padding, size - 2*padding)
        self.color = (255, 255, 255)
        self.collected = False
        self.bounce_offset = 0  # Zıplama animasyonu için
        self.bounce_speed = 2
        
    def draw(self, screen, camera_offset=(0, 0)):
        """
        Collectible'ı çiz
        
        Args:
            screen: Pygame surface
            camera_offset: Kamera kayması (x, y)
        """
        if self.collected:
            return
        
        draw_x = self.rect.x - camera_offset[0]
        draw_y = self.rect.y - camera_offset[1] + self.bounce_offset
        
        # Daire olarak çiz (basit)
        center = (draw_x + self.rect.width // 2, draw_y + self.rect.height // 2)
        radius = self.rect.width // 2
        
        pygame.draw.circle(screen, self.color, center, radius)
        pygame.draw.circle(screen, (0, 0, 0), center, radius, 1)
    
    def update(self, dt):
        """
        Zıplama animasyonu
        
        Args:
            dt: Delta time
        """
        if not self.collected:
            self.bounce_offset = math.sin(pygame.time.get_ticks() * 0.003) * 5
    
    def collect(self, player):
        """
        Toplanma eylemi
        
        Args:
            player: Player objesi
        """
        self.collected = True
    
    def is_collected(self):
        """Toplanmış mı kontrol et"""
        return self.collected


# ============================================
# COLLECTIBLE TYPES
# ============================================

class Star(Collectible):
    """Yıldız (*) - Puan toplama"""
    
    def __init__(self, x, y, size):
        super().__init__(x, y, size)
        self.color = STAR_COLOR
        
        # Sprite yükle
        try:
            self.sprite = pygame.image.load("Assets/Sprites/Yildiz.png")
            self.sprite = pygame.transform.scale(self.sprite, (size, size))
        except:
            self.sprite = None
            print("⚠️ Yildiz.png yüklenemedi")
        
    def draw(self, screen, camera_offset=(0, 0)):
        if self.collected:
            return
        
        # Rect padding'i telafi et
        padding = self.size // 8
        draw_x = self.rect.x - camera_offset[0] - padding
        draw_y = self.rect.y - camera_offset[1] - padding
        
        # Sprite varsa sprite çiz, yoksa eski şekil
        if self.sprite:
            screen.blit(self.sprite, (draw_x, draw_y))
        else:
            # Fallback: Yıldız şekli
            center = (draw_x + self.rect.width // 2, draw_y + self.rect.height // 2)
            radius = self.rect.width // 2
            points = self._get_star_points(center, radius)
            pygame.draw.polygon(screen, self.color, points)
            pygame.draw.polygon(screen, (0, 0, 0), points, 2)
    
    def _get_star_points(self, center, radius):
        """5 köşeli yıldız noktaları"""
        cx, cy = center
        points = []
        
        for i in range(10):
            angle = math.pi / 2 + (2 * math.pi * i / 10)
            r = radius if i % 2 == 0 else radius / 2
            x = cx + r * math.cos(angle)
            y = cy - r * math.sin(angle)
            points.append((x, y))
        
        return points
    
    def collect(self, player):
        super().collect(player)
        player.stars_collected += 1
        print(f"⭐ Star collected! Total: {player.stars_collected}")


class Key(Collectible):
    """Anahtar (K) - Kapıyı açmak için gerekli"""
    
    def __init__(self, x, y, size):
        super().__init__(x, y, size)
        self.color = KEY_COLOR
        
        # Sprite yükle
        try:
            self.sprite = pygame.image.load("Assets/Sprites/Key.png")
            self.sprite = pygame.transform.scale(self.sprite, (size, size))
        except:
            self.sprite = None
            print("⚠️ Key.png yüklenemedi")
        
    def draw(self, screen, camera_offset=(0, 0)):
        if self.collected:
            return
        
        # Rect padding'i telafi et
        padding = self.size // 8
        draw_x = self.rect.x - camera_offset[0] - padding
        draw_y = self.rect.y - camera_offset[1] - padding
        
        # Sprite varsa sprite çiz
        if self.sprite:
            screen.blit(self.sprite, (draw_x, draw_y))
        else:
            # Fallback: Basit anahtar şekli
            center = (draw_x + self.rect.width // 2, draw_y + self.rect.height // 2)
            pygame.draw.circle(screen, self.color, center, self.rect.width // 3)
            body_rect = pygame.Rect(center[0] - 3, center[1], 6, self.rect.height // 2)
            pygame.draw.rect(screen, self.color, body_rect)
            pygame.draw.circle(screen, (0, 0, 0), center, self.rect.width // 3, 2)
            pygame.draw.rect(screen, (0, 0, 0), body_rect, 2)
    
    def collect(self, player):
        super().collect(player)
        player.has_key = True
        print("🔑 Key obtained!")


class Door(Collectible):
    """Kapı (D) - Çıkış noktası"""
    
    def __init__(self, x, y, size):
        # NOT: super().__init__ çağırmayalım, çünkü padding istemiyoruz
        self.x = x
        self.y = y
        self.size = size
        self.rect = pygame.Rect(x, y, size, size)  # Tam kare collision
        self.color = DOOR_COLOR
        self.collected = False
        self.bounce_offset = 0
        self.bounce_speed = 2
        self.is_open = False
        self.last_try_time = 0  # Mesaj spam önleme
        self.message_cooldown = 0.5  # saniye
        
        # Sprite yükle (kapalı ve açık kapı)
        try:
            # Orijinal görseli yükle ve aspect ratio'yu koru
            closed_img = pygame.image.load("Assets/Sprites/Kapi.png")
            open_img = pygame.image.load("Assets/Sprites/AcikKapi.png")
            
            # Smooth scale ile kaliteyi koru
            self.sprite_closed = pygame.transform.smoothscale(closed_img, (size, size))
            self.sprite_open = pygame.transform.smoothscale(open_img, (size, size))
        except:
            self.sprite_closed = None
            self.sprite_open = None
            print("⚠️ Kapi.png veya AcikKapi.png yüklenemedi")
        
    def draw(self, screen, camera_offset=(0, 0), player=None):
        # Door padding kullanmıyor, tam kare
        draw_x = self.rect.x - camera_offset[0]
        draw_y = self.rect.y - camera_offset[1]
        
        # Sprite varsa sprite çiz
        if self.sprite_closed and self.sprite_open:
            # Oyuncu bilgisi varsa ona göre, yoksa is_open'a göre
            if player:
                # Sadece anahtar alındıysa açık kapı görseli
                can_open = player.has_key
                sprite = self.sprite_open if can_open else self.sprite_closed
            else:
                sprite = self.sprite_open if self.is_open else self.sprite_closed
            screen.blit(sprite, (draw_x, draw_y))
        else:
            # Fallback: Renkli kapı
            if player:
                # Sadece anahtar alındıysa açık kapı rengi
                can_open = player.has_key
                color = (50, 255, 50) if can_open else self.color
            else:
                color = self.color if not self.is_open else (50, 255, 50)
            pygame.draw.rect(screen, color, (draw_x, draw_y, self.size, self.size))
            pygame.draw.rect(screen, (255, 255, 255), (draw_x, draw_y, self.size, self.size), 1)
            inner_rect = pygame.Rect(draw_x + 10, draw_y + 10, self.size - 20, self.size - 20)
            pygame.draw.rect(screen, (0, 0, 0), inner_rect, 1)
    
    def can_enter(self, player):
        """
        Oyuncu kapıya girebilir mi kontrol et
        
        Args:
            player: Player objesi
            
        Returns:
            bool: Girebilir mi?
        """
        # Anahtarı var mı ve yeterli yıldızı topladı mı?
        return player.has_key and player.stars_collected >= player.required_stars
    
    def try_enter(self, player, current_time):
        """
        Kapıya girmeyi dene
        
        Args:
            player: Player objesi
            current_time: Şu anki zaman (saniye)
            
        Returns:
            bool: Başarılı mı?
        """
        if self.can_enter(player):
            self.is_open = True
            print("🚪 Door opened! Level complete!")
            return True
        else:
            # Mesaj spam önleme
            if current_time - self.last_try_time > self.message_cooldown:
                missing = []
                if not player.has_key:
                    missing.append("Key")
                if player.stars_collected < player.required_stars:
                    missing.append(f"Stars ({player.stars_collected}/{player.required_stars})")
                
                print(f"🚫 Door locked! Missing: {', '.join(missing)}")
                self.last_try_time = current_time
            return False


class RotateSymbol:
    """
    Döndürme sembolü (R)
    Haritayı 90 derece döndürür
    """
    
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.rect = pygame.Rect(x, y, size, size)
        self.color = ROTATE_COLOR
        self.rotation_angle = 0  # Animasyon için
        self.activated = False
        self.flip_lr = False     # İstenirse yön değişimi için (opsiyonel)
        self.consumed = False    # Tek seferlik kullanım için

        # Tek görsel (BombeliOk.png) yükle
        try:
            base_sprite = pygame.image.load("Assets/Sprites/BombeliOk.png").convert_alpha()
            # Tek, ortalanmış görsel (kare içinde %60 boyut)
            target_w = int(self.size * 0.6)
            target_h = int(self.size * 0.6)
            self.symbol_sprite = pygame.transform.smoothscale(base_sprite, (target_w, target_h))
        except:
            self.symbol_sprite = None
            print("⚠️ BombeliOk.png yüklenemedi, vektörel ok çizimi kullanılacak")
        
    def draw(self, screen, camera_offset=(0, 0)):
        draw_x = self.rect.x - camera_offset[0]
        draw_y = self.rect.y - camera_offset[1]
        
        # Tüketilmişse çizme
        if self.consumed:
            return

        # Tek görseli ortala ve çiz (arka plan doldurma yok, sadece ince kenarlık)
        if self.symbol_sprite:
            # Opsiyonel yön değişimi: flip_lr ise 180° döndür
            sprite = pygame.transform.rotate(self.symbol_sprite, 180) if self.flip_lr else self.symbol_sprite
            sx = draw_x + (self.size - sprite.get_width()) // 2
            sy = draw_y + (self.size - sprite.get_height()) // 2
            screen.blit(sprite, (sx, sy))
        else:
            # Fallback: tek vektörel ok
            arrow_color = (0, 0, 0)
            cx = draw_x + self.size // 2
            cy = draw_y + self.size // 2
            w = self.size // 2
            h = self.size // 5
            half_w = w // 2
            half_h = h // 2
            if not self.flip_lr:
                points = [
                    (cx - half_w, cy - half_h), (cx + half_w - half_h, cy - half_h),
                    (cx + half_w, cy), (cx + half_w - half_h, cy + half_h), (cx - half_w, cy + half_h)
                ]
            else:
                points = [
                    (cx + half_w, cy - half_h), (cx - half_w + half_h, cy - half_h),
                    (cx - half_w, cy), (cx - half_w + half_h, cy + half_h), (cx + half_w, cy + half_h)
                ]
            pygame.draw.polygon(screen, arrow_color, points)
        # Kenarlık
        pygame.draw.rect(screen, (0, 0, 0), (draw_x, draw_y, self.size, self.size), 1)
    
    def update(self, dt):
        """Animasyon güncellemesi"""
        if self.activated:
            self.rotation_angle += 5  # Dönme animasyonu
            if self.rotation_angle >= 90:
                self.rotation_angle = 0
                self.activated = False
    
    def activate(self, game_manager):
        """
        Döndürme sembolü tetiklendi
        
        Args:
            game_manager: GameManager objesi
        """
        if not self.activated and not self.consumed:
            self.activated = True
            # Ok yönlerini tersle (üst sağ <-> sol, alt sol <-> sağ)
            self.flip_lr = not self.flip_lr
            print("🔄 Rotation symbol activated!")
            # GameManager'a döndürme sinyali gönder (GameManager tetikler)


# ============================================
# COLLECTIBLE FACTORY
# ============================================

class CollectibleFactory:
    """
    Collectible objesi oluşturma fabrikası
    """
    
    @staticmethod
    def create_collectible(tile_type, x, y, size):
        """
        Tile tipine göre collectible oluştur
        
        Args:
            tile_type (str): Tile tipi
            x (int): X pozisyonu
            y (int): Y pozisyonu
            size (int): Boyut
            
        Returns:
            Collectible: Oluşturulan obje veya None
        """
        if tile_type == TILE_STAR:
            return Star(x, y, size)
        
        elif tile_type == TILE_KEY:
            return Key(x, y, size)
        
        elif tile_type == TILE_DOOR:
            return Door(x, y, size)
        
        elif tile_type == TILE_ROTATE:
            return RotateSymbol(x, y, size)
        
        return None
