# ReVerse | Puzzle Platformer

Grid tabanlı, iki level arasında dönen, health/jump hakları ortak tutulan küçük bir bulmaca-aksiyon. Hedef: Yıldızları topla, anahtarı al, kapıya eriş.

## Nasıl oynanır

- Health-jump havuzu ortaktır: 3 ana health × her can için 3 jump hakkı. Jump modundayken her hamlede hak düşer; hak 0 olursa 1 health gider ve haklar tazelenir.
- Tüm engeller 1 health düşürür (siyah blok, itici ok inişi). health kalırsa jump hakların yenilenir; health 0 ise Game Over.
- Yıldızları topla → anahtar spawn olur (Level 1’de anahtar görünmez, Level 2’de çıkar). Kapı sadece yeterli yıldız + anahtar ile açılır.
- Timer üstte: Best / Now. Sağda durum: Stars, Key, hedef (collect / get key / exit).
- Level 1 ve 2 arasında geçişte health ve jump hakları korunur.

## Kontroller

- A / Sol Ok: Sola
- D / Sağ Ok: Sağa
- SPACE: Jump modunu aç/kapat, sonra yön tuşu ile zıpla
- R: Level reset
- N: Debug panel
- TAB: Yardım paneli
- G: God Mode (debug)
- F10: Pencereyi büyüt/küçült
- F11: Tam ekran
- ESC: Çıkış

## Derleme (Windows)

```pwsh
py -m PyInstaller ^
  --name ReVerse ^
  --icon "Assets/Sprites/Avatar.ico" ^
  --add-data "Assets;Assets" ^
  --add-data "Levels;Levels" ^
  --add-data "Scenes;Scenes" ^
  --add-data "Scripts;Scripts" ^
  --add-data "README.md;." ^
  --noconfirm ^
  --onedir ^
  --clean ^
  --distpath "Build" ^
  main.py
```

Çalıştırmak için:

```pwsh
Start-Process "Build\ReVerse\ReVerse.exe"
```

Notlar: `--onedir` tercih edin; `--add-data` Windows’ta `kaynak;hedef`; ikon yoksa `--icon`’ı çıkarabilirsiniz.

## Dosya rehberi

- `main.py`: Giriş, splash/quick mod
- `Scripts/Core/GameManager.py`: Döngü, state, HUD, timer
- `Levels/LevelData.py`, `Levels/LevelLoader.py`: Haritalar
- `Scripts/Entities/Tile.py`: Zeminler (güvenli, zarar, itici ok)
- `Scripts/Entities/Collectible.py`: Yıldız, anahtar, kapı, döndürme
- `Scripts/Systems/ResourceManager.py`: Health + jump hakları (ortak havuz)
- `Scripts/Systems/RotationManager.py`: Dünya/level rotasyonu
- `config.py`: Ayarlar

İyi oyunlar! 🎮
