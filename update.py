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

# Define the message
message = "[INFO] Downloading and installing libraries...\n"

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
    "requests"  # Add requests to the list
]

def install_requirements():
    # Display the logo and message with different colors
    print(Fore.YELLOW + Style.BRIGHT + logo)
    print(Fore.LIGHTMAGENTA_EX + Style.BRIGHT + message)

    # Header for the update table with new colors
    print(Fore.LIGHTGREEN_EX + Style.BRIGHT + f"{'Library':<25} | Status")
    print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "-" * 40)

    for lib in libraries:
        try:
            # Align library name and status with brackets, change the colors
            print(Fore.LIGHTCYAN_EX + Style.BRIGHT + f"[{lib:<20}] ", end='')
            sys.stdout.flush()
            time.sleep(0.5)  # Simulate some delay

            # Check if the library is already installed
            result = subprocess.run([sys.executable, "-m", "pip", "show", lib], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if result.returncode == 0:
                print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "[Already installed]")
            else:
                print(Fore.YELLOW + Style.BRIGHT + "[Installing...]", end='')
                sys.stdout.flush()
                # Simulate progress with yellow dots
                for _ in range(3):
                    sys.stdout.write(Fore.YELLOW + Style.BRIGHT + " .")
                    sys.stdout.flush()
                    time.sleep(0.5)
                subprocess.check_call([sys.executable, "-m", "pip", "install", lib], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "[Installation complete]")
        except subprocess.CalledProcessError as e:
            print(Fore.RED + Style.BRIGHT + f"[Error during installation: {lib}]")
            sys.exit(1)

def check_and_download_main_file():
    # Check if main.py exists
    main_file = Path("main.py")
    if main_file.exists():
        print(Fore.LIGHTBLUE_EX + Style.BRIGHT + "\n[INFO] main.py has been updated successfully.")
    else:
        print(Fore.LIGHTRED_EX + Style.BRIGHT + "\n[INFO] main.py not found. Downloading...")
        try:
            response = requests.get("https://raw.githubusercontent.com/dungviet224/muamenmen/main/main.py")
            response.raise_for_status()  # Raise an error for bad responses
            with open(main_file, "wb") as file:
                file.write(response.content)
            print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "[Download complete] main.py has been downloaded.")
        except requests.RequestException as e:
            print(Fore.RED + Style.BRIGHT + f"[Error downloading main.py: {e}]")
            sys.exit(1)

def close_message():
    # Print the exit message in a standout color
    print(Fore.LIGHTMAGENTA_EX + Style.BRIGHT + "\nAll tasks completed.")
    print(Fore.LIGHTMAGENTA_EX + Style.BRIGHT + "[Press Enter to close this window]")

    # Wait for the user to press Enter to close the window
    input()

if __name__ == "__main__":
    install_requirements()
    check_and_download_main_file()  # Updated function name
    close_message()
