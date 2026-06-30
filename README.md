# ReVerse | Puzzle Platformer

Grid tabanlı, iki level arasında dönen, health/jump hakları ortak tutulan küçük bir bulmaca-aksiyon. Hedef: Yıldızları topla, anahtarı al, kapıya eriş.

## Nasıl oynanır

- Health-jump havuzu ortaktır: 3 ana health × her can için 3 jump hakkı. Jump modundayken her hamlede hak düşer; hak 0 olursa 1 health gider ve haklar tazelenir.
- Tüm engeller 1 health düşürür (siyah blok). health kalırsa jump hakların yenilenir; health 0 ise Game Over.
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

-----------------------------------------------------------

# ReVerse | Puzzle Platformer

A small grid-based puzzle-action game that cycles between two levels, with shared health and jump attempts. Objective: Collect the stars, grab the key, and reach the door.

## How to play

- Health and jump attempts are shared: 3 main health points × 3 jump attempts per life. In jump mode, one attempt is lost with every move; if attempts reach 0, 1 health point is lost and attempts are refreshed.
- All obstacles cost 1 health point (black block). If health remains, jump attempts are refreshed; if health reaches 0, it’s Game Over.
- Collect stars → a key spawns (the key is invisible in Level 1, but appears in Level 2). The door only opens with enough stars and the key.
- Timer at the top: Best / Now. Status on the right: Stars, Key, objective (collect / get key / exit).
- Health and jump attempts are carried over when switching between Levels 1 and 2.

## Controls

- A / Left Arrow: Left
- D / Right Arrow: Right
- SPACE: Toggle jump mode, then jump using the arrow keys
- R: Reset level
- N: Debug panel
- TAB: Help panel
- G: God Mode (debug)
- F10: Maximise/minimise window
- F11: Full screen
- ESC: Exit

## Building (Windows)

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

To run:

```pwsh
Start-Process "Build\ReVerse\ReVerse.exe"
```

Notes: Use `--onedir`; on Windows, `--add-data` is `source;target`; if there is no icon, you can omit `--icon`.

## File guide

- `main.py`: Introduction, splash/quick mode
- `Scripts/Core/GameManager.py`: Loop, state, HUD, timer
- `Levels/LevelData.py`, `Levels/LevelLoader.py`: Maps
- `Scripts/Entities/Tile.py`: Tiles (safe, damage, push arrow)
- `Scripts/Entities/Collectible.py`: Star, key, door, rotation
- `Scripts/Systems/ResourceManager.py`: Health + jump credits (shared pool)
- `Scripts/Systems/RotationManager.py`: World/level rotation
- `config.py`: Settings

Enjoy the game! 🎮


