import os
import subprocess
import sys
import time
from pathlib import Path

# Function to install colorama if not already installed
def install_colorama():
    try:
        import colorama
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "colorama"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        import colorama

# Function to install requests if not already installed
def install_requests():
    try:
        import requests
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        import requests

# Install colorama and requests
install_colorama()
install_requests()

from colorama import init, Fore, Style
import requests

init(autoreset=True)

# Display the logo first
logo = r'''
  _  _  ___ _   ___   _____ _  _  __   _____ ___ _____   ___  _   _ _  _  ___ 
 | \| |/ __| | | \ \ / / __| \| | \ \ / /_ _| __|_   _| |   \| | | | \| |/ __|
 | .` | (_ | |_| |\ V /| _|| .` |  \ V / | || _|  | |   | |) | |_| | .` | (_ |
 |_|\_|\___|\___/  |_| |___|_|\_|   \_/ |___|___| |_|   |___/ \___/|_|\_|\___|                                                                                                                                         
'''

print(Fore.YELLOW + Style.BRIGHT + logo)

libraries = [
    "pandas",
    "selenium",
    "PyQt5",
    "Pillow",
    "pyperclip",
    "pywin32",
    "gitpython",
    "openpyxl",
    "pyautogui"
]

def install_requirements():
    print(Fore.LIGHTMAGENTA_EX + Style.BRIGHT + "[INFO] Downloading and installing libraries...\n")
    missing_libraries = []

    for lib in libraries:
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "show", lib], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if result.returncode != 0:
                missing_libraries.append(lib)
        except subprocess.CalledProcessError:
            pass

    if missing_libraries:
        print(Fore.LIGHTCYAN_EX + Style.BRIGHT + f"{'Library':<25} | Status")
        print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "-" * 40)
        
        for lib in missing_libraries:
            print(Fore.LIGHTCYAN_EX + Style.BRIGHT + f"[{lib:<20}] ", end='')
            sys.stdout.flush()
            try:
                print(Fore.YELLOW + Style.BRIGHT + "[Installing...]", end='')
                subprocess.check_call([sys.executable, "-m", "pip", "install", lib], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "[Installation complete]")
            except subprocess.CalledProcessError:
                print(Fore.RED + Style.BRIGHT + f"[Error during installation: {lib}]")
                sys.exit(1)

def download_main_file():
    main_file = Path("main.py")
    print(Fore.LIGHTMAGENTA_EX + Style.BRIGHT + "[INFO] Checking for main.py updates...")

    try:
        response = requests.get("https://raw.githubusercontent.com/dungviet224/muamenmen/main/main.py")
        response.raise_for_status()  # Raise an error for bad responses
        with open(main_file, "wb") as file:
            file.write(response.content)
        print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "[INFO] main.py has been updated successfully.")
    except requests.RequestException:
        print(Fore.RED + Style.BRIGHT + "[Error downloading main.py]")
        sys.exit(1)

def run_main_file():
    try:
        # Running main.py and hiding the error output by redirecting stderr
        print(Fore.LIGHTCYAN_EX + Style.BRIGHT + "[INFO] Running main.py...")
        result = subprocess.run([sys.executable, "main.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if result.returncode == 0:
            print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "[INFO] main.py executed successfully.")
            return True
        else:
            print(Fore.RED + Style.BRIGHT + "[ERROR] main.py execution failed.")
            return False
    except Exception:
        print(Fore.RED + Style.BRIGHT + "[ERROR] Exception occurred while running main.py.")
        return False

if __name__ == "__main__":
    download_main_file()  # First, download or update main.py
    if not run_main_file():  # Try to run main.py
        install_requirements()  # If it fails, install missing libraries
        run_main_file()  # Try running main.py again after installing libraries

    sys.exit(0)  # Exit the script automatically after completion
