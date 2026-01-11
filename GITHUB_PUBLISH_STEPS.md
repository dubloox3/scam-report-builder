# GitHub Publishing Steps for Scam Report Builder v1.4

## Quick Summary

You need to do 3 things:
1. **Commit and push source code** (EXE is automatically excluded via .gitignore)
2. **Create GitHub Release** (tag: v1.4)
3. **Upload EXE** as release asset

---

## Step-by-Step Instructions

### Part 1: Commit and Push Source Code

#### Option A: Using Cursor's Source Control Panel (Easiest)

1. **Open Source Control in Cursor:**
   - Click the Source Control icon in the left sidebar (looks like a branch icon)
   - Or press `Ctrl+Shift+G`

2. **Review Changes:**
   - You should see all your modified files listed
   - Files in `dist/` and `build/` will NOT appear (they're excluded by .gitignore)

3. **Stage All Files:**
   - Click the `+` icon next to "Changes" to stage all files
   - Or right-click and select "Stage All Changes"

4. **Write Commit Message:**
   - In the message box at the top, enter:
     ```
     Release v1.4: Custom templates, new fields (Social Media, Other info), bug fixes
     ```

5. **Commit:**
   - Click the checkmark icon (✓) or press `Ctrl+Enter`
   - Or click "Commit" button

6. **Push to GitHub:**
   - Click the "..." menu (three dots) at the top of the Source Control panel
   - Select "Push"
   - Or click the up arrow icon if visible
   - Or use command: `Ctrl+Shift+P` → type "Git: Push" → Enter

#### Option B: Using Command Line

Open a terminal in Cursor (`Ctrl+` ` or Terminal menu):

```bash
# Stage all files (dist/ and build/ automatically excluded)
git add .

# Commit with message
git commit -m "Release v1.4: Custom templates, new fields (Social Media, Other info), bug fixes"

# Push to GitHub
git push origin main
```

---

### Part 2: Create GitHub Release and Upload EXE

1. **Go to GitHub:**
   - Open your browser
   - Go to: `https://github.com/dubloox3/scam-report-builder`

2. **Create New Release:**
   - Click "Releases" in the right sidebar (or go to: `https://github.com/dubloox3/scam-report-builder/releases`)
   - Click "Create a new release" button (or "Draft a new release")

3. **Fill Release Details:**
   - **Tag version:** Type `v1.4` (this creates a new tag)
   - **Release title:** `Scam Report Builder v1.4`
   - **Description:** Copy and paste this:

     ```
     ## What's New in v1.4
     
     ### 🎉 New Features
     - **Custom Templates**: Create your own scam report templates with custom fields
     - **Social Media Field**: New "Scammer Social Media(s)" field in Main Info tab
     - **Other Info Field**: New "Other info" field between Geolocation and Started
     
     ### 🔧 Improvements & Bug Fixes
     - Custom template name/description auto-populates form fields
     - "New Report" button remembers last used template (including custom templates)
     - Fixed custom template fields not pre-filling on new reports
     - Improved template selection and management
     
     ### 📦 Files
     - Download `Scam-Report-Builder.exe` below (Windows standalone executable)
     - Source code is available in the repository
     
     ### ⚠️ Windows Security Warning
     On first run, Windows may show a security warning. Click "More info" → "Run anyway". This is normal for unsigned executables.
     ```

4. **Attach EXE:**
   - Scroll down to "Attach binaries by dropping them here or selecting them"
   - Click "selecting them" or drag and drop
   - Navigate to: `dist/Scam-Report-Builder.exe`
   - Select the file (it's about 241 MB)
   - Wait for upload to complete

5. **Publish Release:**
   - Make sure "Set as the latest release" is checked
   - Click "Publish release" button (green button at bottom)

---

### Part 3: Verify Everything Worked

1. **Check Repository:**
   - Go to your repository page
   - Verify all source files are present
   - Verify `dist/` folder is NOT in the repository (it shouldn't be)

2. **Check Release:**
   - Go to Releases page
   - Click on "v1.4" release
   - Verify:
     - ✅ Description looks correct
     - ✅ EXE file is attached and downloadable
     - ✅ Release is marked as "Latest"

3. **Test Download:**
   - Click the EXE download link
   - Verify it downloads correctly
   - File size should be ~241 MB

---

## Important Notes

✅ **What Gets Committed:**
- All source code files (`.py` files)
- Configuration files (`.spec`, `requirements.txt`, etc.)
- Documentation (`.md` files)
- Screenshots (`.jpg` files)

❌ **What Does NOT Get Committed** (automatically excluded by `.gitignore`):
- `dist/` folder (contains EXE)
- `build/` folder (PyInstaller temp files)
- `__pycache__/` directories
- `scam_report_config.json` (user config)
- `.report_data/` folder (user data)
- `Reports/` folder (user reports)

✅ **The EXE:**
- Goes ONLY in the GitHub Release (as an asset)
- Is NOT committed to the repository
- Users download from the Releases page

---

## Troubleshooting

**"Nothing to commit":**
- All changes are already committed
- Run `git status` to verify

**"dist/ folder appears in changes":**
- Check your `.gitignore` file includes `dist/`
- It should already be there

**"Can't push - authentication error":**
- Cursor should handle authentication automatically
- If not, you may need to set up GitHub credentials in Cursor settings

**"Release page shows wrong tag":**
- Make sure you typed `v1.4` exactly (case-sensitive)
- Don't include quotes or extra spaces

---

## Quick Reference Commands

```bash
# Check what will be committed
git status

# Stage all changes
git add .

# Commit
git commit -m "Release v1.4: Custom templates, new fields, bug fixes"

# Push to GitHub
git push origin main

# Verify .gitignore is working (should NOT list dist/ or build/)
git status --ignored
```

---

## Summary Checklist

- [ ] All source code is ready
- [ ] EXE is built in `dist/Scam-Report-Builder.exe`
- [ ] README.md is updated
- [ ] Screenshots are added (if ready)
- [ ] Committed changes with commit message
- [ ] Pushed to GitHub
- [ ] Created v1.4 release on GitHub
- [ ] Uploaded EXE to release
- [ ] Verified release is public and downloadable

**You're ready to publish! 🚀**
