"""
ReVerse - Game Manager
Ana oyun döngüsü ve state yönetimi (Unity GameManager benzeri)
"""
import pygame
import sys
from config import *
from Scripts.Utils.Constants import *
from Levels.LevelData import LevelData
from Levels.LevelLoader import LevelLoader
from Scripts.Systems.RotationManager import RotationManager

class GameManager:
    """
    Oyunun ana yönetici sınıfı
    Unity MonoBehaviour.Singleton benzeri
    """
    
    def __init__(self):
        # Pygame başlatma
        pygame.init()
        
        # Ekran ayarları (RESIZABLE)
        if FULLSCREEN:
            # Borderless fullscreen (monitör boyutunda pencere)
            info = pygame.display.Info()
            self.screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.NOFRAME | pygame.RESIZABLE)
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        
        pygame.display.set_caption("ReVerse | Puzzle Platformer")
        self.is_maximized = False
        
        # Render surface (gerçek oyun grid boyutunda)
        self.render_surface = pygame.Surface((GRID_SIZE * GRID_COLS, GRID_SIZE * GRID_ROWS))
        
        # Saat (FPS kontrolü)
        self.clock = pygame.time.Clock()
        
        # Oyun durumu
        self.state = STATE_PLAYING
        self.current_level = 1
        self.running = True
        
        # Toplanan öğeleri level bazında kaydet: ('star'|'key', gx, gy)
        self.collected_by_level = {}
        # Tüm seviyeler arası global toplanan seti (tip, gx, gy)
        self.collected_global = set()
        # Rotate sembollerini tek seferlik yapmak için kullanılan set (level-> {(gx,gy)})
        self.used_rotation_symbols = {}

        # Level sistemi
        self.level_loader = LevelLoader(GRID_SIZE)
        self.load_level(self.current_level)
        
        # Kamera
        self.camera_x = 0
        self.camera_y = 0
        
        # Font (scale'e göre ayarlanmış)
        self.font_small = pygame.font.Font(None, int(20 * SCALE))
        self.font_medium = pygame.font.Font(None, int(28 * SCALE))
        self.font_large = pygame.font.Font(None, int(48 * SCALE))
        
        
        
        # Debug overlay
        self.debug_enabled = False
        # Help overlay (TAB to toggle)
        self.help_enabled = True
        # Rotation Manager
        self.rotation_manager = RotationManager()
        # Rotate tetikleme cooldown (seviye geçişinde çifte tetiklemeyi önler)
        self.rotate_cooldown = 0.0
        # Rotate tetikleme kenar algılama (üzerinden ayrılmadan tekrar tetiklenmesin)
        self.on_rotate = False
    
    def toggle_fullscreen(self):
        """Tam ekran modunu aç/kapat"""
        global FULLSCREEN
        FULLSCREEN = not FULLSCREEN
        
        if FULLSCREEN:
            # Borderless fullscreen (monitör boyutunda pencere)
            info = pygame.display.Info()
            self.screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.NOFRAME | pygame.RESIZABLE)
            print("🖥️ Borderless Fullscreen ON (F11 or ESC to exit)")
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
            print("🖥️ Windowed mode (F11 for fullscreen)")
        # Tam ekran değişiminde maximize bayrağını sıfırla
        self.is_maximized = False

    def toggle_maximize(self):
        """Pencereyi ekran boyutuna büyüt/küçült (windowed maximize)."""
        if FULLSCREEN:
            # Fullscreen açıkken maximize anlamsız; önce fullscreen kapatılmalı
            print("ℹ️ Disable fullscreen to use maximize (F11)")
            return
        info = pygame.display.Info()
        if not self.is_maximized:
            self.screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.RESIZABLE)
            self.is_maximized = True
            print("🗖 Window maximized (F10 to restore)")
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
            self.is_maximized = False
            print("🗗 Window restored (F10 to maximize)")
    
    def load_level(self, level_number):
        """
        Belirli bir level'i yükle
        
        Args:
            level_number (int): Level numarası
        """
        level_data = LevelData.get_level(level_number)
        
        if not level_data:
            print(f"❌ Level {level_number} not found!")
            return False
        
        try:
            self.level_objects = self.level_loader.load_level(level_data)
            self.player = self.level_objects["player"]
            self.tiles = self.level_objects["tiles"]
            self.collectibles = self.level_objects["collectibles"]
            self.door = self.level_objects["door"]
            self.rotation_symbols = self.level_objects["rotation_symbols"]
            # Tek seferlik kullanılan rotate sembollerini filtrele
            used_set = self.used_rotation_symbols.get(level_number, set())
            if used_set:
                kept = []
                for sym in self.rotation_symbols:
                    gx = sym.x // GRID_SIZE
                    gy = sym.y // GRID_SIZE
                    if (gx, gy) not in used_set:
                        kept.append(sym)
                self.rotation_symbols = kept
            
            # Daha önce toplananları gizle (hem bu level'a ait kayıtlar hem global kayıtlar)
            hidden = 0
            collected_set = self.collected_by_level.get(level_number, set())
            for item in self.collectibles:
                gx = item.x // GRID_SIZE if hasattr(item, 'x') else 0
                gy = item.y // GRID_SIZE if hasattr(item, 'y') else 0
                if item.__class__.__name__ == 'Star':
                    key = ('star', gx, gy)
                elif item.__class__.__name__ == 'Key':
                    key = ('key', gx, gy)
                else:
                    key = None
                if key and (key in collected_set or key in self.collected_global):
                    item.collected = True
                    hidden += 1
            if hidden:
                print(f"🙈 Hidden previously collected items: {hidden}")

            print(f"✅ Level {level_number} loaded successfully!")
            return True
        
        except Exception as e:
            print(f"❌ Error loading level: {e}")
            return False
    
    def run(self):
        """Ana oyun döngüsü (Unity Update loop benzeri)"""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time (saniye)
            
            self.handle_events()
            self.update(dt)
            self.draw()
            
            pygame.display.flip()
        
        self.quit()
    
    def handle_events(self):
        """
        Pygame event'lerini işle
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                # ESC - Çıkış
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                
                # R - Level reset
                elif event.key == pygame.K_r:
                    self.reset_level()
                
                # N - Debug panel toggle (level switch disabled)
                elif event.key == pygame.K_n:
                    self.debug_enabled = not self.debug_enabled
                    print(f"🔧 Debug overlay: {'ON' if self.debug_enabled else 'OFF'}")
                
                # G - God mode toggle (debug)
                elif event.key == pygame.K_g:
                    import config
                    config.GOD_MODE = not config.GOD_MODE
                    print(f"🛡️ God Mode: {'ON' if config.GOD_MODE else 'OFF'}")

                # F11 - Fullscreen toggle
                elif event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                # F10 - Maximize toggle (windowed)
                elif event.key == pygame.K_F10:
                    self.toggle_maximize()
                # TAB - Controls help overlay toggle
                elif event.key == pygame.K_TAB:
                    self.help_enabled = not self.help_enabled
                    print(f"❓ Help overlay: {'ON' if self.help_enabled else 'OFF'}")
    
    def update(self, dt):
        """
        Frame güncellemesi
        
        Args:
            dt: Delta time
        """
        if self.state == STATE_PLAYING:
            # Cooldown azalt
            if self.rotate_cooldown > 0:
                self.rotate_cooldown = max(0.0, self.rotate_cooldown - dt)
            self.update_gameplay(dt)
        elif self.state == STATE_PAUSED:
            pass  # Pause menüsü (ileride)
        elif self.state == STATE_WIN:
            pass  # Win ekranı (ileride)
        elif self.state == STATE_GAME_OVER:
            pass  # Game Over ekranı (ileride)
    
    def update_gameplay(self, dt):
        """
        Oyun içi güncellemeler
        
        Args:
            dt: Delta time
        """
        # Klavye girişleri
        keys = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks() / 1000.0
        self.player.handle_input(keys, current_time)
        
        # Player güncelle
        self.player.update(dt, self.tiles)
        
        # Collectible'ları kontrol et
        collected = self.player.check_collectibles(self.collectibles)
        # Toplananları level bazında kaydet
        if collected:
            level_set = self.collected_by_level.setdefault(self.current_level, set())
            for item in collected:
                gx = item.x // GRID_SIZE if hasattr(item, 'x') else 0
                gy = item.y // GRID_SIZE if hasattr(item, 'y') else 0
                if item.__class__.__name__ == 'Star':
                    key = ('star', gx, gy)
                    level_set.add(key)
                    self.collected_global.add(key)
                elif item.__class__.__name__ == 'Key':
                    key = ('key', gx, gy)
                    level_set.add(key)
                    self.collected_global.add(key)
        
        # Rotation symbol kontrolü: Level 1 ↔ 2 toggle + konumu/stats'ı koru
        # Yalnızca simgenin üzerine YENİDEN basıldığında (kenar) tetikle
        collided_symbol = None
        for symbol in self.rotation_symbols:
            if self.player.rect.colliderect(symbol.rect):
                collided_symbol = symbol
                break

        if collided_symbol is not None:
            if not self.on_rotate and self.rotate_cooldown == 0.0:
                collided_symbol.activate(self)
                # Bu sembolü kullanılmış olarak işaretle (tek seferlik)
                gx = collided_symbol.x // GRID_SIZE
                gy = collided_symbol.y // GRID_SIZE
                self.used_rotation_symbols.setdefault(self.current_level, set()).add((gx, gy))
                # Karşı levelde aynı koordinattaki rotate de devre dışı olsun
                other_level = 2 if self.current_level == 1 else 1
                self.used_rotation_symbols.setdefault(other_level, set()).add((gx, gy))
                collided_symbol.consumed = True
                target_level = 2 if self.current_level == 1 else 1
                print(f"🔁 Switching to Level {target_level} (carry stars+key, keep pos)")
                self.switch_to_level(target_level, carry_stars=True, preserve_pos=True)
                # Rotate sonrası ekstra snap davranışı kaldırıldı (artık '>' '<' tile'larında uygulanıyor)
                self.on_rotate = True
            return  # Bu frame'i bitir (çifte tetiklemeyi kesin önle)
        else:
            # Üzerinden ayrıldı
            self.on_rotate = False
        
        # Kapı kontrolü
        if self.door and self.player.rect.colliderect(self.door.rect):
            if self.door.try_enter(self.player, current_time):
                self.level_complete()
        
        # Tile'ları güncelle
        self.level_loader.update_all(dt)
        
        # Kamera güncelle
        self.update_camera()
        
        # Game Over kontrolü
        if not self.player.is_alive:
            self.game_over()
    
    def update_camera(self):
        """
        Kamerayı player'a göre ayarla
        """
        # Basit kamera takibi (grid boyutuna göre)
        grid_width = GRID_SIZE * GRID_COLS
        grid_height = GRID_SIZE * GRID_ROWS
        target_x = self.player.x - grid_width // 2 + self.player.size // 2
        target_y = self.player.y - grid_height // 2 + self.player.size // 2
        
        # Kamera yumuşatma
        self.camera_x += (target_x - self.camera_x) * 0.1
        self.camera_y += (target_y - self.camera_y) * 0.1
        
        # Level sınırları içinde tut
        level_width, level_height = self.level_loader.get_level_bounds()
        
        self.camera_x = max(0, min(self.camera_x, level_width - grid_width))
        self.camera_y = max(0, min(self.camera_y, level_height - grid_height))
    
    def draw(self):
        """Ekrana çizim"""
        # Arka plan (render surface'e çiz)
        self.render_surface.fill(BG_COLOR)
        
        # Grid çizgileri (render surface'e)
        if SHOW_GRID:
            self.draw_grid()
        
        # Tüm objeleri çiz (render surface'e)
        camera_offset = (int(self.camera_x), int(self.camera_y))
        self.level_loader.draw_all(self.render_surface, camera_offset)
        
        # Önce üst HUD’ı ekrana çiz (haritanın üzerinde bağımsız)
        self.player.draw_ui(self.screen)
        
        # Haritayı HUD’ın altında çizecek şekilde ölçekle ve konumlandır
        map_height = max(0, SCREEN_HEIGHT - HUD_HEIGHT)
        scaled_surface = pygame.transform.scale(self.render_surface, (SCREEN_WIDTH, map_height))
        self.screen.blit(scaled_surface, (0, HUD_HEIGHT))
        
        # State'e göre overlay
        if self.state == STATE_WIN:
            self.draw_win_screen()
        elif self.state == STATE_GAME_OVER:
            self.draw_game_over_screen()
        
        # Draw debug overlay if enabled
        if self.debug_enabled:
            self._draw_debug_overlay()
        # Draw controls help overlay if enabled (tab menu)
        if self.help_enabled:
            self._draw_help_overlay()
    
    def draw_grid(self):
        """Grid çizgilerini çiz"""
        camera_offset = (int(self.camera_x), int(self.camera_y))
        grid_width = GRID_SIZE * GRID_COLS
        grid_height = GRID_SIZE * GRID_ROWS
        
        # Dikey çizgiler
        for x in range(0, grid_width + GRID_SIZE, GRID_SIZE):
            world_x = x + camera_offset[0]
            screen_x = world_x - camera_offset[0]
            pygame.draw.line(self.render_surface, GRID_LINE_COLOR, 
                           (screen_x, 0), (screen_x, grid_height), 1)
        
        # Yatay çizgiler
        for y in range(0, grid_height + GRID_SIZE, GRID_SIZE):
            world_y = y + camera_offset[1]
            screen_y = world_y - camera_offset[1]
            pygame.draw.line(self.render_surface, GRID_LINE_COLOR, 
                           (0, screen_y), (grid_width, screen_y), 1)
    
    def draw_ui(self):
        """UI elementlerini çiz"""
        # Player bilgileri (metin içeren gri yazılar varsa devre dışı bırak)
        # Oyuncu kalp/jump gibi görselleri çiziyor olabilir; yalnızca metinleri gizleyelim.
        try:
            if hasattr(self.player, 'draw_ui_texts'):
                # Eğer oyuncu metinleri ayrı çiziyorsa, kapat
                pass  # metinleri çizme
            else:
                # Varsayılan: oyuncu UI'sini yine de çiz, fakat metinler oyunda kaldırılacak
                self.player.draw_ui(self.screen)
        except Exception:
            self.player.draw_ui(self.screen)
        
        # Oyun içi Level/FPS yazılarını gizle (sadece debug panelde gösterilecek)
        # Level yazısı ve FPS artık çizilmiyor
        pass
    
    def draw_win_screen(self):
        """Kazanma ekranı"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Yazı
        win_text = self.font_large.render("LEVEL COMPLETE!", True, (50, 255, 50))
        text_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(win_text, text_rect)

        # İpucu: Yeni strateji denemek için R'ye basın
        hint_text = self.font_medium.render("Press R to try a new strategy", True, UI_TEXT_COLOR)
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(hint_text, hint_rect)
    
    def _draw_debug_overlay(self):
        # Panel config
        panel_width = 280
        panel_margin = 12
        panel_padding = 10
        sw, sh = self.screen.get_size()
        panel_rect = pygame.Rect(sw - panel_width - panel_margin, panel_margin, panel_width, sh - panel_margin*2)

        # Semi-transparent background (stronger alpha) + border
        overlay = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA).convert_alpha()
        overlay.fill((0, 0, 0, 200))  # darker for readability
        self.screen.blit(overlay, panel_rect.topleft)
        pygame.draw.rect(self.screen, (80, 80, 80), panel_rect, 1)

        # Text config
        try:
            font = pygame.font.SysFont('consolas', 18, bold=False)
        except Exception:
            font = pygame.font.SysFont(None, 18)
        color = (220, 220, 220)  # lighter gray
        line_h = 20
        x = panel_rect.x + panel_padding
        y = panel_rect.y + panel_padding

        def draw_line(label, value=None):
            nonlocal y
            text = f"{label}: {value}" if value is not None else str(label)
            # shadow for readability
            shadow = font.render(text, True, (0, 0, 0))
            self.screen.blit(shadow, (x+1, y+1))
            surf = font.render(text, True, color)
            self.screen.blit(surf, (x, y))
            y += line_h

        # Collect state info
        lvl = getattr(self, 'current_level', 1)
        px, py = self.player.grid_x, self.player.grid_y
        stars = getattr(self.player, 'stars', 0)
        has_key = getattr(self.player, 'has_key', False)
        lives = getattr(self.player, 'lives', None)
        jumps = getattr(self.player, 'jump_tokens', None)
        rot_cd = round(self.rotate_cooldown, 2)
        fps = int(self.clock.get_fps())
        import config
        god = "ON" if config.GOD_MODE else "OFF"

        # Draw sections
        draw_line("DEBUG")
        draw_line("──────────────")
        draw_line("Level", lvl)
        draw_line("Player", f"({px},{py})")
        draw_line("Stars", stars)
        draw_line("Key", "Yes" if has_key else "No")
        if lives is not None:
            draw_line("Lives", lives)
        if jumps is not None:
            draw_line("JumpTokens", jumps)
        draw_line("RotateCD", rot_cd)
        draw_line("GodMode", god)
        draw_line("FPS", fps)

        # Counts
        rot_cnt = len(getattr(self.level_loader, 'rotation_symbols', []))
        coll_cnt = len(getattr(self.level_loader, 'collectibles', []))
        tile_cnt = len(getattr(self.level_loader, 'tiles', []))
        draw_line("──────────────")
        draw_line("Tiles", tile_cnt)
        draw_line("Collectibles", coll_cnt)
        draw_line("RotSymbols", rot_cnt)

        # Hints
        draw_line("──────────────")
        draw_line("Hint", "N: Toggle debug panel")

    def _draw_help_overlay(self):
        # Right-side panel similar to debug, but dedicated to controls
        panel_width = 340
        panel_margin = 12
        panel_padding = 10
        sw, sh = self.screen.get_size()
        panel_rect = pygame.Rect(sw - panel_width - panel_margin, panel_margin, panel_width, sh - panel_margin*2)

        overlay = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA).convert_alpha()
        overlay.fill((0, 0, 0, 210))
        self.screen.blit(overlay, panel_rect.topleft)
        pygame.draw.rect(self.screen, (100, 100, 100), panel_rect, 1)

        try:
            title_font = pygame.font.SysFont('consolas', 20, bold=True)
            font = pygame.font.SysFont('consolas', 18)
        except Exception:
            title_font = pygame.font.SysFont(None, 20)
            font = pygame.font.SysFont(None, 18)
        color = (230, 230, 230)
        line_h = 22
        x = panel_rect.x + panel_padding
        y = panel_rect.y + panel_padding

        def draw(text, bold=False):
            nonlocal y
            f = title_font if bold else font
            shadow = f.render(text, True, (0, 0, 0))
            self.screen.blit(shadow, (x+1, y+1))
            surf = f.render(text, True, color)
            self.screen.blit(surf, (x, y))
            y += line_h

        draw("CONTROLS", bold=True)
        draw("──────────────")
        draw("TAB: Show/Hide this help")
        draw("A / LEFT: Move left")
        draw("D / RIGHT: Move right")
        draw("SPACE: Select jump / cancel")
        draw("WASD: Move after jump select")
        draw("R: Restart level")
        draw("N: Toggle debug panel")
        draw("G: Toggle God mode")
        draw("F10: Maximize window")
        draw("F11: Toggle fullscreen")
        draw("ESC: Quit game")
    
    def draw_game_over_screen(self):
        """Game Over ekranı"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Yazı
        go_text = self.font_large.render("GAME OVER", True, (255, 50, 50))
        text_rect = go_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(go_text, text_rect)
        
        hint_text = self.font_medium.render("Press R to restart", True, UI_TEXT_COLOR)
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(hint_text, hint_rect)
    
    def rotate_world(self):
        """
        Dünyayı 90 derece döndür (RotationManager kullanarak)
        Üçgen yönlerini saat yönünde döndür
        """
        self.rotation_manager.rotate_world_90(self.level_loader)
    
    def level_complete(self):
        """Level tamamlandı"""
        self.state = STATE_WIN
        print(f"🎉 Level {self.current_level} completed!")
        self.reset_player_progress()
    
    def game_over(self):
        """Game Over"""
        self.state = STATE_GAME_OVER
        print("💀 Game Over!")
        self.reset_player_progress()
    
    def reset_level(self):
        """Level'i resetle"""
        self.level_loader.reset_level()
        self.rotation_manager.reset()
        self.state = STATE_PLAYING
        # Seviye yüklenince kısa bir cooldown ver (spawn'da anında tetiklemeyi engelle)
        self.rotate_cooldown = 0.5
        # Yeni levele geçerken oyuncu hâlâ bir rotate üzerinde olabilir; tekrar tetiklenmeyi engelle
        self.on_rotate = True
        print("🔄 Level restarted!")
    
    def next_level(self):
        """Sonraki level'e geç"""
        next_level = self.current_level + 1
        
        if next_level > LevelData.get_total_levels():
            print("🎊 All levels completed!")
            self.current_level = 1  # Başa dön
        else:
            self.current_level = next_level
        
        self.load_level(self.current_level)
        self.state = STATE_PLAYING

    def switch_to_level(self, target_level, carry_stars=False, preserve_pos=False):
        """
        Belirli bir level'e geç ve istenirse yıldız sayısını taşı, konumu koru
        """
        carried_stars = self.player.stars_collected if (carry_stars and hasattr(self, 'player')) else None
        carried_key = self.player.has_key if hasattr(self, 'player') else None
        saved_grid = (self.player.grid_x, self.player.grid_y) if (preserve_pos and hasattr(self, 'player')) else None
        self.current_level = target_level
        self.load_level(self.current_level)
        if carried_stars is not None:
            self.player.stars_collected = carried_stars
        if carried_key is not None:
            self.player.has_key = carried_key
        # Konumu koru (grid bazlı), sınırlar içinde tut
        if saved_grid is not None:
            gx, gy = saved_grid
            # Yeni level boyutları
            grid_w = self.level_loader.grid_width
            grid_h = self.level_loader.grid_height
            gx = max(0, min(gx, grid_w - 1))
            gy = max(0, min(gy, grid_h - 1))
            self.player.grid_x = gx
            self.player.grid_y = gy
            self.player.x = gx * GRID_SIZE
            self.player.y = gy * GRID_SIZE
            self.player.rect.x = self.player.x
            self.player.rect.y = self.player.y
        self.state = STATE_PLAYING
    
    def quit(self):
        """Oyunu kapat"""
        # Oyuncu ilerlemesini ve toplananları sıfırla
        try:
            self.reset_player_progress()
        except Exception:
            pass
        print("\n👋 Thanks for playing ReVerse!")
        pygame.quit()
        sys.exit()

    def snap_player_in_front_of_nearest_arrow(self):
        pass  # Artık kullanılmıyor

    def reset_player_progress(self):
        """Oyuncunun topladığı verileri sıfırla (yıldız, anahtar, görünmezlik kayıtları)"""
        # Global ve level-bazlı toplanan kayıtlarını temizle
        self.collected_by_level.clear()
        self.collected_global.clear()
        # Rotate haklarını tamamen sıfırla
        self.used_rotation_symbols.clear()
        # Oyuncu envanterini temizle
        if hasattr(self, 'player') and self.player:
            self.player.stars_collected = 0
            self.player.has_key = False
        # Rotate tetikleme durumlarını temizle
        self.rotate_cooldown = 0.0
        self.on_rotate = False
        # Level'i yeniden yükle ki filtrelenen rotate'ler geri gelsin
        try:
            self.load_level(self.current_level)
        except Exception:
            pass
        print("🧹 Player progress reset (stars, key, collections)")


# ============================================
# ENTRY POINT
# ============================================
if __name__ == "__main__":
    print("=== ReVerse - Starting Game ===\n")
    
    game = GameManager()
    game.run()
