"""
Verify project is ready for GitHub release
Checks that all required files are present and build artifacts are excluded
Run: python verify_release_ready.py
"""

import os
from pathlib import Path

# ANSI color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def print_success(message):
    """Print success message"""
    print(f"{GREEN}[OK]{RESET} {message}")

def print_error(message):
    """Print error message"""
    print(f"{RED}[ERROR]{RESET} {message}")

def print_warning(message):
    """Print warning message"""
    print(f"{YELLOW}[WARN]{RESET} {message}")

def check_required_files():
    """Check that all required source files are present"""
    print("\n1. Checking required source files...")
    required_files = [
        'main.py',
        'requirements.txt',
        'README.md',
        'BUILD_INSTRUCTIONS.md',
        'build_exe.py',
        'Scam-Report-Builder.spec',
        'core/__init__.py',
        'core/config_manager.py',
        'core/odt_generator.py',
        'core/template_manager.py',
        'ui/__init__.py',
        'ui/main_window.py',
        'ui/dialogs/__init__.py',
        'ui/dialogs/report_number_dialog.py',
        'ui/dialogs/template_selection_dialog.py',
        'ui/widgets/__init__.py',
        'ui/widgets/dynamic_list_widget.py',
        'ui/widgets/image_crop_dialog.py',
        'ui/widgets/image_list_widget.py',
        'ui/widgets/other_payment_widget.py',
    ]
    
    missing = []
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)
        else:
            print_success(f"Found: {file}")
    
    if missing:
        print_error(f"Missing required files: {', '.join(missing)}")
        return False
    
    return True

def check_excluded_files():
    """Check that build artifacts and user files are excluded (they can exist locally but should be in .gitignore)"""
    print("\n2. Checking excluded files (can exist locally, must be in .gitignore)...")
    excluded_paths = [
        ('dist/', 'Build output - OK if in .gitignore'),
        ('build/', 'Build temp - OK if in .gitignore'),
        ('scam_report_config.json', 'User config - should not be committed'),
        ('.report_data/', 'User data - should not be committed'),
        ('Reports/', 'User reports - should not be committed'),
    ]
    
    found_excluded = []
    gitignore_path = Path('.gitignore')
    gitignore_content = ''
    if gitignore_path.exists():
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            gitignore_content = f.read()
    
    for path, description in excluded_paths:
        if Path(path).exists():
            # Check if it's in .gitignore
            path_pattern = path.rstrip('/')
            if path_pattern in gitignore_content or path.rstrip('/').replace('/', '') in gitignore_content:
                print_success(f"{path} exists locally but is in .gitignore - OK")
            else:
                found_excluded.append((path, description))
                print_warning(f"{path} exists but NOT in .gitignore - {description}")
    
    if found_excluded:
        print_warning(f"Found {len(found_excluded)} excluded path(s) not in .gitignore")
        return False
    
    print_success("All excluded paths are properly configured in .gitignore")
    return True

