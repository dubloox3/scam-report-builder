# Scam Report Builder v1.4

## 📸 Application Screenshots

### 1. Initial Setup - Report Folder
![Report Folder Setup](01%20initial%20Q%20for%20report%20folder.jpg)
*First run: Choose where to save your scam reports*

### 2. Template Selection
![Template Selection](02%20template%20selection.jpg)  
*Select the type of scam report to create*

### 3. Main Information Tab
![Main Info Tab](03%20main%20info%20tab.jpg)
*Enter scammer details: aliases, emails, websites, timeline*

### 4. Payment Information Tab
![Payment Info Tab](04%20payment%20info%20tab.jpg)
*Add payment amounts, bank accounts, and other financial details*

### 5. Evidence Tab
![Evidence Tab](05%20Evidence%20tab.jpg)
*Upload screenshots, photos, passports, and other evidence*

### 6. Remarks Tab
![Remarks Tab](06%20Remarks%20tab.jpg)
*Add additional notes and observations*

### 7. Custom Template Editor (NEW in v1.4)
![Custom Template Editor](08%20custom%20template%20editor.jpg)
*Create your own custom scam report templates with custom fields*

### 8. Custom Template Selection (NEW in v1.4)
![Custom Template Selection](09%20custom%20template%20selection.jpg)
*Select from your custom templates alongside built-in templates*

### 9. Generated Report Example
![Example Report](07%20Example%20report.jpg)
*Final ODT report with embedded images and organized sections*

## What Is It?
A desktop application to create organized, professional scam reports with embedded evidence. Fill in what you know, add screenshots, and generate a ready-to-share document.

## Features

- **Built-in Templates**: Start with pre-configured templates (e.g., Advance-Fee Scam)
- **Custom Templates** (NEW in v1.4): Create your own templates with custom fields and requirements
- **Evidence Management**: Upload and embed screenshots, photos, passports, and other evidence
- **Payment Tracking**: Record payment amounts, bank accounts, and other payment methods
- **Professional Output**: Generate ODT (OpenDocument Text) reports with embedded images
- **Report Management**: Modify existing reports, track report numbers, and organize your reporting workflow

---

## Quick Start

### Option 1: Run from Source
```bash
pip install -r requirements.txt
python main.py
```

### Option 2: Use Standalone EXE (Windows) - **Recommended**

**Download the latest release:**
- Go to [GitHub Releases](https://github.com/dubloox3/scam-report-builder/releases)
- Download `Scam-Report-Builder.exe` from the latest release (v1.4)
- No installation needed - just download and run!

**First Run:**
1. Double-click `Scam-Report-Builder.exe` to run
2. **Windows Security Warning:** On first run, Windows may show "Windows protected your PC" warning
   - Click "More info"
   - Click "Run anyway"
   - This is normal for unsigned executables (the app is safe, just not code-signed)
3. The EXE creates files next to itself:
   - `Reports/` folder for your reports
   - `.report_data/` folder for modification data
   - `scam_report_config.json` for settings

**Note:** The EXE is portable - you can move it anywhere and it will work. All data is stored relative to the EXE location.

---

## Using Custom Templates (NEW in v1.4)

Create your own scam report templates tailored to your specific needs:

1. **Create a Custom Template:**
   - Click "Create Custom Template" in the template selection dialog
   - Fill in the template editor with:
     - Template name (will populate "Type of scam" field)
     - Description (will populate "Short summary" field)
     - Select which fields to include
     - Mark fields as required or optional
   - Save your template for future use

2. **Use Custom Templates:**
   - Custom templates appear in the template selection dialog
   - Select your custom template like any built-in template
   - The template name and description automatically populate the form
   - Create reports using your custom template structure

3. **Template Features:**
   - Customize field labels and requirements
   - Choose which fields to include (aliases, emails, websites, social media, etc.)
   - Option to use custom filename generation field
   - Templates are saved as JSON files in `templates/custom/` folder

### First Run
1. **Choose Report Folder:** Select where to save reports (this folder is remembered)
2. **Select Template:** Choose the type of scam report (currently "Advance-Fee Scam")
3. **Fill in the Tabs:**
   - **Main Info:** Scammer aliases, emails, websites, IPs, locations, dates
   - **Payment Info:** Amount, bank accounts, other payment methods
   - **Evidence:** Upload images (passports, photos, IDs) - supports cropping and rotation
   - **Remarks:** Additional notes
4. **Create Report:** Click "Create Scam Report", set report number, and save

---

## Key Features

- **No required fields** - Fill in only what you have
- **Image support** - Crop, rotate, resize images before adding (remembers last folder)
- **Report numbering** - Automatic sequential numbering with customizable formats
- **Modify reports** - Edit existing reports right after creation (keeps same number)
- **New report option** - Clear form and create another report (number auto-increments)
- **ODT format** - Opens in Word, LibreOffice, Google Docs
- **Professional layout** - Clean, organized document with embedded images

---

## Usage Tips

- **Main alias:** Used in the filename - make it meaningful and unique
- **Images:** Last selected folder is remembered for faster batch processing
- **Report numbers:** Modifying keeps the same number; "New Report" increments
- **JSON files:** Automatically saved in `.report_data` folder for modification capability
- **Save location:** Always pre-selects your chosen reports folder

---

## System Requirements

**For EXE version:**
- Windows 10/11
- No Python installation needed

**For source version:**
- Python 3.8+
- Windows (tested on Windows, may work on other platforms)
- Dependencies: PySide6, Pillow, odfpy, python-dateutil

## Building the EXE (For Developers)

To create the standalone EXE:

1. **Install PyInstaller:**
   ```bash
   pip install pyinstaller
   ```

2. **Build the EXE:**
   ```bash
   python build_exe.py
   ```
   Or manually:
   ```bash
   pyinstaller Scam-Report-Builder.spec
   ```

3. **Output:** The EXE will be in the `dist/` folder

**Build Notes:**
- The EXE is a single file (--onefile mode)
- All dependencies are bundled
- Reports folder is created next to the EXE (not in temp folder)
- JSON data folder (`.report_data`) is created next to the EXE

---

## File Structure

- **Reports:** Saved in your chosen folder (or default `Reports/` folder)
- **JSON data:** Stored in `.report_data/` folder (application root) for modification
- **Config:** `scam_report_config.json` stores settings and report numbering

