# Quick Upload Steps - Cursor to GitHub v1.4

## ⚡ Fast Track (5 Minutes)

### Step 1: Open Source Control in Cursor
- Press `Ctrl+Shift+G` (or click Source Control icon in left sidebar)

### Step 2: Stage All Files
- Click the **`+`** icon at the top (next to "SOURCE CONTROL")
- This stages all modified and new files
- ✅ Verify: `dist/` and `build/` should NOT appear in staged files

### Step 3: Commit
- Type commit message in the box:
  ```
  Release v1.4: Enhanced report modification, improved image handling, and UI improvements
  ```
- Press `Ctrl+Enter` to commit

### Step 4: Push to GitHub
- Click the **three dots** (`...`) menu at top of Source Control
- Select **"Push"**
- Or press `Ctrl+Shift+P` → type "Git: Push" → Enter

### Step 5: Create GitHub Release
1. Go to: https://github.com/dubloox3/scam-report-builder/releases/new
2. Tag: `v1.4`
3. Title: `Scam Report Builder v1.4`
4. Description: Copy from `CURSOR_GITHUB_UPLOAD_GUIDE.md` (Release Description section)
5. Upload: Drag `dist/Scam-Report-Builder.exe` to "Attach binaries"
6. Click "Publish release"

---

## 🔍 What Cursor Does (Behind the Scenes)

When you click buttons in Cursor, it runs these Git commands:

```bash
# Stage files (when you click +)
git add .
# Note: .gitignore prevents dist/ and build/ from being added

# Commit (when you press Ctrl+Enter)
git commit -m "Release v1.4: Enhanced report modification, improved image handling, and UI improvements"

# Push (when you click Push)
git push origin main
```

---

## ✅ Verification Checklist

After pushing, verify:

1. **In Cursor:**
   - Source Control shows "Your branch is up to date with 'origin/main'"
   - No "↑" indicator (no commits ahead)

2. **On GitHub:**
   - Visit: https://github.com/dubloox3/scam-report-builder
   - Latest commit shows your commit message
   - `dist/` folder is NOT visible in repository

3. **Release:**
   - Visit: https://github.com/dubloox3/scam-report-builder/releases
   - v1.4 release exists
   - EXE is downloadable

---

## 🚨 Important Notes

- **EXE is NOT committed** - It's only uploaded to GitHub Releases
- **dist/ folder is ignored** - `.gitignore` prevents it from being committed
- **File size:** EXE is ~242 MB - upload may take a few minutes
- **Windows Security:** Users will see "Unknown publisher" warning (normal for unsigned executables)

---

## 📚 Full Guide

For detailed instructions, see: `CURSOR_GITHUB_UPLOAD_GUIDE.md`
