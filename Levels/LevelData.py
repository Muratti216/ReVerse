"""
ReVerse - Level Data
Unity Scene benzeri level verileri
"""
from Scripts.Utils.Constants import *

class LevelData:
    """
    Tüm seviyelerin verilerini saklar
    Unity Inspector benzeri yapı
    """
    
    # ============================================
    # LEVEL 1 - Tutorial
    # ============================================
    LEVEL_1 = {
        "name": "Tutorial",
        "description": "Learn the basics of ReVerse",
        "grid": [
            ["K", "R", "X", ".", "X", "*"],  # Row A
            [".", "X", ">", ".", ".", "."],  # Row B
            ["X", ".", "S", "D", "X", "."],  # Row C
            [".", "X", ".", ".", ".", "X"],  # Row D
            ["R", "X", "X", "<", "X", "*"]   # Row E
        ],
        "stars_required": 2,  # Kazanmak için gereken yıldız
        "time_limit": None,   # Zaman sınırı (None = sınırsız)
        "background_color": (20, 20, 30),
        "hint": "Collect stars and avoid black platforms!"
    }
    
    # ============================================
    # LEVEL 2 - Mirror World
    # ============================================
    LEVEL_2 = {
        "name": "Mirror World",
        "description": "Triangles are reversed",
        "grid": [
            ["K", "R", "X", ".", "X", "*"],  # Row A
            [".", "X", "<", ".", ".", "."],  # Row B (Ters yön)
            ["X", ".", "S", "D", "X", "."],  # Row C
            [".", "X", ".", ".", ".", "X"],  # Row D
            ["R", "X", "X", ">", "X", "*"]   # Row E (Ters yön)
        ],
        "stars_required": 2,
        "time_limit": 120,  # 2 dakika
        "background_color": (30, 20, 20),
        "hint": "Watch out for reversed push directions!"
    }
    
    # ============================================
    # STATIC METHODS
    # ============================================
    
    @staticmethod
    def get_level(level_number):
        """
        Level numarasına göre level verisi döndür
        
        Args:
            level_number (int): Level numarası (1, 2, ...)
            
        Returns:
            dict: Level verisi veya None
        """
        levels = {
            1: LevelData.LEVEL_1,
            2: LevelData.LEVEL_2
        }
        return levels.get(level_number, None)
    
    @staticmethod
    def get_total_levels():
        """Toplam level sayısını döndür"""
        return 2
    
    @staticmethod
    def validate_grid(grid):
        """
        Grid'in geçerli olup olmadığını kontrol et
        
        Args:
            grid (list): 2D grid listesi
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not grid or len(grid) == 0:
            return False, "Grid is empty"
        
        # Satır uzunluklarını kontrol et
        row_length = len(grid[0])
        for i, row in enumerate(grid):
            if len(row) != row_length:
                return False, f"Row {i} has inconsistent length"
        
        # Gerekli sembolleri kontrol et
        has_start = False
        has_door = False
        
        for row in grid:
            for cell in row:
                if cell == TILE_START:
                    has_start = True
                elif cell == TILE_DOOR:
                    has_door = True
                elif cell not in LEGEND:
                    return False, f"Unknown tile symbol: {cell}"
        
        if not has_start:
            return False, "Grid must have a Start position (S)"
        if not has_door:
            return False, "Grid must have a Door (D)"
        
        return True, "Grid is valid"
    
    @staticmethod
    def get_grid_size(grid):
        """
        Grid boyutlarını döndür
        
        Args:
            grid (list): 2D grid listesi
            
        Returns:
            tuple: (columns, rows)
        """
        if not grid:
            return 0, 0
        return len(grid[0]), len(grid)
    
    @staticmethod
    def count_collectibles(grid, tile_type):
        """
        Belirli bir toplanabilir objenin sayısını say
        
        Args:
            grid (list): 2D grid listesi
            tile_type (str): Tile tipi (TILE_STAR, TILE_KEY, vs.)
            
        Returns:
            int: Toplanabilir obje sayısı
        """
        count = 0
        for row in grid:
            for cell in row:
                if cell == tile_type:
                    count += 1
        return count
    
    @staticmethod
    def print_level_info(level_number):
        """Level bilgilerini yazdır (Debug için)"""
        level = LevelData.get_level(level_number)
        if not level:
            print(f"❌ Level {level_number} not found!")
            return
        
        grid = level["grid"]
        cols, rows = LevelData.get_grid_size(grid)
        stars = LevelData.count_collectibles(grid, TILE_STAR)
        keys = LevelData.count_collectibles(grid, TILE_KEY)
        
        print(f"\n{'='*50}")
        print(f"📋 LEVEL {level_number}: {level['name']}")
        print(f"{'='*50}")
        print(f"Description: {level['description']}")
        print(f"Grid Size: {cols}x{rows}")
        print(f"Stars: {stars} (Required: {level['stars_required']})")
        print(f"Keys: {keys}")
        print(f"Time Limit: {level['time_limit'] if level['time_limit'] else 'None'}")
        print(f"Hint: {level['hint']}")
        
        # Grid'i yazdır
        print(f"\n📍 Grid Layout:")
        for i, row in enumerate(grid):
            print(f"  Row {chr(65+i)}: {' '.join(row)}")
        
        # Validasyon
        is_valid, msg = LevelData.validate_grid(grid)
        if is_valid:
            print(f"\n✅ {msg}")
        else:
            print(f"\n❌ {msg}")
        print(f"{'='*50}\n")


# ============================================
# TEST CODE
# ============================================
if __name__ == "__main__":
    # Test all levels
    for i in range(1, LevelData.get_total_levels() + 1):
        LevelData.print_level_info(i)
