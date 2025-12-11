"""
ReVerse - Splash Scene
Unity benzeri açılış ekranı (Video desteği ile)
"""
import pygame
import os
import math
from config import *

class SplashScene:
    """
    Açılış ekranı yöneticisi
    Video splash veya statik logo gösterir
    """
    
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # Video kontrol
        self.video_available = False
        self.video_player = None
        
        # Video varsa yükle
        if os.path.exists(SPLASH_VIDEO):
            try:
                # pygame.movie modülü yoksa alternatif: opencv veya moviepy
                # Basit çözüm: Video yerine animasyonlu logo
                self.video_available = False
                print("⚠️ Video splash requires additional libraries (opencv-python)")
            except:
                self.video_available = False
    
    def show(self, duration=3.0):
        """
        Splash ekranını göster
        
        Args:
            duration (float): Gösterim süresi (saniye)
        
        Returns:
            bool: True = devam et, False = çıkış
        """
        if self.video_available:
            return self.show_video_splash()
        else:
            return self.show_animated_splash(duration)
    
    def show_video_splash(self):
        """
        Video splash göster (gelecekte eklenecek)
        
        Returns:
            bool: True = devam et
        """
        # TODO: opencv-python ile video oynatma
        # import cv2
        # video = cv2.VideoCapture(SPLASH_VIDEO)
        # ...
        
        print("📹 Video splash not implemented yet")
        return self.show_animated_splash(3.0)
    
    def show_animated_splash(self, duration):
        """
        Animasyonlu logo splash
        
        Args:
            duration (float): Gösterim süresi (saniye)
        
        Returns:
            bool: True = devam et, False = çıkış
        """
        start_time = pygame.time.get_ticks()
        alpha = 0
        # Daha yumuşak geçiş için süreleri biraz uzat ve easing uygula
        fade_in_duration = 1200   # 1.2 saniye
        fade_out_duration = 1200  # 1.2 saniye
        fade_out_start = int(duration * 1000) - fade_out_duration
        
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            current_time = pygame.time.get_ticks() - start_time
            
            # Event kontrolü (skip için)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    return True  # Skip splash
            
            # Süre kontrolü
            if current_time > duration * 1000:
                return True
            
            # Fade in/out hesapla (smooth easing)
            if current_time < fade_in_duration:
                t = max(0.0, min(1.0, current_time / fade_in_duration))
                t_ease = 0.5 - 0.5 * math.cos(math.pi * t)  # smoothstep (cosine ease)
                alpha = int(t_ease * 255)
            elif current_time > fade_out_start:
                t = max(0.0, min(1.0, (current_time - fade_out_start) / fade_out_duration))
                t_ease = 0.5 - 0.5 * math.cos(math.pi * t)
                alpha = int((1 - t_ease) * 255)
            else:
                alpha = 255
            
            # Çizim
            self.draw_splash(alpha)
            pygame.display.flip()
        
        return True
    
    def draw_splash(self, alpha):
        """
        Splash ekranını çiz
        
        Args:
            alpha (int): Transparanlık (0-255)
        """
        # Arka plan (siyaha yakın koyu kahverengi - #1A120B)
        self.screen.fill((26, 18, 11))
        
        # Logo/Başlık
        title_surface = self.font_large.render("ReVerse", True, (255, 255, 255))
        title_surface.set_alpha(alpha)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(title_surface, title_rect)
        
        # Alt başlık
        subtitle_surface = self.font_medium.render("Made with Python & powered by Pygame", True, (255, 255, 255))
        subtitle_surface.set_alpha(alpha)
        subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(subtitle_surface, subtitle_rect)
        
        # Studio adı (opsiyonel)
        studio_surface = self.font_small.render("Mid-term Game Project", True, (255, 255, 255))
        studio_surface.set_alpha(alpha)
        studio_rect = studio_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(studio_surface, studio_rect)
        
        # Unity benzeri koyu görünüm için glow kapatıldı
        # (İstenirse hafif vignette veya düşük yoğunluklu glow tekrar eklenebilir)


class CompanySplash:
    """
    Yapımcı logosu splash (opsiyonel)
    """
    
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 48)
    
    def show(self, company_name="Your Studio", duration=2.0):
        """
        Yapımcı splash göster
        
        Args:
            company_name (str): Studio adı
            duration (float): Gösterim süresi
        
        Returns:
            bool: True = devam et
        """
        start_time = pygame.time.get_ticks()
        
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            current_time = pygame.time.get_ticks() - start_time
            
            # Event kontrolü
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    return True  # Skip
            
            # Süre kontrolü
            if current_time > duration * 1000:
                return True
            
            # Fade in/out
            if current_time < 500:
                alpha = int((current_time / 500) * 255)
            elif current_time > (duration - 0.5) * 1000:
                fade_progress = (current_time - (duration - 0.5) * 1000) / 500
                alpha = int((1 - fade_progress) * 255)
            else:
                alpha = 255
            
            # Çizim
            self.screen.fill((0, 0, 0))
            
            text_surface = self.font.render(company_name, True, (255, 255, 255))
            text_surface.set_alpha(alpha)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(text_surface, text_rect)
            
            pygame.display.flip()
        
        return True


# ============================================
# TEST CODE
# ============================================
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Splash Test")
    
    # Company splash
    company = CompanySplash(screen)
    if not company.show("YourStudio"):
        pygame.quit()
        exit()
    
    # Game splash
    splash = SplashScene(screen)
    if not splash.show():
        pygame.quit()
        exit()
    
    print("✅ Splash scenes completed!")
    pygame.quit()