def check_gitignore():
    """Verify .gitignore is properly configured"""
    print("\n3. Checking .gitignore configuration...")
    gitignore_path = Path('.gitignore')
    
    if not gitignore_path.exists():
        print_error(".gitignore file not found!")
        return False
    
    with open(gitignore_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_patterns = {
        '__pycache__': 'Python cache',
        'dist': 'Build output',
        'build': 'Build temp',
        'scam_report_config.json': 'User config',
        '.report_data': 'User data',
        'Reports': 'User reports',
        '*.odt': 'Generated reports',
    }
    
    missing_patterns = []
    for pattern, description in required_patterns.items():
        if pattern not in content:
            missing_patterns.append(f"{pattern} ({description})")
    
    if missing_patterns:
        print_error(f"Missing patterns in .gitignore: {', '.join(missing_patterns)}")
        return False
    
    # Check that .spec file is NOT ignored (should be included)
    if '*.spec' in content and 'Scam-Report-Builder.spec' not in content:
        print_warning(".spec pattern found in .gitignore - verify Scam-Report-Builder.spec is explicitly allowed")
    
    print_success(".gitignore is properly configured")
    return True

def check_exe_location():
    """Check if EXE exists and provide release instructions"""
    print("\n4. Checking EXE for GitHub Releases...")
    
    exe_path = Path('dist/Scam-Report-Builder.exe')
    if exe_path.exists():
        file_size = exe_path.stat().st_size / (1024 * 1024)  # Size in MB
        print_success(f"EXE found: {exe_path} ({file_size:.1f} MB)")
        print("\n" + "="*60)
        print("EXE RELEASE INSTRUCTIONS:")
        print("="*60)
        print("1. DO NOT commit the EXE to the repository")
        print("2. Create a GitHub Release:")
        print("   - Go to: https://github.com/YOUR_USERNAME/YOUR_REPO/releases/new")
        print("   - Create a new tag (e.g., v1.0.0)")
        print("   - Upload the EXE as a release asset:")
        print(f"     File: {exe_path}")
        print("3. Users can download from the Releases page")
        print("="*60)
        return True
    else:
        print_warning("EXE not found in dist/ folder")
        print("   To create EXE: python build_exe.py")
        return False

def check_structure():
    """Check overall project structure"""
    print("\n5. Checking project structure...")
    
    structure_ok = True
    
    # Check core module
    if not Path('core').is_dir():
        print_error("core/ directory not found")
        structure_ok = False
    else:
        print_success("core/ directory exists")
    
    # Check ui module
    if not Path('ui').is_dir():
        print_error("ui/ directory not found")
        structure_ok = False
    else:
        print_success("ui/ directory exists")
    
    # Check for __init__.py files
    init_files = [
        'core/__init__.py',
        'ui/__init__.py',
        'ui/dialogs/__init__.py',
        'ui/widgets/__init__.py',
    ]
    
    for init_file in init_files:
        if not Path(init_file).exists():
            print_error(f"Missing: {init_file}")
            structure_ok = False
        else:
            print_success(f"Found: {init_file}")
    
    return structure_ok

def check_no_debug_code():
    """Quick check for obvious debug code"""
    print("\n6. Checking for debug code...")
    
    debug_patterns = [
        ('print(', 'Debug print statements'),
        ('# DEBUG', 'DEBUG comments'),
        ('# TODO', 'TODO comments'),
    ]
    
    source_files = list(Path('.').rglob('*.py'))
    source_files = [f for f in source_files if 'build' not in str(f) and 'dist' not in str(f)]
    
    found_debug = False
    for pattern, description in debug_patterns:
        matches = []
        for py_file in source_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Allow print in build_exe.py and this script
                    if pattern in content and py_file.name not in ['build_exe.py', 'verify_release_ready.py']:
                        # Count occurrences
                        count = content.count(pattern)
                        if count > 0:
                            matches.append((str(py_file), count))
            except Exception:
                pass
        
        if matches:
            found_debug = True
            print_warning(f"Found {description} in {len(matches)} file(s)")
            for file, count in matches[:3]:  # Show first 3
                print(f"  - {file}: {count} occurrence(s)")
            if len(matches) > 3:
                print(f"  ... and {len(matches) - 3} more")
    
    if not found_debug:
        print_success("No obvious debug code found (print statements are OK in build scripts)")
    
    return True  # Don't fail on this, just warn

def main():
    """Main verification function"""
    print("="*60)
    print("GitHub Release Verification")
    print("="*60)
    
    results = []
    
    results.append(("Required Files", check_required_files()))
    results.append(("Excluded Files", check_excluded_files()))
    results.append((".gitignore Config", check_gitignore()))
    results.append(("Project Structure", check_structure()))
    results.append(("EXE for Release", check_exe_location()))
    results.append(("Debug Code Check", check_no_debug_code()))
    
    # Summary
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    
    all_passed = True
    for name, result in results:
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"{status} - {name}")
        if not result:
            all_passed = False
    
    print("="*60)
    
    if all_passed:
        print(f"\n{GREEN}[OK] Project is ready for GitHub release!{RESET}")
        print("\nNext steps:")
        print("1. Review all files: git status")
        print("2. Commit changes: git add . && git commit -m 'Prepare for release'")
        print("3. Create GitHub release and upload EXE from dist/ folder")
    else:
        print(f"\n{RED}[FAIL] Some checks failed. Please fix the issues above.{RESET}")
    
    print()
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())
