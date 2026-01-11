# Upload Scam Report Builder v1.4 to GitHub - Cursor Guide

This guide walks you through uploading v1.4 to GitHub using Cursor's built-in Git integration.

---

## Prerequisites

✅ Cursor is linked to GitHub (dubloox3/scam-report-builder)  
✅ EXE built successfully in `dist/` folder  
✅ Source code cleaned and ready  
✅ `.gitignore` properly configured (dist/ and build/ excluded)

---

## Step 1: Verify What Will Be Committed

### Using Cursor's Source Control Panel:

1. **Open Source Control:**
   - Click the **Source Control** icon in the left sidebar (looks like a branch/fork icon)
   - Or press `Ctrl+Shift+G` (Windows) / `Cmd+Shift+G` (Mac)

2. **Review Changes:**
   - You'll see two sections:
     - **Changes** (modified files)
     - **Untracked** (new files)

3. **Verify dist/ is NOT listed:**
   - `dist/` folder should NOT appear in the source control panel
   - If it does appear, check `.gitignore` includes `dist/`

### Expected Files to Commit:

**Modified Files:**
- `.gitignore`
- `README.md`
- `core/config_manager.py`
- `core/odt_generator.py`
- `main.py`
- `ui/main_window.py`
- `ui/widgets/image_list_widget.py`
- `ui/widgets/other_payment_widget.py`

**New Files (Untracked):**
- `BUILD_INSTRUCTIONS.md`
- `GITHUB_RELEASE_SUMMARY.md`
- `RELEASE_GUIDE.md`
- `Scam-Report-Builder.spec`
- `build_exe.py`
- `verify_release_ready.py`

**Should NOT appear:**
- ❌ `dist/` folder
- ❌ `build/` folder
- ❌ `__pycache__/` folders

---

## Step 2: Stage Files in Cursor

### Method 1: Stage All Files (Recommended)

1. **In Source Control Panel:**
   - Click the **`+`** icon next to "Changes" to stage all modified files
   - Click the **`+`** icon next to "Untracked" to stage all new files
   - Or click the **`+`** icon at the top (next to "SOURCE CONTROL") to stage everything

2. **Verify:**
   - Files should move to "Staged Changes" section
   - All source files should be staged
   - `dist/` and `build/` should NOT be staged

### Method 2: Stage Individual Files

1. **Hover over each file** in the Changes/Untracked sections
2. Click the **`+`** icon that appears next to each file
3. Files move to "Staged Changes"

### What Cursor Does Behind the Scenes:

When you click the `+` buttons, Cursor runs:
```bash
git add <file>
# or
git add .
```

**Important:** Cursor respects `.gitignore`, so `dist/` and `build/` won't be added even if you stage all files.

---

## Step 3: Commit Changes

1. **In Source Control Panel:**
   - Look for the message box at the top (says "Message" or "Type commit message...")
   - Enter commit message:
     ```
     Release v1.4: Enhanced report modification, improved image handling, and UI improvements
     ```

2. **Commit:**
   - Press `Ctrl+Enter` (Windows) / `Cmd+Enter` (Mac)
   - Or click the **checkmark** icon (✓) at the top of the Source Control panel

### What Cursor Does:

```bash
git commit -m "Release v1.4: Enhanced report modification, improved image handling, and UI improvements"
```

---

## Step 4: Push to GitHub

### Using Cursor's Interface:

1. **After committing:**
   - Look for a notification or indicator showing commits ahead of origin
   - You'll see something like "↑ 1" (1 commit ahead)

2. **Push:**
   - Click the **three dots** (`...`) menu at the top of Source Control panel
   - Select **"Push"** from the dropdown
   - Or use the keyboard shortcut shown in the menu

3. **Alternative - Command Palette:**
   - Press `Ctrl+Shift+P` (Windows) / `Cmd+Shift+P` (Mac)
   - Type "Git: Push"
   - Select it and press Enter

### What Cursor Does:

```bash
git push origin main
```

### Verify Push:

1. **Check Status:**
   - After pushing, the "↑ 1" indicator should disappear
   - Source Control panel should show "Your branch is up to date with 'origin/main'"

2. **Verify on GitHub:**
   - Go to: https://github.com/dubloox3/scam-report-builder
   - Check that your latest commit appears
   - Verify `dist/` folder is NOT in the repository

---

## Step 5: Create GitHub Release v1.4

### Option A: Using GitHub Website (Recommended)

1. **Navigate to Releases:**
   - Go to: https://github.com/dubloox3/scam-report-builder/releases
   - Click **"Draft a new release"** button

2. **Create Release:**
   - **Choose a tag:** Click "Choose a tag" → Type `v1.4` → Click "Create new tag: v1.4 on publish"
   - **Release title:** `Scam Report Builder v1.4`
   - **Description:** Copy and paste the changelog below

3. **Attach EXE:**
   - Scroll down to **"Attach binaries by dropping them here or selecting them"**
   - Drag and drop `dist/Scam-Report-Builder.exe` from your file explorer
   - Wait for upload to complete (file is ~242 MB, may take a few minutes)

