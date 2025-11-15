"""
Build script to compile The Power of 50 into an executable
Bundles all packages and dependencies into a single .exe file
"""
import PyInstaller.__main__
import os
import sys

# Force ASCII output to avoid encoding errors in CI
os.environ['PYTHONIOENCODING'] = 'ascii'

# Get the absolute path to the project directory
project_dir = os.path.dirname(os.path.abspath(__file__))

# PyInstaller arguments
args = [
    'dev/menu.py',  # Main entry point
    '--name=ThePowerOf50',  # Name of the executable
    '--onefile',  # Create a single executable file
    '--windowed',  # No console window (GUI only)
    '--icon=NONE',  # No icon (you can add one later)
    
    # Add data files (assets, etc.)
    f'--add-data=Assets{os.pathsep}Assets',
    f'--add-data=games{os.pathsep}games',
    f'--add-data=Utils{os.pathsep}Utils',
    
    # Collect all submodules and packages
    '--collect-all=pygame',  # Bundle entire pygame package
    '--collect-submodules=pygame',
    '--copy-metadata=pygame',
    
    # Hidden imports (modules that PyInstaller might miss)
    '--hidden-import=pygame',
    '--hidden-import=pygame.base',
    '--hidden-import=pygame.constants',
    '--hidden-import=pygame.rect',
    '--hidden-import=pygame.rwobject',
    '--hidden-import=pygame.surface',
    '--hidden-import=pygame.math',
    '--hidden-import=pygame.mixer',
    '--hidden-import=pygame.font',
    '--hidden-import=pygame.image',
    '--hidden-import=pygame.display',
    '--hidden-import=pygame.draw',
    '--hidden-import=pygame.event',
    '--hidden-import=pygame.key',
    '--hidden-import=pygame.mouse',
    '--hidden-import=pygame.time',
    '--hidden-import=pygame.transform',
    '--hidden-import=pygame.sprite',
    '--hidden-import=pygame.pkgdata',
    
    # Game modules
    '--hidden-import=games',
    '--hidden-import=games.snake',
    '--hidden-import=games.snake.snake_game',
    '--hidden-import=games.shooter',
    '--hidden-import=games.shooter.shooter_game',
    '--hidden-import=games.shooter.tilemap',
    '--hidden-import=games.shooter.wall_renderer',
    '--hidden-import=games.shooter.helpers',
    '--hidden-import=games.tower_defense',
    '--hidden-import=games.tower_defense.tower_defense_game',
    
    # Utils modules
    '--hidden-import=Utils',
    '--hidden-import=Utils.portal',
    '--hidden-import=Utils.textbox',
    
    # Python standard library modules that might be needed
    '--hidden-import=math',
    '--hidden-import=random',
    '--hidden-import=sys',
    '--hidden-import=os',
    '--hidden-import=pathlib',
    
    # Bundle binary dependencies
    '--collect-binaries=pygame',
    '--collect-data=pygame',
    
    # Optimization
    '--optimize=2',  # Optimize Python bytecode
    
    # Clean build
    '--clean',
    '--noconfirm',  # Don't ask for confirmation to overwrite
    
    # Output directory
    '--distpath=dist',
    '--workpath=build',
    '--specpath=.',
]

print("="*60)
print("Building The Power of 50 Executable")
print("="*60)
print("Starting build process...")
print("="*60)

# Run PyInstaller
try:
    PyInstaller.__main__.run(args)
    sys.exit(0)  # Exit immediately on success
except Exception as e:
    # Silent failure - just exit with error code
    sys.exit(1)
