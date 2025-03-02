#!/usr/bin/env python3
"""
BART Hub 2.0 - Main launcher script

This script ensures all required dependencies are available and starts the BART Hub 2.0 application.
"""

import sys
import os
import importlib.util
import tkinter as tk
from tkinter import messagebox


def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'pandas',
        'matplotlib',
        'pygame'
    ]

    missing_packages = []

    for package in required_packages:
        if importlib.util.find_spec(package) is None:
            missing_packages.append(package)

    return missing_packages


def install_dependencies(missing_packages):
    """Attempt to install missing dependencies"""
    try:
        import subprocess

        # Install each missing package
        for package in missing_packages:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

        return True
    except Exception as e:
        print(f"Error installing dependencies: {e}")
        return False


def check_asset_directory():
    """Check if assets directory exists, create if not"""
    assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
        print(f"Created assets directory: {assets_dir}")

        # Create a readme file in the assets directory
        with open(os.path.join(assets_dir, 'README.txt'), 'w') as f:
            f.write("Place sound files (pump.wav, pop.wav, cashout.wav) and icons in this directory.")


def main():
    """Main function to run BART Hub 2.0"""
    # Check dependencies
    missing_packages = check_dependencies()

    if missing_packages:
        print(f"Missing required packages: {', '.join(missing_packages)}")

        # Try to install missing packages
        if install_dependencies(missing_packages):
            print("All dependencies installed successfully.")
        else:
            print("Failed to install dependencies. Please install them manually:")
            print(f"pip install {' '.join(missing_packages)}")
            return

    # Check asset directory
    check_asset_directory()

    # Check if the required modules exist in the current directory
    required_modules = ['BART_hub2.py', 'BART_experiment.py', 'BART_utils.py']
    missing_modules = [m for m in required_modules if not os.path.exists(m)]

    if missing_modules:
        print(f"Error: Missing required module files: {', '.join(missing_modules)}")
        print("Please ensure all required files are in the same directory as this script.")
        return

    # Import BARTHub and run
    try:
        from BART_hub2 import BARTHub

        root = tk.Tk()
        app = BARTHub(root)
        root.mainloop()
    except Exception as e:
        # Show error message if GUI is available, otherwise print to console
        error_message = f"Error starting BART Hub 2.0: {str(e)}"
        try:
            messagebox.showerror("Error", error_message)
        except:
            print(error_message)

        # Print detailed traceback
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()