4. **Publish:**
   - Click **"Publish release"** button
   - Done! Users can now download the EXE

### Option B: Using GitHub CLI (if installed)

```bash
# Create release
gh release create v1.4 \
  --title "Scam Report Builder v1.4" \
  --notes-file CHANGELOG_v1.4.md \
  dist/Scam-Report-Builder.exe
```

---

## Release Description (Changelog) for v1.4

Copy this into the GitHub Release description:

```markdown
## Scam Report Builder v1.4

### 🎉 What's New

- **Enhanced Report Modification:** Modify existing reports while preserving report numbers
- **Improved Image Handling:** 
  - Remembers last selected folder for faster batch processing
  - Better image cropping and rotation
  - Fixed label readability in Evidence tab (white text on dark background)
- **Better User Experience:**
  - Disabled mouse wheel on payment method dropdowns (prevents accidental changes)
  - Correct report folder pre-selection in save dialogs
  - Improved report numbering logic (new vs. modify reports)
- **Code Quality:**
  - Removed all debug code
  - Optimized error handling
  - Clean, production-ready codebase

### 📥 Installation

1. Download `Scam-Report-Builder.exe` from the assets below
2. Double-click to run (no installation needed)
3. On first run, Windows may show a security warning:
   - Click "More info"
   - Click "Run anyway"
   - This is normal for unsigned executables

### 🖥️ System Requirements

- Windows 10/11
- No Python installation needed
- ~500 MB free disk space

### 📝 Usage

1. **First Run:** Choose where to save reports (folder is remembered)
2. **Select Template:** Choose report type
3. **Fill in Tabs:** Enter scammer details, payment info, evidence, remarks
4. **Create Report:** Click "Create Scam Report", set number, save
5. **Modify or New:** After creation, choose to modify existing report or create new one

### 🔧 For Developers

To build from source:
```bash
pip install -r requirements.txt
pip install pyinstaller
python build_exe.py
```

See `BUILD_INSTRUCTIONS.md` for details.

### 📄 Full Changelog

- Fixed report numbering when modifying existing reports
- Fixed report numbering for new reports after previous ones
- Relocated JSON data files to `.report_data` folder (keeps Reports folder clean)
- Fixed unreadable labels in Evidence tab
- Added "New Report" and "Modify Report" options after report creation
- Improved folder persistence for image selection
- Disabled mouse wheel on dropdown menus
- Cleaned up all debug code and test files
- Optimized for EXE distribution
```

---

## Step 6: Verify Everything

### Check Repository:

1. **Source Code:**
   - Visit: https://github.com/dubloox3/scam-report-builder
   - Verify all source files are present
   - Verify `dist/` folder is NOT in repository

2. **Release:**
   - Visit: https://github.com/dubloox3/scam-report-builder/releases
   - Verify v1.4 release exists
   - Verify EXE is attached and downloadable

3. **Test Download:**
   - Click "Download" on the EXE asset
   - Verify file downloads correctly
   - File should be ~242 MB

---

## Troubleshooting

### Issue: dist/ folder appears in Source Control

**Solution:**
1. Check `.gitignore` includes `dist/`
2. If `dist/` was previously committed, remove it:
   ```bash
   git rm -r --cached dist/
   git commit -m "Remove dist folder from repository"
   ```

### Issue: Can't push to GitHub

**Possible causes:**
1. **Authentication:** Cursor may prompt for GitHub credentials
2. **Branch protection:** Check if main branch has protection rules
3. **Network:** Check internet connection

**Solution:**
- Use Cursor's authentication prompt if it appears
- Or configure Git credentials manually

### Issue: EXE upload fails

**Solution:**
- GitHub has a 100 MB file size limit for browser uploads
- For files > 100 MB, use GitHub CLI:
  ```bash
  gh release upload v1.4 dist/Scam-Report-Builder.exe
  ```
- Or use Git LFS (Large File Storage) if needed

---

## Quick Reference: Cursor Git Commands

### What Cursor Does Behind the Scenes:

| Action in Cursor | Git Command |
|-----------------|-------------|
| Click `+` to stage | `git add <file>` |
| Stage all | `git add .` |
| Commit | `git commit -m "message"` |
| Push | `git push origin main` |
| Pull | `git pull origin main` |
| Status | `git status` |

### Keyboard Shortcuts:

- `Ctrl+Shift+G` / `Cmd+Shift+G` - Open Source Control
- `Ctrl+Enter` / `Cmd+Enter` - Commit staged changes
- `Ctrl+Shift+P` / `Cmd+Shift+P` - Command Palette (for Git commands)

---

## Summary Checklist

Before uploading, verify:

- [ ] All source files staged (not dist/ or build/)
- [ ] Commit message: "Release v1.4: [description]"
- [ ] Pushed to GitHub successfully
- [ ] Verified dist/ is NOT in repository
- [ ] Created GitHub Release v1.4
- [ ] Uploaded EXE to release assets
- [ ] Tested EXE download from GitHub

---

**You're all set! 🚀**

Your v1.4 release is now live on GitHub. Users can download the EXE from the Releases page.
