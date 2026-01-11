# Building Scam Report Builder EXE

## Prerequisites

1. Install Python 3.8+ (if not already installed)
2. Install build dependencies:
   ```bash
   pip install pyinstaller
   pip install -r requirements.txt
   ```

## Building the EXE

### Method 1: Using the build script (Recommended)
```bash
python build_exe.py
```

### Method 2: Using PyInstaller directly
```bash
pyinstaller Scam-Report-Builder.spec
```

### Method 3: Using PyInstaller with command line
```bash
pyinstaller --name=Scam-Report-Builder --onefile --windowed --clean main.py
```

## Output

The EXE will be created in the `dist/` folder:
- `dist/Scam-Report-Builder.exe`

## Testing the EXE

1. Copy `Scam-Report-Builder.exe` to a test folder
2. Run the EXE
3. Verify:
   - Reports folder is created next to the EXE (not in temp folder)
   - `.report_data` folder is created next to the EXE
   - Config file is created next to the EXE
   - Application runs without errors
   - All features work (image upload, report creation, etc.)

## Troubleshooting

### EXE is too large
- The EXE includes all PySide6 libraries and dependencies
- Typical size: 50-100 MB (this is normal for PySide6 apps)
- To reduce size, you can exclude unused modules in the spec file

### EXE doesn't start
- Check Windows Event Viewer for errors
- Try running from command line to see error messages
- Ensure all dependencies are included in hiddenimports

### Path issues
- The EXE uses `Path(sys.executable).parent` for all file operations
- All folders (Reports, .report_data) are created next to the EXE
- Config file is also created next to the EXE

### Missing modules
- Add missing modules to `hiddenimports` in the spec file
- Rebuild the EXE

## Windows Security Warning

When users first run the EXE, Windows may show:
- "Windows protected your PC" warning
- This is normal for unsigned executables
- Users need to click "More info" → "Run anyway"
- Consider code signing for production releases (requires certificate)
