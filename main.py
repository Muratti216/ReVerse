"""
╔═══════════════════════════════════════════════════════════╗
║                        ReVerse                            ║
║                  Puzzle Platformer                        ║
║                                                           ║
║  A grid-based puzzle game with unique 3x3 life system     ║
║  Made with Python & Pygame                                ║
╚═══════════════════════════════════════════════════════════╝

Main Entry Point - Unity benzeri oyun başlatıcı
"""
import pygame
import sys
import os

# Proje kök dizinini Python path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Çalışma dizinini exe'nin bulunduğu klasöre ayarla (PyInstaller uyumu)
try:
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)
except Exception:
    pass

from config import *
from Scenes.SplashScene import SplashScene, CompanySplash
from Scripts.Core.GameManager import GameManager


def show_splash_screens():
    """
    Açılış ekranlarını göster
    
    Returns:
        bool: True = devam et, False = çıkış
    """
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("ReVerse - Loading...")
    
    # Company splash (opsiyonel - yorumdan çıkar)
    # company = CompanySplash(screen)
    # if not company.show("Your Studio Name"):
    #     return False
    
    # Game splash
    splash = SplashScene(screen)
    if not splash.show(duration=3.0):
        return False
    
    return True


def main():
    """
    Ana oyun başlatıcı
    Unity'deki Build benzeri entry point
    """
    print("\n" + "="*60)
    print("  ____     __     __                   ")
    print(" |  _ \\   / /    / /                  ")
    print(" | |_) | / /    / /                     ")
    print(" |  _ < / /    / /                      ")
    print(" | |_) / /    / /                       ")
    print(" |____/_/    /_/  erse                  ")
    print("="*60)
    print(" Puzzle Platformer | Python + Pygame")
    print("="*60 + "\n")
    
    # Splash screens göster
    if not show_splash_screens():
        print("👋 Exiting game...")
        sys.exit(0)
    
    # Ana oyunu başlat
    try:
        print("🎮 Starting Game Manager...")
        game = GameManager()
        
        print("\n" + "="*60)
        print(" CONTROLS:")
        print("="*60)
        print(" A/LEFT  - Move Left")
        print(" D/RIGHT - Move Right")
        print(" SPACE   - Jump")
        print(" R       - Restart Level")
        print(" N       - Next Level (debug)")
        print(" G       - Toggle God Mode (debug)")
        print(" ESC     - Quit")
        print("="*60 + "\n")
        
        print("✅ Game loaded successfully!")
        print("🎮 Starting main game loop...\n")
        
        # Oyun döngüsü
        game.run()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Game interrupted by user (Ctrl+C)")
    
    except Exception as e:
        print(f"\n\n❌ Critical Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n👋 Thanks for playing ReVerse!")
        print("="*60 + "\n")
        pygame.quit()
        sys.exit(0)


def quick_start():
    """
    Hızlı başlangıç (splash olmadan)
    Debug için kullanılır
    """
    print("\n🚀 Quick Start Mode (No Splash)\n")
    
    try:
        game = GameManager()
        game.run()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
        sys.exit(0)


def test_systems():
    """
    Sistemleri test et (Debug)
    """
    print("\n🧪 Testing Game Systems...\n")
    
    # ResourceManager testi
    print("1️⃣ Testing ResourceManager...")
    from Scripts.Systems.ResourceManager import ResourceManager
    rm = ResourceManager()
    print(f"   Initial: {rm}")
    for i in range(3):
        rm.use_jump()
        print(f"   After jump {i+1}: {rm}")
    print("   ✅ ResourceManager OK\n")
    
    # LevelData testi
    print("2️⃣ Testing LevelData...")
    from Levels.LevelData import LevelData
    level = LevelData.get_level(1)
    if level is None:
        print("   ❌ LevelData ERROR: Level 1 not found!\n")
    else:
        print(f"   Level name: {level['name']}")
        print(f"   Grid size: {len(level['grid'][0])}x{len(level['grid'])}")
        print("   ✅ LevelData OK\n")
    
    # LevelLoader testi
    print("3️⃣ Testing LevelLoader...")
    from Levels.LevelLoader import LevelLoader
    loader = LevelLoader()
    objects = loader.load_level(level)
    print(f"   Loaded {len(objects['tiles'])} tiles")
    print(f"   Loaded {len(objects['collectibles'])} collectibles")
    print("   ✅ LevelLoader OK\n")
    
    print("✅ All systems tested successfully!\n")


# ============================================
# ENTRY POINTS
# ============================================

if __name__ == "__main__":
    import sys
    
    # Komut satırı argümanları
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "test":
            # Test modu
            test_systems()
        
        elif command == "quick":
            # Splash olmadan başlat
            quick_start()
        
        elif command == "help":
            # Yardım
            print("\nReVerse - Command Line Options:")
            print("  python main.py        - Normal oyun başlatma (splash ile)")
            print("  python main.py quick  - Hızlı başlatma (splash olmadan)")
            print("  python main.py test   - Sistem testleri")
            print("  python main.py help   - Bu yardım menüsü")
            print()
        
        else:
            print(f"❌ Unknown command: {command}")
            print("   Use 'python main.py help' for options")
    
    else:
        # Normal başlangıç
        main()
