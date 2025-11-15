# GitHub Setup Guide

## Initial Setup (One Time)

### 1. Install Git
Download and install Git from: https://git-scm.com/download/win

### 2. Configure Git
Open terminal and run:
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 3. Create GitHub Repository
1. Go to https://github.com/new
2. Repository name: `the-power-of-50` (or your choice)
3. Description: "A collection of three arcade games where the goal is to reach 50"
4. Choose Public or Private
5. **DO NOT** initialize with README (we already have one)
6. Click "Create repository"

### 4. Connect Local Repository to GitHub
```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: The Power of 50 game collection"

# Add remote (replace YOUR_USERNAME and YOUR_REPO)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Creating Releases

### Automatic Method (Recommended)
Simply run the batch file:
```bash
create_release.bat
```

This will:
1. Ask for a version number (e.g., 1.0.0)
2. Commit and push your changes
3. Create and push a version tag
4. Trigger GitHub Actions to build and release

### Manual Method
```bash
# Commit your changes
git add .
git commit -m "Your commit message"
git push origin main

# Create a version tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

## What Happens Automatically

When you push a version tag (like `v1.0.0`), GitHub Actions will:

1. ✅ Set up Python environment
2. ✅ Install dependencies
3. ✅ Build the executable using PyInstaller
4. ✅ Create a GitHub Release
5. ✅ Upload `ThePowerOf50.exe` to the release
6. ✅ Generate release notes

## Monitoring Builds

1. Go to your GitHub repository
2. Click the "Actions" tab
3. You'll see the build progress
4. When complete, check the "Releases" section

## Troubleshooting

### "Git is not recognized"
- Install Git from https://git-scm.com/download/win
- Restart your terminal/IDE after installation

### "Permission denied"
- Make sure you're logged into GitHub
- You may need to set up SSH keys or use a Personal Access Token

### "Build failed"
- Check the Actions tab for error logs
- Ensure `requirements.txt` is up to date
- Verify `build_exe.py` works locally first

## File Organization

The repository is organized to keep things clean:

```
Repository Root/
├── .github/workflows/     # Automated build scripts (committed)
├── Assets/               # Game assets (committed)
├── games/                # Game source code (committed)
├── dev/                  # Development files (committed)
├── Utils/                # Utilities (committed)
├── build_exe.py          # Build script (committed)
├── requirements.txt      # Dependencies (committed)
├── README.md            # Documentation (committed)
├── .gitignore           # Ignore rules (committed)
│
├── build/               # Build artifacts (ignored)
├── dist/                # Compiled exe (ignored)
└── __pycache__/         # Python cache (ignored)
```

**Note:** The `dist/` folder with the .exe is NOT committed to git. Instead, it's automatically built and attached to GitHub Releases.

## Version Numbering

Use semantic versioning: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes (v2.0.0)
- **MINOR**: New features (v1.1.0)
- **PATCH**: Bug fixes (v1.0.1)

Examples:
- `v1.0.0` - Initial release
- `v1.1.0` - Added new game mode
- `v1.1.1` - Fixed bug in shooter game
- `v2.0.0` - Complete rewrite

## Quick Commands Reference

```bash
# Check status
git status

# See commit history
git log --oneline

# See all tags
git tag

# Delete a tag (if you made a mistake)
git tag -d v1.0.0
git push origin :refs/tags/v1.0.0

# Pull latest changes
git pull origin main

# Create a new branch
git checkout -b feature-name
```
