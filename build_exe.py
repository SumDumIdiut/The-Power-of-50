"""
Build script to compile The Power of 50 into an executable.
"""
import PyInstaller.__main__
import os
import sys

project_dir = os.path.dirname(os.path.abspath(__file__))

args = [
    os.path.join(project_dir, "dev", "menu.py"),
    "--name=ThePowerOf50",
    "--onefile",
    "--windowed",
    "--icon=NONE",
]

data_folders = [
    (os.path.join(project_dir, "Assets"), "Assets"),
    (os.path.join(project_dir, "games"),  "games"),
    (os.path.join(project_dir, "Utils"),  "Utils"),
]

for src, dest in data_folders:
    args.append(f"--add-data={src}{os.pathsep}{dest}")

hidden_imports = [
    "pygame", "pygame.base", "pygame.constants", "pygame.rect", "pygame.rwobject",
    "pygame.surface", "pygame.math", "pygame.mixer", "pygame.font", "pygame.image",
    "pygame.display", "pygame.draw", "pygame.event", "pygame.key", "pygame.mouse",
    "pygame.time", "pygame.transform", "pygame.sprite", "pygame.pkgdata",
    "games.snake", "games.snake.snake_game",
    "games.shooter", "games.shooter.shooter_game", "games.shooter.tilemap",
    "games.shooter.wall_renderer", "games.shooter.helpers",
    "Utils", "Utils.textbox", "Utils.save_manager",
    "math", "random", "sys", "os", "pathlib",
]

for mod in hidden_imports:
    args.append(f"--hidden-import={mod}")

args += [
    "--collect-binaries=pygame",
    "--collect-data=pygame",
    "--optimize=2",
    "--clean",
    "--noconfirm",
    "--distpath=dist",
    "--workpath=build",
    "--specpath=.",
]

print("=" * 60)
print("Building The Power of 50...")
print("=" * 60)

try:
    PyInstaller.__main__.run(args)
    print("\nBuild complete! Check the 'dist' folder for ThePowerOf50.exe")
    sys.exit(0)
except Exception as e:
    print(f"Build failed: {e}")
    sys.exit(1)
