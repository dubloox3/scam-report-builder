# GitHub Release Guide

This guide explains how to prepare and publish a release of Scam Report Builder on GitHub.

## Pre-Release Checklist

Before creating a release, verify everything is ready:

```bash
python verify_release_ready.py
```

This script checks:
- ✅ All required source files are present
- ✅ Build artifacts are properly excluded (in .gitignore)
- ✅ Project structure is correct
- ✅ No debug code in production files
- ✅ EXE is ready for upload

## Files Structure

### **KEEP in Repository:**
- ✅ `main.py` - Application entry point
- ✅ `core/` - Core application modules
- ✅ `ui/` - User interface components
- ✅ `requirements.txt` - Python dependencies
- ✅ `README.md` - Project documentation
- ✅ `BUILD_INSTRUCTIONS.md` - Build instructions
- ✅ `build_exe.py` - Build script for users
- ✅ `Scam-Report-Builder.spec` - PyInstaller configuration
- ✅ `.gitignore` - Git ignore rules
- ✅ Screenshots (`.jpg` files) - Documentation

### **REMOVE/EXCLUDE from Repository:**
- ❌ `dist/` folder - Contains EXE (build artifact)
- ❌ `build/` folder - PyInstaller temporary files
- ❌ `__pycache__/` folders - Python cache files
- ❌ `scam_report_config.json` - User configuration
- ❌ `.report_data/` - User data folder
- ❌ `Reports/` - User reports folder
- ❌ `*.pyc` files - Compiled Python files

**Note:** These are automatically excluded via `.gitignore`, but verify with `git status` before committing.

## Building the EXE

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller
   ```

2. **Build the EXE:**
   ```bash
   python build_exe.py
   ```

3. **Verify the EXE:**
   - The EXE will be created in `dist/Scam-Report-Builder.exe`
   - Test it on a clean machine (or VM) without Python installed
   - Verify all features work correctly

## Creating a GitHub Release

### Step 1: Prepare the Repository

1. **Clean build artifacts (optional, already in .gitignore):**
   ```bash
   # These folders won't be committed anyway, but you can remove them locally:
   rmdir /s /q dist build
   # Or use cleanup script if you recreate it
   ```

2. **Commit all source code:**
   ```bash
   git add .
   git commit -m "Release v1.0.0: Scam Report Builder"
   git push origin main
   ```

### Step 2: Create a Release Tag

1. **Tag the release:**
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

   Or create the tag through GitHub web interface.

### Step 3: Create GitHub Release

1. **Go to GitHub Releases:**
   - Navigate to: `https://github.com/YOUR_USERNAME/YOUR_REPO/releases`
   - Click "Draft a new release"

2. **Fill in release details:**
   - **Tag:** Select or create tag (e.g., `v1.0.0`)
   - **Title:** `Scam Report Builder v1.0.0`
   - **Description:** 
     ```
     ## What's New
     - Initial release
     - Report generation with embedded images
     - Template-based report creation
     - Report modification capability
     
     ## Installation
     Download `Scam-Report-Builder.exe` from the assets below and run it.
     No installation required - just double-click the EXE file.
     
     ## System Requirements
     - Windows 10 or later
     - No additional software required
     ```

3. **Upload the EXE:**
   - Scroll to "Attach binaries"
   - Drag and drop `dist/Scam-Report-Builder.exe`
   - Wait for upload to complete

4. **Publish the release:**
   - Click "Publish release"
   - Users can now download the EXE from the Releases page

## Release Notes Template

Use this template for release notes:

```markdown
## Scam Report Builder v1.0.0

### Features
- Create professional scam reports with embedded evidence
- Support for multiple payment methods and evidence types
- Report modification and re-export capability
- Template-based report generation

### Installation
1. Download `Scam-Report-Builder.exe` from the assets below
2. Double-click to run (no installation needed)
3. Follow the on-screen instructions

### System Requirements
- Windows 10 or later
- 4 GB RAM minimum
- 500 MB free disk space

### Build from Source
If you prefer to build from source:
1. Install Python 3.8+ and dependencies: `pip install -r requirements.txt`
2. Run: `python build_exe.py`
3. See `BUILD_INSTRUCTIONS.md` for details
```

## Post-Release

1. **Update README.md** (if needed) with download links:
   ```markdown
   ## Download
   Get the latest release from [GitHub Releases](https://github.com/YOUR_USERNAME/YOUR_REPO/releases)
   ```

2. **Test the release:**
   - Download the EXE from GitHub Releases
   - Test on a clean Windows machine
   - Verify all features work

3. **Monitor for issues:**
   - Check GitHub Issues for user feedback
   - Fix any critical bugs and create patch releases

## Troubleshooting

### EXE is too large
- The EXE includes all dependencies (PySide6, PIL, etc.)
- Typical size: 200-300 MB
- This is normal for PyInstaller one-file builds
- Consider using `--onedir` mode for smaller initial download (but multiple files)

### EXE flagged by antivirus
- This is common for unsigned executables
- Users may need to:
  - Right-click → Properties → Unblock
  - Add exception to antivirus
  - Consider code signing for future releases

### EXE doesn't run
- Verify all dependencies are included in `.spec` file
- Test on clean Windows VM
- Check PyInstaller warnings during build
- Review `warn-Scam-Report-Builder.txt` in build folder

## Versioning

Follow [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH` (e.g., `1.0.0`)
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

## Security Considerations

- ✅ No hardcoded secrets or credentials
- ✅ No network connections (offline application)
- ✅ All data stored locally
- ⚠️ EXE is unsigned (users may see security warnings)
- ⚠️ Consider code signing for production releases
