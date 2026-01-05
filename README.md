# Scam Report Builder

## 📸 Application Screenshots

### 1. Initial Setup - Report Folder
![Report Folder Setup](01-report-folder-setup.jpg)
*First run: Choose where to save your scam reports*

### 2. Template Selection
![Template Selection](02-template-selection.jpg)  
*Select the type of scam report to create*

### 3. Main Information Tab
![Main Info Tab](03-main-info-tab.jpg)
*Enter scammer details: aliases, emails, websites, timeline*

### 4. Payment Information Tab
![Payment Info Tab](04-payment-info-tab.jpg)
*Add payment amounts, bank accounts, and other financial details*

### 5. Evidence Tab
![Evidence Tab](05-evidence-tab.jpg)
*Upload screenshots, photos, passports, and other evidence*

### 6. Remarks Tab
![Remarks Tab](06-remarks-tab.jpg)
*Add additional notes and observations*

### 7. Generated Report Example
![Example Report](07-example-report.jpg)
*Final ODT report with embedded images and organized sections*

Scam Report Builder - Quick Start Guide
What Is It?
-A desktop app to create organized scam reports with evidence. Fill in what you know, add screenshots, get a professional document ready to share with authorities.

Quick Start
-Run python main.py
-Pick a folder to save reports (once only)
-Choose template (currently only "Advance-Fee Scam", more tbd)
-Fill in the tabs with scam details
-Add images (scammers passports, evidence, screenshots, ...)
-Click "Create Scam Report" → Save as ODT file

Key Features
-No required fields - Fill in only what you have
-Image support - Add evidence screenshots/photos (cropping/resizing for the report included)
-Automatic formatting - Clean, professional layout
-ODT format - Opens in Word, LibreOffice, Google Docs
-Report numbering - Keeps your cases organized (continue with your own format or start a new numbering)

What You Need
-Python 3.8+
-Install: pip install PySide6 Pillow
-only tested on Windows

Report Contains
-Scammer info (aliases, emails, websites, ...)
-Payment details (amount, bank accounts)
-Evidence (images with captions)
-Timeline & remarks

Tips
-Save reports to a dedicated folder (numbering logic will count upwards)
-Use clear filenames for images

-talk to your reporting contact what info they need (and adjust the format)
