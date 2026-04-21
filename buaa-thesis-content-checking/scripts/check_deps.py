#!/usr/bin/env python3
"""
Dependency checker for paper audit skill.
Checks if required packages are installed and offers to install them.
"""

import sys
import subprocess
import os


def check_package(package_name, import_name=None):
    """Check if a package is installed."""
    if import_name is None:
        import_name = package_name
    try:
        __import__(import_name)
        return True, None
    except ImportError as e:
        return False, str(e)


def install_package(package_name):
    """Install a package using python3 -m pip."""
    print(f"Installing {package_name}...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package_name, "--quiet"],
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            print(f"  ✓ {package_name} installed successfully")
            return True
        else:
            print(f"  ✗ Failed to install {package_name}: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"  ✗ Installation timed out for {package_name}")
        return False
    except Exception as e:
        print(f"  ✗ Error installing {package_name}: {e}")
        return False


def main():
    print("=" * 60)
    print("Checking dependencies for paper audit skill...")
    print("=" * 60)

    packages_to_check = [
        ("pdfplumber", "pdfplumber"),
        ("PyMuPDF (fitz)", "fitz"),
        ("pypdf", "pypdf"),
    ]

    missing = []
    all_ok = True

    for display_name, import_name in packages_to_check:
        ok, error = check_package(display_name, import_name)
        if ok:
            print(f"✓ {display_name}: OK")
        else:
            print(f"✗ {display_name}: NOT FOUND")
            missing.append((display_name, import_name))
            all_ok = False

    print()

    if all_ok:
        print("All dependencies are installed!")
        print("You can now run the paper audit script.")
        return 0

    print(f"Missing {len(missing)} package(s).")
    response = input("Would you like to install them now? [Y/n]: ").strip().lower()

    if response == "" or response == "y" or response == "yes":
        print()
        success_count = 0
        for display_name, import_name in missing:
            if install_package(import_name):
                success_count += 1

        print()
        if success_count == len(missing):
            print(f"✓ All {success_count} package(s) installed successfully!")
            print("You can now run the paper audit script.")
            return 0
        else:
            print(f"⚠ {success_count}/{len(missing)} package(s) installed.")
            print("Please install the remaining packages manually:")
            for display_name, import_name in missing:
                print(f"  python3 -m pip install {import_name}")
            return 1
    else:
        print("Skipping installation.")
        print("To install manually, run:")
        for display_name, import_name in missing:
            print(f"  python3 -m pip install {import_name}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
