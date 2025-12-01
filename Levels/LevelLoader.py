"""
ReVerse - Level Loader
Unity LevelManager benzeri harita yükleme sistemi
"""
import pygame
from config import GRID_SIZE, STARS_TO_WIN
from Scripts.Utils.Constants import *
from Scripts.Entities.Tile import TileFactory
from Scripts.Entities.Collectible import CollectibleFactory
from Scripts.Core.Player import Player

class LevelLoader:
    """
    Harita verilerini alıp oyun objelerini oluşturur
    Unity Scene Loader benzeri
    """
    
    def __init__(self, grid_size=GRID_SIZE):
        self.grid_size = grid_size
        self.reset()
    
    def reset(self):
        """İç verileri temizle"""
        self.tiles = []
        self.collectibles = []
        self.rotation_symbols = []
        self.player = None
        self.door = None
        self.start_position = None
        self.grid_width = 0
        self.grid_height = 0
    
    def load_level(self, level_data):
        """
        Level verilerini yükle ve objeleri oluştur
        
        Args:
            level_data (dict): LevelData.get_level() tarafından dönen veri
            
        Returns:
            dict: Oluşturulan tüm oyun objeleri
        """
        self.reset()
        
        grid = level_data["grid"]
        self.grid_height = len(grid)
        self.grid_width = len(grid[0]) if grid else 0
        
        print(f"\n{'='*50}")
        print(f"📦 Loading Level: {level_data['name']}")
        print(f"{'='*50}")
        print(f"Grid Size: {self.grid_width}x{self.grid_height}")
        
        # Her hücreyi tara ve obje oluştur
        for row_idx in range(self.grid_height):
            for col_idx in range(self.grid_width):
                symbol = grid[row_idx][col_idx]
                x = col_idx * self.grid_size
                y = row_idx * self.grid_size
                
                # Tile oluştur
                tile = TileFactory.create_tile(symbol, x, y, self.grid_size)
                if tile:
                    self.tiles.append(tile)
                
                # Collectible oluştur
                collectible = CollectibleFactory.create_collectible(symbol, x, y, self.grid_size)
                if collectible:
                    if symbol == TILE_DOOR:
                        # Kapı bir collectible olarak kalır
                        self.door = collectible
                        self.collectibles.append(collectible)
                    elif symbol == TILE_ROTATE:
                        # RotateSymbol collectible değildir; ayrı listede tutulur
                        self.rotation_symbols.append(collectible)
                    else:
                        # Yıldız ve Anahtar gibi toplanabilirler
                        self.collectibles.append(collectible)
                
                # Player başlangıç pozisyonu
                if symbol == TILE_START:
                    self.start_position = (x, y)
                    # NOT: Oyuncu ile aynı hücreye zemin yerleştirmiyoruz ki çarpışma olmasın
                    self.player = Player(x, y, self.grid_size)
                    self.player.required_stars = level_data.get("stars_required", STARS_TO_WIN)
        
        # İstatistikler
        print(f"✅ Tiles: {len(self.tiles)}")
        print(f"✅ Collectibles: {len(self.collectibles)}")
        print(f"✅ Rotation Symbols: {len(self.rotation_symbols)}")
        print(f"✅ Player: {'Yes' if self.player else 'No'}")
        print(f"✅ Door: {'Yes' if self.door else 'No'}")
        print(f"{'='*50}\n")
        
        # Validasyon
        if not self.player:
            raise ValueError("❌ Level must have a Start position (S)!")
        if not self.door:
            raise ValueError("❌ Level must have a Door (D)!")
        
        return self.get_level_objects()
    
    def get_level_objects(self):
        """
        Yüklenmiş tüm objeleri döndür
        
        Returns:
            dict: Tüm oyun objeleri
        """
        return {
            "player": self.player,
            "tiles": self.tiles,
            "collectibles": self.collectibles,
            "door": self.door,
            "rotation_symbols": self.rotation_symbols,
            "start_position": self.start_position,
            "grid_size": (self.grid_width, self.grid_height)
        }
    
    def get_pushable_tiles(self):
        """
        İtici üçgen tile'ları döndür (Rotation için)
        
        Returns:
            list: PushTriangle objeleri
        """
        from Scripts.Entities.Tile import PushTriangle
        return [tile for tile in self.tiles if isinstance(tile, PushTriangle)]
    
    def draw_all(self, screen, camera_offset=(0, 0)):
        """
        Tüm objeleri çiz
        
        Args:
            screen: Pygame surface
            camera_offset: Kamera kayması
        """
        # Tile'ları çiz
        for tile in self.tiles:
            tile.draw(screen, camera_offset)
        
        # Collectible'ları çiz (Door için player bilgisi ver)
        for item in self.collectibles:
            if hasattr(item, 'draw'):
                # Door için player parametresi ekle
                if item.__class__.__name__ == 'Door':
                    item.draw(screen, camera_offset, self.player)
                else:
                    item.draw(screen, camera_offset)

        # Rotation sembollerini çiz
        for sym in self.rotation_symbols:
            if hasattr(sym, 'draw'):
                sym.draw(screen, camera_offset)
        
        # Player'ı çiz
        if self.player:
            self.player.draw(screen, camera_offset)
    
    def update_all(self, dt):
        """
        Tüm objeleri güncelle
        
        Args:
            dt: Delta time
        """
        # Tile'ları güncelle
        for tile in self.tiles:
            tile.update(dt)
        
        # Collectible'ları güncelle (animasyon için)
        for item in self.collectibles:
            if hasattr(item, 'update'):
                item.update(dt)

        # Rotation sembollerini güncelle (animasyon ve durum)
        for sym in self.rotation_symbols:
            if hasattr(sym, 'update'):
                sym.update(dt)
    
    def reset_level(self):
        """Level'i baştan başlat"""
        if self.player and self.start_position:
            self.player.reset(*self.start_position)
        
        # Collectible'ları sıfırla
        for item in self.collectibles:
            if hasattr(item, 'collected'):
                item.collected = False
            if hasattr(item, 'is_open'):
                item.is_open = False
        # Rotate sembollerini sıfırla (tüketim/aktivasyon)
        for sym in self.rotation_symbols:
            if hasattr(sym, 'consumed'):
                sym.consumed = False
            if hasattr(sym, 'activated'):
                sym.activated = False
        
        print("🔄 Level reset!")
    
    def get_level_bounds(self):
        """
        Level sınırlarını döndür (kamera için)
        
        Returns:
            tuple: (width, height) piksel cinsinden
        """
        return (
            self.grid_width * self.grid_size,
            self.grid_height * self.grid_size
        )


# ============================================
# TEST CODE
# ============================================
if __name__ == "__main__":
    from Levels.LevelData import LevelData
    
    print("=== LevelLoader Test ===\n")
    
    # Level 1'i yükle
    level_data = LevelData.get_level(1)
    loader = LevelLoader()
    
    try:
        objects = loader.load_level(level_data)
        
        print(f"\n📊 Loaded Objects:")
        print(f"  Player: {objects['player']}")
        print(f"  Tiles: {len(objects['tiles'])} items")
        print(f"  Collectibles: {len(objects['collectibles'])} items")
        print(f"  Door: {objects['door']}")
        print(f"  Grid: {objects['grid_size']}")
        
        bounds = loader.get_level_bounds()
        print(f"\n📐 Level Bounds: {bounds[0]}x{bounds[1]} pixels")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("\n=== Test Complete ===")
