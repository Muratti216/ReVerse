# ReVerse | Puzzle Platformer

ReVerse, Python + Pygame ile geliştirilmiş, 3x3 can sistemi ve harita dönüş mekanikleriyle öne çıkan, grid tabanlı bir bulmaca/aksiyon platform oyunudur.

## Özellikler

- Grid tabanlı hareket ve kare harita yapısı
- 3x3 can sistemi (3 ana can × her can için 3 zıplama hakkı)
- Zararlı (siyah çizgili) zeminlerde zıplama hakları tüketimi
- Tek-seferlik döndürme sembolleri ve çift dünya/katman rotasyonu
- Yıldız (puan) ve Anahtar (kapı açma) toplanabilir öğeleri
- Kapı (çıkış) mekaniği: Anahtar ve yeterli yıldız olmadan açılmaz
- İtici Ok (PushTriangle) zeminleri: Oyuncuyu belirli yöne iter ve inişte ok ucunun önüne hizalar
- Üstte bağımsız HUD (canlar ve zıplama hakları), harita HUD’ın altında render edilir
- Sağ tarafta Debug Panel (N ile aç/kapat)
  - Seviye, oyuncu konumu, yıldız/anahtar durumu
  - Canlar, zıplama tokenları, rotasyon bekleme süresi
  - Tile/Collectible/Rotate sayıları, FPS
  - God Mode: ON/OFF durumu
- Sağ tarafta Yardım Paneli (TAB ile aç/kapat) – kontrol rehberi
- Pencere özellikleri: yeniden boyutlandırılabilir, F10 ile maximize, F11 ile fullscreen
- Win ekranında ipucu: "Press R to try a new strategy"

## Kontroller

- `A` / `Sol Ok`: Sola hareket
- `D` / `Sağ Ok`: Sağa hareket
- `SPACE`: Zıplama
- `R`: Seviyeyi yeniden başlat
- `N`: Debug panelini aç/kapat
- `TAB`: Yardım panelini aç/kapat
- `G`: God Mode aç/kapat (debug)
- `F10`: Pencereyi büyüt/küçült (maximize)
- `F11`: Tam ekran
- `ESC`: Çıkış

## God Mode

- Açıkken zararlı zeminlere inişlerde hasar alınmaz.
- Debug panelinde "GodMode: ON/OFF" olarak görünür.

## Build Alma (Windows)

PyInstaller ile tek klasör çıkışı alınır. İkon opsiyoneldir.

Bağımlılık yüklemeyi atlamak isterseniz doğrudan PyInstaller komutunu çalıştırın.

 
 
```pwsh
py -m PyInstaller \
  --name ReVerse \
  --icon "Assets/Sprites/Avatar.ico" \
  --add-data "Assets;Assets" \
  --add-data "Levels;Levels" \
  --add-data "Scenes;Scenes" \
  --add-data "Scripts;Scripts" \
  --add-data "README.md;." \
  --noconfirm \
  --onedir \
  --clean \
  --distpath "Build" \
  main.py
```

Çıktıyı çalıştırmak için:

```pwsh
Start-Process "Build\ReVerse\ReVerse.exe"
```

> Notlar:
>
> - `--onedir` önerilir (asset ve Pygame DLL uyumluluğu için).
> - `--add-data` Windows’ta `kaynak;hedef` biçimindedir.
> - İkon dosyanız yoksa `--icon` bayrağını kaldırabilirsiniz.

## Mimari

- `main.py`: Giriş noktası (splash, normal ve quick start)
- `Scripts/Core/GameManager.py`: Ana döngü, input, sahne ve overlay yönetimi
- `Levels/LevelData.py` ve `Levels/LevelLoader.py`: Harita veri ve yükleme
- `Scripts/Entities/Tile.py`: Zemin tipleri (Güvenli, Zararlı, İtici Ok)
- `Scripts/Entities/Collectible.py`: Yıldız, Anahtar, Kapı, Döndürme sembolü
- `Scripts/Systems/ResourceManager.py`: 3x3 can sistemi, zıplama tokenları
- `Scripts/Systems/RotationManager.py`: Harita/dünya rotasyonu
- `config.py`: Ekran, ölçek, HUD yüksekliği (`HUD_HEIGHT`), GOD_MODE ve renkler

## Bilinen Davranışlar

- Döndürme sembolleri tek kullanımlıktır ve katman/dünya değiştirir.
- İtici Ok zeminleri inişte oyuncuyu okun ucunun önündeki güvenli kareye hizalar.
- Kapılar yalnızca anahtar ve yeterli yıldız ile açılır.

İyi oyunlar! 🎮
