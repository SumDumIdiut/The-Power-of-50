# GitHub Setup Guide

## One-Time Setup

### 1. Install Git
Download from https://git-scm.com/download/win

### 2. Configure Git
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 3. Create a GitHub Repository
1. Go to https://github.com/new
2. Name it `the-power-of-50` (or whatever you prefer)
3. Choose Public or Private
4. **Do not** initialise with a README — you already have one
5. Click **Create repository**

### 4. Push the Local Repo
```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

---

## Creating Releases

### Automatic (recommended)

```bash
create_release.bat
```

Prompts for a version number, commits and pushes your changes, creates a version tag, and pushes it. GitHub Actions then builds and publishes the release automatically.

### Manual

```bash
git add .
git commit -m "Your message"
git push origin main

git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

---

## What GitHub Actions Does

When a `v*` tag is pushed, the workflow:

1. Sets up Python 3.12
2. Installs dependencies from `requirements.txt`
3. Runs `build_exe.py` via PyInstaller
4. Creates a GitHub Release and attaches `ThePowerOf50.exe`

Monitor progress under the **Actions** tab of your repository.

---

## Troubleshooting

**"Git is not recognized"** — install Git and restart your terminal.

**"Permission denied"** — make sure you're authenticated. Set up an SSH key or use a Personal Access Token.

**"Build failed"** — check the Actions tab for the full log. Verify `build_exe.py` works locally first.

---

## Version Numbering

Use semantic versioning — `MAJOR.MINOR.PATCH`:

| Increment | When to use              | Example  |
|-----------|--------------------------|----------|
| MAJOR     | Breaking changes         | `v2.0.0` |
| MINOR     | New features             | `v1.1.0` |
| PATCH     | Bug fixes                | `v1.0.1` |

---

## Useful Git Commands

```bash
git status                        # Show working tree state
git log --oneline                 # Compact commit history
git tag                           # List all tags
git tag -d v1.0.0                 # Delete a local tag
git push origin :refs/tags/v1.0.0 # Delete a remote tag
git pull origin main              # Pull latest changes
git checkout -b feature-name      # Create and switch to a new branch
```
