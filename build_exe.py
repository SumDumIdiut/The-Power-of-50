"""
Build script to compile The Power of 50 into an executable
Bundles assets, utils, and custom beatmaps only
"""
import PyInstaller.__main__
import os
import sys

project_dir = os.path.dirname(os.path.abspath(__file__))

# Folders to include
assets_folder = os.path.join(project_dir, "Assets")
games_folder = os.path.join(project_dir, "games")
utils_folder = os.path.join(project_dir, "Utils")
custom_beatmaps_folder = os.path.join(games_folder, "rhythm", "beatmaps")  # Only custom maps

# PyInstaller arguments
args = [
    os.path.join(project_dir, "dev", "menu.py"),
    "--name=ThePowerOf50",
    "--onefile",
    "--windowed",
    "--icon=NONE",
]

# Add data folders
data_folders = [
    (assets_folder, "Assets"),
    (games_folder, "games"),
    (utils_folder, "Utils"),
]

# Add only custom beatmaps
if os.path.exists(custom_beatmaps_folder):
    data_folders.append((custom_beatmaps_folder, "beatmaps"))
    print(f"Including custom beatmaps from: {custom_beatmaps_folder}")

for src, dest in data_folders:
    args.append(f"--add-data={src}{os.pathsep}{dest}")

# Hidden imports for pygame and game modules
hidden_imports = [
    "pygame", "pygame.base", "pygame.constants", "pygame.rect", "pygame.rwobject",
    "pygame.surface", "pygame.math", "pygame.mixer", "pygame.font", "pygame.image",
    "pygame.display", "pygame.draw", "pygame.event", "pygame.key", "pygame.mouse",
    "pygame.time", "pygame.transform", "pygame.sprite", "pygame.pkgdata",
    "games.snake", "games.snake.snake_game",
    "games.shooter", "games.shooter.shooter_game", "games.shooter.tilemap",
    "games.shooter.wall_renderer", "games.shooter.helpers",
    "games.tower_defense", "games.tower_defense.tower_defense_game",
    "Utils", "Utils.portal", "Utils.textbox",
    "math", "random", "sys", "os", "pathlib"
]

for mod in hidden_imports:
    args.append(f"--hidden-import={mod}")

# Collect binaries and data for pygame
args += [
    "--collect-binaries=pygame",
    "--collect-data=pygame",
    "--optimize=2",
    "--clean",
    "--noconfirm",
    "--distpath=dist",
    "--workpath=build",
    "--specpath=."
]

# Build
print("="*60)
print("Building The Power of 50 Executable with Custom Beatmaps Only...")
print("="*60)

try:
    PyInstaller.__main__.run(args)
    print("\nBuild complete! Check the 'dist' folder for ThePowerOf50.exe")
    sys.exit(0)
except Exception as e:
    print(f"Build failed: {e}")
    sys.exit(1)
