"""
ReVerse - Player
Yeşil amorf taş karakter - Grid tabanlı turn-based hareket
"""
import pygame
from Scripts.Utils.Path import asset_path
from config import *
from Scripts.Systems.ResourceManager import ResourceManager
from Scripts.Utils.Constants import *

class Player:
    """
    Oyuncu karakteri
    Turn-based grid hareket: SPACE -> zıpla seçimi -> yön tuşu -> hareket
    """
    
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.rect = pygame.Rect(x, y, size, size)
        self.color = PLAYER_COLOR
        
        # Sprite yükle
        try:
            self._default_sprite_path = "Assets/Sprites/Avatar.png"
            self.sprite = pygame.image.load(asset_path(self._default_sprite_path))
            self.sprite = pygame.transform.scale(self.sprite, (size, size))
        except (FileNotFoundError, pygame.error) as e:
            self.sprite = None
            print(f"⚠️ Avatar.png yüklenemedi: {e}")
        
        # Kalp sprite yükle (UI için)
        try:
            heart_size = int(32 * SCALE)  # Kalp boyutu
            self.heart_sprite = pygame.image.load(asset_path("Assets/Sprites/Kalp.png"))
            self.heart_sprite = pygame.transform.smoothscale(self.heart_sprite, (heart_size, heart_size))
        except (FileNotFoundError, pygame.error) as e:
            self.heart_sprite = None
            print(f"⚠️ Kalp.png yüklenemedi: {e}")
        
        # Grid pozisyon
        self.grid_x = x // size
        self.grid_y = y // size
        
        # Turn-based hareket durumu
        self.turn_state = "waiting"  # "waiting", "jump_selected", "moving"
        self.will_jump = False
        self.target_grid_x = self.grid_x
        self.target_grid_y = self.grid_y
        self.move_progress = 0.0  # 0.0 - 1.0 arası animasyon
        self.move_speed = 8.0  # Hız çarpanı (daha yüksek = daha hızlı)
        self.just_pushed = False  # Ok tarafından itildi mi (çift hasar önleme)
        
        # Oyun durumu
        self.resource_manager = None  # GameManager tarafından set edilecek
        self.stars_collected = 0
        self.required_stars = STARS_TO_WIN
        self.has_key = False
        self.require_key = True
        self.is_alive = True
        
        # Input throttle (tuş basılı tutmayı engelle)
        self.last_input_time = 0
        self.input_cooldown = 0.15  # saniye

    def set_sprite(self, relative_path: str):
        """Oyuncu sprite'ını değiştir (Assets/Sprites altındaki dosya)."""
        try:
            img = pygame.image.load(asset_path(relative_path))
            self.sprite = pygame.transform.scale(img, (self.size, self.size))
        except (FileNotFoundError, pygame.error) as e:
            print(f"⚠️ Sprite yüklenemedi ({relative_path}): {e}")

    def restore_default_sprite(self):
        """Varsayılan Avatar sprite'ına geri dön."""
        try:
            img = pygame.image.load(asset_path(self._default_sprite_path))
            self.sprite = pygame.transform.scale(img, (self.size, self.size))
        except (FileNotFoundError, pygame.error) as e:
            print(f"⚠️ Varsayılan Avatar yüklenemedi: {e}")
        
    def update(self, dt, tiles):
        """
        Frame güncellemesi
        
        Args:
            dt: Delta time
            tiles: Tile listesi (çarpışma için)
        """
        if not self.is_alive:
            return
        
        # Hareket animasyonu
        if self.turn_state == "moving":
            self.move_progress += self.move_speed * dt
            
            if self.move_progress >= 1.0:
                # Hareket tamamlandı
                self.move_progress = 1.0
                self.grid_x = self.target_grid_x
                self.grid_y = self.target_grid_y
                self.x = self.grid_x * self.size
                self.y = self.grid_y * self.size
                self.rect.x = int(self.x)
                self.rect.y = int(self.y)
                
                # Hedefe ulaştıktan sonra tile kontrolü
                self._check_landing(tiles)
                
                # Tur bitti, yeni tur başlat
                self.turn_state = "waiting"
                self.will_jump = False
            else:
                # Animasyon devam ediyor
                start_x = (self.grid_x * self.size)
                start_y = (self.grid_y * self.size)
                target_x = (self.target_grid_x * self.size)
                target_y = (self.target_grid_y * self.size)
                
                # Eğri interpolasyon (zıplarken yukarı çık)
                t = self.move_progress
                if self.will_jump:
                    # Parabol eğrisi (zıplama) - negatif yukarı yönde hareket
                    arc = JUMP_ARC_HEIGHT * (1 - (2*t - 1)**2)
                    self.x = start_x + (target_x - start_x) * t
                    self.y = start_y + (target_y - start_y) * t + arc
                else:
                    # Düz hareket
                    self.x = start_x + (target_x - start_x) * t
                    self.y = start_y + (target_y - start_y) * t
                
                self.rect.x = int(self.x)
                self.rect.y = int(self.y)
        
        # Oyun sonu kontrolü
        if self.resource_manager and self.resource_manager.is_game_over():
            self.is_alive = False
    
    def handle_input(self, keys, current_time):
        """
        Turn-based klavye girişlerini işle
        
        Args:
            keys: pygame.key.get_pressed()
            current_time: pygame.time.get_ticks() / 1000.0
        """
        if not self.is_alive:
            return
        
        # Hareket animasyonu devam ediyorsa input alma
        if self.turn_state == "moving":
            return
        
        # Input cooldown
        if current_time - self.last_input_time < self.input_cooldown:
            return
        
        # SPACE tuşu -> Zıplama seçimi (toggle)
        if keys[pygame.K_SPACE]:
            self.will_jump = not self.will_jump
            self.turn_state = "jump_selected" if self.will_jump else "waiting"
            self.last_input_time = current_time
            status = "JUMP mode ON" if self.will_jump else "JUMP mode OFF"
            print(f"⚡ {status}")
            return
        
        # Yön tuşları -> Hareket yönü seç ve hareketi başlat
        dx, dy = 0, 0
        direction_pressed = False
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = -1
            direction_pressed = True
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = 1
            direction_pressed = True
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -1
            direction_pressed = True
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = 1
            direction_pressed = True
        
        if direction_pressed:
            self.last_input_time = current_time
            self._try_move(dx, dy)
    
    def _try_move(self, dx, dy):
        """
        Belirtilen yöne hareket etmeyi dene
        
        Args:
            dx, dy: Grid yönü (-1, 0, 1)
        """
        # Eğer jump modundaysa önceden token tüket; bitmişse hareket etme
        if self.will_jump:
            if self.resource_manager:
                can_continue = self.resource_manager.use_jump()
                if not can_continue:
                    self.is_alive = False
                    return
        # Hedef grid pozisyonunu hesapla
        new_grid_x = self.grid_x + dx
        new_grid_y = self.grid_y + dy
        
        # Grid sınırlarını kontrol et
        if new_grid_x < 0 or new_grid_x >= GRID_COLS:
            print("🚫 Out of bounds (X)")
            return
        if new_grid_y < 0 or new_grid_y >= GRID_ROWS:
            print("🚫 Out of bounds (Y)")
            return
        
        # Hedefi ayarla ve hareketi başlat
        self.target_grid_x = new_grid_x
        self.target_grid_y = new_grid_y
        self.move_progress = 0.0
        self.turn_state = "moving"
        
        jump_str = " + JUMP" if self.will_jump else ""
        print(f"➡️  Moving to ({new_grid_x}, {new_grid_y}){jump_str}")
    
    def _check_landing(self, tiles):
        """
        Hedefe ulaştıktan sonra tile kontrolü yap
        
        Args:
            tiles: Tile listesi
        """
        # Ok tarafından itildiyse, hedef tile'ın hasarını alma (çift hasar önleme)
        if self.just_pushed:
            self.just_pushed = False
            return
            
        for tile in tiles:
            if not tile.is_solid:
                continue
            
            # Oyuncu ile aynı grid pozisyonunda mı?
            tile_grid_x = tile.x // self.size
            tile_grid_y = tile.y // self.size
            
            if tile_grid_x == self.grid_x and tile_grid_y == self.grid_y:
                # Zıplamadıysa ve siyah tile ise can götür
                if not self.will_jump and hasattr(tile, 'on_player_land'):
                    tile.on_player_land(self)
                elif self.will_jump:
                    print("🦘 Jumped over tile!")
                break
    
    def check_collectibles(self, collectibles):
        """
        Toplanabilir objelerle çarpışma kontrolü
        
        Args:
            collectibles: Collectible objesi listesi
            
        Returns:
            list: Toplanan objeler
        """
        collected = []
        
        for item in collectibles:
            # Güvenlik: Beklenen arayüz yoksa atla
            if not hasattr(item, 'rect'):
                continue
            if hasattr(item, 'is_collected') and item.is_collected():
                continue
            
            if self.rect.colliderect(item.rect):
                if hasattr(item, 'collect'):
                    item.collect(self)
                    collected.append(item)
        
        return collected
    
    def push(self, dx, dy):
        """
        Oyuncuyu belirli yöne it (Triangle tarafından)
        İleride: İtme animasyonu eklenebilir
        
        Args:
            dx: X yönünde grid sayısı
            dy: Y yönünde grid sayısı
        """
        print(f"🔺 Pushed by triangle!")
        # Şimdilik itmeyi devre dışı bırak
        # self._try_move(dx, dy)
    
    def draw(self, screen, camera_offset=(0, 0)):
        """
        Oyuncuyu çiz
        
        Args:
            screen: Pygame surface
            camera_offset: Kamera kayması
        """
        if not self.is_alive:
            return
        
        draw_x = int(self.x) - camera_offset[0]
        draw_y = int(self.y) - camera_offset[1]
        
        # Zıplama modu göstergesi (parlama efekti)
        if self.will_jump and self.turn_state == "jump_selected":
            center = (draw_x + self.size // 2, draw_y + self.size // 2)
            glow_radius = self.size // 2 + 5
            glow_surface = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (50, 255, 50, 100), (glow_radius, glow_radius), glow_radius)
            screen.blit(glow_surface, (center[0] - glow_radius, center[1] - glow_radius))
        
        # Sprite varsa sprite çiz, yoksa eski daire
        if self.sprite:
            screen.blit(self.sprite, (draw_x, draw_y))
        else:
            # Fallback: Yeşil daire
            center = (draw_x + self.size // 2, draw_y + self.size // 2)
            radius = self.size // 2 - 2
            pygame.draw.circle(screen, self.color, center, radius)
            pygame.draw.circle(screen, (0, 0, 0), center, radius, 2)
    
    def draw_ui(self, screen):
        """
        Oyuncu UI (kalpler ve jump token'lar) — haritanın üstünde görünür.
        """
        font = pygame.font.Font(None, int(18 * SCALE))
        
        # Can bilgisi
        if not self.resource_manager:
            return
        info = self.resource_manager.get_lives_info()
        
        # Üstte yarı-transparan üst şerit ve UI yerleşimi
        heart_size = int(32 * SCALE)
        token_size = int(20 * SCALE)
        start_x = int(10 * SCALE)
        start_y = int(6 * SCALE)
        spacing = int(40 * SCALE)
        try:
            sw, sh = screen.get_size()
            bar_h = max(int(54 * SCALE), heart_size + token_size + int(16 * SCALE))
            top_bar = pygame.Surface((sw, bar_h), pygame.SRCALPHA)
            top_bar.fill((0, 0, 0, 120))
            screen.blit(top_bar, (0, 0))
            pygame.draw.line(screen, (80, 80, 80), (0, bar_h), (sw, bar_h), 1)
        except Exception:
            pass
        
        # 3 kalp çiz
        for i in range(3):
            x = start_x + i * spacing
            if self.heart_sprite:
                # Sprite varsa onu kullan
                if i < info['main_lives']:
                    screen.blit(self.heart_sprite, (x, start_y))
                else:
                    # Boş kalp için soluk göster
                    faded = self.heart_sprite.copy()
                    faded.set_alpha(50)
                    screen.blit(faded, (x, start_y))
            else:
                # Sprite yoksa renkli kare
                if i < info['main_lives']:
                    pygame.draw.rect(screen, (255, 0, 0), (x, start_y, heart_size, heart_size))
                else:
                    pygame.draw.rect(screen, (100, 100, 100), (x, start_y, heart_size, heart_size))
        
        # Kalplerin altında 3 yeşil kare (jump tokens)
        token_y = start_y + heart_size + int(5 * SCALE)
        for i in range(3):
            x = start_x + i * spacing + (heart_size - token_size) // 2  # Ortalanmış
            if i < info['jump_tokens']:
                pygame.draw.rect(screen, (50, 200, 50), (x, token_y, token_size, token_size))
            else:
                pygame.draw.rect(screen, (100, 100, 100), (x, token_y, token_size, token_size))
        
        # Yıldız ve anahtar (kalbin sağında)
        text_x = start_x + 3 * spacing + int(10 * SCALE)
        text_y = start_y
        
        # Oyun içinde gri metinler kaldırıldı (yıldız/anahtar metinleri gösterme)
        
        # Turn durumu (alt kısımda)
        # Oyun içinde kontrol ipuçları (SPACE/WASD) metinleri kaldırıldı
    
    def reset(self, x, y):
        """
        Oyuncuyu başlangıç pozisyonuna döndür
        
        Args:
            x, y: Yeni pozisyon
        """
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        self.grid_x = x // self.size
        self.grid_y = y // self.size
        self.target_grid_x = self.grid_x
        self.target_grid_y = self.grid_y
        self.turn_state = "waiting"
        self.will_jump = False
        self.move_progress = 0.0
        self.just_pushed = False  # İtme bayrağını temizle
        self.stars_collected = 0
        self.has_key = False
        self.is_alive = True
        if self.resource_manager:
            self.resource_manager.reset()
        print("🔄 Player reset!")


# ============================================
# TEST CODE
# ============================================
if __name__ == "__main__":
    print("Player sınıfı test edilemez (pygame gerekli)")
    print("main.py'den çalıştırın")
