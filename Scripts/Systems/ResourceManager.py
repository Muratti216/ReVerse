"""
ReVerse - Resource Manager
3x3 Can Kuralı Sistemi (Unity Component benzeri)
"""
import config

class ResourceManager:
    """
    Oyuncunun can ve zıplama haklarını yönetir
    Unity MonoBehaviour benzeri yapı
    """
    
    def __init__(self):
        self.main_lives = config.MAX_MAIN_LIVES      # 3 ana can
        self.jump_tokens = config.JUMPS_PER_LIFE     # 3 zıplama hakkı
        self.total_jumps_used = 0             # Toplam kullanılan zıplama

    def take_hit(self, reason="Obstacle"):
        """Her engel temasında 1 can götür; can kalırsa jump tokenları yenile."""
        if config.GOD_MODE:
            print(f"🛡️ GOD MODE: Hit ignored ({reason})")
            return True

        self.main_lives -= 1
        print(f"💔 Hit: -1 life (reason: {reason}) → Lives: {self.main_lives}")

        if self.main_lives > 0:
            # Her can kaybında zıplama haklarını tazele
            self.jump_tokens = config.JUMPS_PER_LIFE
            print(f"🔄 Jump tokens refilled: {self.jump_tokens}")
            return True
        else:
            print("☠️ GAME OVER - No lives left!")
            return False
        
    def use_jump(self):
        """
        Siyah platformdan zıplandığında çağrılır
        3x3 kuralını uygular
        
        Returns:
            bool: True = oyun devam, False = Game Over
        """
        if config.GOD_MODE:
            print("🛡️ GOD MODE: Jump ignored")
            return True
        
        # Jump token kullan
        self.jump_tokens -= 1
        self.total_jumps_used += 1
        
        print(f"⚡ Jump used! Tokens left: {self.jump_tokens}")
        
        # Token bitti mi?
        if self.jump_tokens <= 0:
            # Ana can azalt
            self.main_lives -= 1
            print(f"💔 Main life lost! Lives: {self.main_lives}")
            
            if self.main_lives > 0:
                # Tokenları yenile
                self.jump_tokens = config.JUMPS_PER_LIFE
                print(f"🔄 Jump tokens refilled: {self.jump_tokens}")
            else:
                # Game Over
                print("☠️ GAME OVER - No lives left!")
                return False
        
        return True
    
    def is_game_over(self):
        """
        Oyun bitti mi kontrol et
        
        Returns:
            bool: True = Game Over
        """
        return self.main_lives <= 0 and not config.GOD_MODE
    
    def has_lives(self):
        """
        Can var mı kontrol et
        
        Returns:
            bool: True = Can var
        """
        return self.main_lives > 0 or config.GOD_MODE
    
    def get_lives_info(self):
        """
        Can bilgilerini döndür (UI için)
        
        Returns:
            dict: Can bilgileri
        """
        return {
            "main_lives": self.main_lives,
            "jump_tokens": self.jump_tokens,
            "total_jumps": self.total_jumps_used,
            "god_mode": config.GOD_MODE
        }
    
    def reset(self):
        """Canları başlangıç değerlerine döndür"""
        self.main_lives = config.MAX_MAIN_LIVES
        self.jump_tokens = config.JUMPS_PER_LIFE
        self.total_jumps_used = 0
        print("🔄 Resources reset!")
    
    def add_life(self):
        """Bonus can ekle (ileride powerup için)"""
        if self.main_lives < config.MAX_MAIN_LIVES:
            self.main_lives += 1
            print(f"❤️ Life restored! Lives: {self.main_lives}")
    
    def __str__(self):
        """String representation (Debug için)"""
        return f"Lives: {self.main_lives} | Tokens: {self.jump_tokens}"


# ============================================
# TEST CODE
# ============================================
if __name__ == "__main__":
    print("=== ResourceManager Test ===\n")
    
    rm = ResourceManager()
    print(f"Initial: {rm}\n")
    
    # 9 zıplama simülasyonu (3x3)
    for i in range(1, 10):
        print(f"\n--- Jump #{i} ---")
        can_continue = rm.use_jump()
        print(f"Status: {rm}")
        
        if not can_continue:
            print("\n❌ Game Over!")
            break
    
    print("\n=== Test Complete ===")
