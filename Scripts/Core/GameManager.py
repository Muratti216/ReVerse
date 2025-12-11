"""
ReVerse - Game Manager
Ana oyun döngüsü ve state yönetimi (Unity GameManager benzeri)
"""
import pygame
import sys
import os
import json
import config
from config import *
from Scripts.Utils.Constants import *
from Levels.LevelData import LevelData
from Levels.LevelLoader import LevelLoader
from Scripts.Systems.RotationManager import RotationManager
from Scripts.Systems.ResourceManager import ResourceManager

class GameManager:
    """
    Oyunun ana yönetici sınıfı
    Unity MonoBehaviour.Singleton benzeri
    """
    
    def __init__(self):
        # Pygame başlatma
        pygame.init()
        
        # Ekran ayarları (RESIZABLE)
        # VSYNC için pygame.SCALED yerine clock.tick() kullanılacak (daha uyumlu)
        display_flags = pygame.RESIZABLE
        
        if FULLSCREEN:
            # Borderless fullscreen (monitör boyutunda pencere)
            info = pygame.display.Info()
            self.screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.NOFRAME | display_flags)
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), display_flags)
        
        pygame.display.set_caption("ReVerse | Puzzle Platformer")
        self.is_maximized = False

        # Ortak kaynak yöneticisi (can + jump token) — level geçişinde korunur
        self.resource_manager = ResourceManager()
        
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
        
        # Font cache (HUD metinleri için)
        self._font_cache = {}
        self._init_font_cache()

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
        
        # Zamanlayıcı ve en iyi süreler
        self.level_start_time = 0.0
        self.level_end_time = 0.0   # Win/GameOver olduğunda süreyi dondur
        self.best_times = {}
        self.best_times_path = os.path.join(os.getcwd(), "best_times.json")
        self._load_best_times()
        
        # Anahtar spawn kontrolü
        self.key_spawn_point = None
        self.key_spawned = False
    
    def _init_font_cache(self):
        """HUD için sık kullanılan font boyutlarını önbellek"""
        base_sizes = [12, 14, 16, 18, 20]
        for size in base_sizes:
            scaled_size = int(size * SCALE)
            try:
                self._font_cache[scaled_size] = pygame.font.SysFont('consolas', scaled_size, bold=False)
            except:
                self._font_cache[scaled_size] = pygame.font.Font(None, scaled_size)
    
    def _get_cached_font(self, size):
        """Cache'den font al, yoksa oluştur"""
        if size not in self._font_cache:
            try:
                self._font_cache[size] = pygame.font.SysFont('consolas', size, bold=False)
            except:
                self._font_cache[size] = pygame.font.Font(None, size)
        return self._font_cache[size]
    
    def toggle_fullscreen(self):
        """Tam ekran modunu aç/kapat"""
        global FULLSCREEN
        FULLSCREEN = not FULLSCREEN
        
        # Display flags (VSYNC via clock.tick)
        display_flags = pygame.RESIZABLE
        
        if FULLSCREEN:
            # Borderless fullscreen (monitör boyutunda pencere)
            info = pygame.display.Info()
            self.screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.NOFRAME | display_flags)
            print("🖥️ Borderless Fullscreen ON (F11 or ESC to exit)")
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), display_flags)
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
            # Can/jump durumunu level geçişinde koru
            try:
                self.player.resource_manager = self.resource_manager
            except Exception:
                pass
            # Level'e özel oyuncu sprite'ı uygula
            try:
                if level_number == 2:
                    self.player.set_sprite("Assets/Sprites/Avatar_Level2.png")
                else:
                    self.player.restore_default_sprite()
            except Exception as e:
                print(f"⚠️ Level sprite switch failed: {e}")
            # Anahtar spawn noktası (anahtar başlangıçta gizli)
            self.key_spawn_point = self.level_objects.get("key_spawn_point")
            self.key_spawned = False
            # Her level'de kapı için anahtar gereksinimi varsayılan: True
            try:
                self.player.require_key = True
            except Exception:
                pass

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

            # Timer'i sıfırla (ilk draw frame'inde başlayacak)
            self.level_start_time = 0.0
            # Yıldız şartı zaten sağlanmışsa anahtarı hemen göster
            self._maybe_spawn_key_if_ready()

            print(f"✅ Level {level_number} loaded successfully!")
            return True
        
        except (KeyError, ValueError, AttributeError) as e:
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

                # B - Reset best time (only on win/game over screens)
                elif event.key == pygame.K_b:
                    if self.state in (STATE_WIN, STATE_GAME_OVER):
                        self._reset_best_time_current_level()
    
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

        # Yıldızlar tamamlandıysa anahtarı spawn et
        self._maybe_spawn_key_if_ready()
        
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
        # Kapı her levelde anahtar gerektirir (anahtar taşınmıyorsa tekrar alınmalı)
        if hasattr(self.player, 'require_key'):
            self.player.require_key = True
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
        # Timer'ı ilk frame'de başlat (ekran göründüğünde)
        if self.level_start_time == 0.0:
            self.level_start_time = pygame.time.get_ticks() / 1000.0
            self.level_end_time = 0.0
        
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
        # HUD meta: hedef metni ve zamanlayıcılar
        self._draw_hud_meta()
        
        # Haritayı HUD’ın altında çizecek şekilde ölçekle ve konumlandır (dinamik boyut)
        sw, sh = self.screen.get_size()
        bar_h = self._hud_bar_height()
        map_height = max(0, sh - bar_h)
        scaled_surface = pygame.transform.scale(self.render_surface, (sw, map_height))
        self.screen.blit(scaled_surface, (0, bar_h))
        
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
        except (AttributeError, TypeError) as e:
            print(f"⚠️ Player UI draw failed: {e}")
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

        reset_text = self.font_medium.render("Press B to reset best time", True, UI_TEXT_COLOR)
        reset_rect = reset_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 90))
        self.screen.blit(reset_text, reset_rect)

    def _format_time(self, seconds: float) -> str:
        seconds = max(0.0, float(seconds))
        m = int(seconds // 60)
        s = int(seconds % 60)
        cs = int((seconds - int(seconds)) * 100)  # centiseconds
        return f"{m:02d}:{s:02d}.{cs:02d}"

    def _load_best_times(self):
        try:
            if os.path.exists(self.best_times_path):
                with open(self.best_times_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self.best_times = data
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️ Best times yüklenemedi: {e}")
            self.best_times = {}

    def _save_best_times(self):
        try:
            with open(self.best_times_path, "w", encoding="utf-8") as f:
                json.dump(self.best_times, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"⚠️ Best times kaydedilemedi: {e}")

    def _current_level_best(self):
        key = str(self.current_level)
        val = self.best_times.get(key)
        try:
            return float(val) if val is not None else None
        except (ValueError, TypeError):
            return None

    def _update_best_time_if_better(self, elapsed: float):
        key = str(self.current_level)
        prev = self._current_level_best()
        if prev is None or elapsed < prev:
            self.best_times[key] = round(float(elapsed), 3)
            self._save_best_times()

    def _reset_best_time_current_level(self):
        key = str(self.current_level)
        if key in self.best_times:
            del self.best_times[key]
            self._save_best_times()
            print(f"⏱️ Best time for level {key} reset.")
        else:
            print("ℹ️ No best time to reset for this level.")

    def _draw_hud_meta(self):
        # Ekran boyutu ve metinler
        sw, sh = self.screen.get_size()
        bar_h = self._hud_bar_height()
        # Merkez zamanlayıcı
        now = self.level_end_time if self.level_end_time else pygame.time.get_ticks() / 1000.0
        elapsed = now - self.level_start_time if self.level_start_time else 0.0
        best = self._current_level_best()
        best_text = self._format_time(best) if best is not None else "--:--.--"
        now_text = self._format_time(elapsed)
        center_text = f"Best: {best_text} | Now: {now_text}"
        # Daha okunaklı açık renk
        # Responsive center timer: shrink or split into 2 lines if needed
        margin = int(10 * SCALE)
        max_center_width = int(sw * 0.3) - margin  # center area: max 30% width
        font_size = int(16 * SCALE)
        center_font = self._get_cached_font(font_size)
        center_surf = center_font.render(center_text, True, (235, 235, 235))
        # Reduce font size until it fits, but keep legible
        while center_surf.get_width() > max_center_width and font_size > int(12 * SCALE):
            font_size -= 1
            center_font = self._get_cached_font(font_size)
            center_surf = center_font.render(center_text, True, (235, 235, 235))
        # If still too wide, split into two lines: Best / Now
        if center_surf.get_width() > max_center_width:
            best_line = f"Best: {best_text}"
            now_line = f"Now:  {now_text}"
            best_surf = center_font.render(best_line, True, (235, 235, 235))
            now_surf = center_font.render(now_line, True, (235, 235, 235))
            total_h = best_surf.get_height() + 2 + now_surf.get_height()
            bx = (sw - best_surf.get_width()) // 2
            by = (bar_h - total_h) // 2
            # Shadows
            best_shadow = center_font.render(best_line, True, (0, 0, 0))
            now_shadow = center_font.render(now_line, True, (0, 0, 0))
            self.screen.blit(best_shadow, (bx + 1, by + 1))
            self.screen.blit(best_surf, (bx, by))
            ny = by + best_surf.get_height() + 2
            nx = (sw - now_surf.get_width()) // 2
            self.screen.blit(now_shadow, (nx + 1, ny + 1))
            self.screen.blit(now_surf, (nx, ny))
        else:
            center_rect = center_surf.get_rect(center=(sw // 2, bar_h // 2))
            shadow = center_font.render(center_text, True, (0, 0, 0))
            self.screen.blit(shadow, (center_rect.x + 1, center_rect.y + 1))
            self.screen.blit(center_surf, center_rect.topleft)

        # Sağ tarafta hedef başlık + metin
        # Right margin for objective (separate from timer)
        right_margin = int(15 * SCALE)
        title_font = self._get_cached_font(int(14 * SCALE))
        body_font = self._get_cached_font(int(12 * SCALE))
        
        # Dynamically generate objective based on game state
        title = "STATUS"
        stars = self.player.stars_collected if hasattr(self.player, 'stars_collected') else 0
        required = self.player.required_stars if hasattr(self.player, 'required_stars') else STARS_TO_WIN
        has_key = self.player.has_key if hasattr(self.player, 'has_key') else False
        
        key_status = "Yes" if has_key else "No"
        if stars < required:
            body = f"Stars: {stars}/{required}  Key: {key_status}  Collect all stars"
        elif not has_key:
            body = f"Stars: {stars}/{required}  Key: {key_status}  Obtain the key"
        else:
            body = f"Stars: {stars}/{required}  Key: {key_status}  Go to exit"
        
        title_surf = title_font.render(title, True, (235, 235, 235))

        # Right-side max width for wrapping (about 25% of screen width on far right)
        max_width = int(sw * 0.25) - right_margin

        # Wrap body into lines
        words = body.split(' ')
        lines = []
        current = ''
        for w in words:
            test = (current + ' ' + w).strip()
            test_surf = body_font.render(test, True, (235, 235, 235))
            if test_surf.get_width() <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = w
        if current:
            lines.append(current)
        # Allow up to 5 lines; no ellipsis needed (show full text wrapped)
        # No truncation—let it wrap naturally

        # Compute total body height (tighter line spacing)
        line_spacing = 1  # pixels between lines
        body_surfs = [body_font.render(line, True, (235, 235, 235)) for line in lines]
        total_body_h = sum(s.get_height() for s in body_surfs) + (len(body_surfs) - 1) * line_spacing

        # Right alignment positions within HUD band
        tx = sw - right_margin - title_surf.get_width()
        # Center vertically: title + body block inside bar_h
        ty = max(2, (bar_h - (title_surf.get_height() + 2 + total_body_h)) // 2)

        # Draw title with shadow
        title_shadow = title_font.render(title, True, (0, 0, 0))
        self.screen.blit(title_shadow, (tx + 1, ty + 1))
        self.screen.blit(title_surf, (tx, ty))

        # Draw wrapped body lines right-aligned with shadow
        by = ty + title_surf.get_height() + 2
        line_spacing = 1
        for idx, s in enumerate(body_surfs):
            bx = sw - right_margin - s.get_width()
            shadow_line = lines[idx]
            body_shadow = body_font.render(shadow_line, True, (0, 0, 0))
            self.screen.blit(body_shadow, (bx + 1, by + 1))
            self.screen.blit(s, (bx, by))
            by += s.get_height() + line_spacing

    def _hud_bar_height(self):
        """Player UI ile aynı üst bar yüksekliğini hesapla."""
        heart_size = int(32 * SCALE)
        token_size = int(20 * SCALE)
        bar_h = max(int(54 * SCALE), heart_size + token_size + int(16 * SCALE))
        return bar_h
    
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

        reset_text = self.font_medium.render("Press B to reset best time", True, UI_TEXT_COLOR)
        reset_rect = reset_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 90))
        self.screen.blit(reset_text, reset_rect)
    
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
        # Süreyi kaydet (en iyi - en hızlı)
        self.level_end_time = pygame.time.get_ticks() / 1000.0
        elapsed = self.level_end_time - self.level_start_time if self.level_start_time else 0.0
        self._update_best_time_if_better(elapsed)
        self.reset_player_progress()
    
    def game_over(self):
        """Game Over"""
        self.state = STATE_GAME_OVER
        print("💀 Game Over!")
        self.level_end_time = pygame.time.get_ticks() / 1000.0
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
        # Timer'i sıfırla (ilk draw frame'inde yeniden başlayacak)
        self.level_start_time = 0.0
        self.level_end_time = 0.0
        # Anahtarı şart sağlanmadıysa gizle
        if hasattr(self, 'collectibles'):
            self.collectibles = [c for c in self.collectibles if c.__class__.__name__ != 'Key']
        self.key_spawned = False
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
        # Level'a göre anahtar gereksinimini yeniden uygula (taşıma senaryolarında garanti et)
        try:
            self.player.require_key = True
            # Level 2+ geçişlerinde (veya genel) anahtarı sıfırla; yeni levelde anahtar toplanmalı
            if self.current_level != 1:
                self.player.has_key = False
        except Exception:
            pass
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
        # Yıldız/anahtar durumu güncellendikten sonra anahtarı gerekirse spawn et
        self._maybe_spawn_key_if_ready()
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

    def _maybe_spawn_key_if_ready(self):
        """Yeterli yıldız toplandıysa anahtarı sahneye ekle."""
        if self.key_spawned:
            return
        if not self.key_spawn_point:
            return
        # Level 1'de anahtar hiç görünmesin
        if self.current_level == 1:
            return
        # Gerekli yıldızlar toplandı mı?
        if hasattr(self.player, 'required_stars') and self.player.stars_collected >= self.player.required_stars:
            x, y, size = self.key_spawn_point
            try:
                from Scripts.Entities.Collectible import Key
                key_obj = Key(x, y, size)
                self.collectibles.append(key_obj)
                self.key_spawned = True
                print("🗝️ Anahtar ortaya çıktı!")
            except Exception as e:
                print(f"⚠️ Anahtar spawn hatası: {e}")


# ============================================
# ENTRY POINT
# ============================================
if __name__ == "__main__":
    print("=== ReVerse - Starting Game ===\n")
    
    game = GameManager()
    game.run()
