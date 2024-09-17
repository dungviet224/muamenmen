import os
import subprocess
import sys
import time
from pathlib import Path
import requests  # Import the requests library

# Function to install colorama if not already installed
def install_colorama():
    try:
        import colorama
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "colorama"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        import colorama

# Install colorama
install_colorama()

from colorama import init, Fore, Style

init(autoreset=True)

# Define the logo with new colors
logo = r'''
  _  _  ___ _   ___   _____ _  _  __   _____ ___ _____   ___  _   _ _  _  ___ 
 | \| |/ __| | | \ \ / / __| \| | \ \ / /_ _| __|_   _| |   \| | | | \| |/ __|
 | .` | (_ | |_| |\ V /| _|| .` |  \ V / | || _|  | |   | |) | |_| | .` | (_ |
 |_|\_|\___|\___/  |_| |___|_|\_|   \_/ |___|___| |_|   |___/ \___/|_|\_|\___|                                                                                                                                         
'''

# List of libraries to install
libraries = [
    "pandas",
    "selenium",
    "PyQt5",
    "Pillow",
    "pyperclip",
    "pywin32",
    "gitpython",
    "openpyxl",
    "pyautogui",
    "requests"
]

def install_requirements():
    # Display the logo and message with different colors
    print(Fore.YELLOW + Style.BRIGHT + logo)
    print(Fore.LIGHTMAGENTA_EX + Style.BRIGHT + "[INFO] Downloading and installing libraries...\n")

    # Header for the update table with new colors
    print(Fore.LIGHTGREEN_EX + Style.BRIGHT + f"{'Library':<25} | Status")
    print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "-" * 40)

    missing_libraries = []

    for lib in libraries:
        try:
            print(Fore.LIGHTCYAN_EX + Style.BRIGHT + f"[{lib:<20}] ", end='')
            sys.stdout.flush()

            # Check if the library is already installed
            result = subprocess.run([sys.executable, "-m", "pip", "show", lib], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if result.returncode == 0:
                print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "[Already installed]")
            else:
                missing_libraries.append(lib)
        except subprocess.CalledProcessError as e:
            print(Fore.RED + Style.BRIGHT + f"[Error checking {lib}]")

    if missing_libraries:
        for lib in missing_libraries:
            print(Fore.YELLOW + Style.BRIGHT + f"[Installing {lib}...]", end='')
            sys.stdout.flush()
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(Fore.LIGHTGREEN_EX + Style.BRIGHT + f"[Installation complete: {lib}]")

def download_main_file():
    main_file = Path("main.py")
    print(Fore.LIGHTMAGENTA_EX + Style.BRIGHT + "[INFO] Checking for main.py updates...")

    try:
        response = requests.get("https://raw.githubusercontent.com/dungviet224/muamenmen/main/main.py")
        response.raise_for_status()  # Raise an error for bad responses
        with open(main_file, "wb") as file:
            file.write(response.content)
        print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "[INFO] main.py has been updated successfully.")
    except requests.RequestException as e:
        print(Fore.RED + Style.BRIGHT + f"[Error downloading main.py: {e}]")
        sys.exit(1)

def run_main_file():
    try:
        print(Fore.LIGHTCYAN_EX + Style.BRIGHT + "[INFO] Running main.py...")
        result = subprocess.run([sys.executable, "main.py"])
        if result.returncode == 0:
            print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "[INFO] main.py executed successfully.")
            return True
        else:
            print(Fore.RED + Style.BRIGHT + "[ERROR] main.py failed to execute.")
            return False
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + f"[ERROR] Exception occurred: {e}")
        return False

def close_message():
    print(Fore.LIGHTMAGENTA_EX + Style.BRIGHT + "\nAll tasks completed.")
    print(Fore.LIGHTMAGENTA_EX + Style.BRIGHT + "[Press Enter to close this window]")
    input()

if __name__ == "__main__":
    download_main_file()
    if not run_main_file():
        install_requirements()  # Install missing libraries if any
        run_main_file()  # Try running main.py again after installing libraries
    close_message()
