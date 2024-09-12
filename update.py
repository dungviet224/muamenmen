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
        print("Installing colorama...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "colorama"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        import colorama
    else:
        import colorama

# Install colorama
install_colorama()

from colorama import init, Fore, Style

init(autoreset=True)

# Define the logo
logo = r'''
  _   _  _____ _    ___     ________ _   _  __      _______ ______ _______   _____  _    _ _   _  _____ 
 | \ | |/ ____| |  | \\ \\   / /  ____| \\ | | \\ \\    / /_   _|  ____|__   __| |  __ \\| |  | | \\ | |/ ____|
 |  \\| | |  __| |  | |\\ \\_/ /| |__  |  \\| |  \\ \\  / /  | | | |__     | |    | |  | | |  | |  \\| | |  __ 
 | . ` | | |_ | |  | | \\   / |  __| | . ` |   \\ \\/ /   | | |  __|    | |    | |  | | |  | | . ` | | |_ |
 | |\\  | |__| | |__| |  | |  | |____| |\\  |    \\  /   _| |_| |____   | |    | |__| | |__| | |\\  | |__| |
 |_| \\_|\\_____/\\____/   |_|  |______|_| \\_|     \\/   |_____|______|  |_|    |_____/ \\____/|_| \\_|\\_____/                                                                
'''

# Define the message
message = "Downloading and installing libraries..."

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

    print(Fore.YELLOW + Style.BRIGHT + logo)
    print(Fore.CYAN + Style.BRIGHT + message)

    for lib in libraries:
        try:
            print(Fore.CYAN + Style.BRIGHT + f"{{lib}}: checking...", end='')
            sys.stdout.flush()
            time.sleep(0.5)  # Simulate some delay

            # Check if the library is already installed
            result = subprocess.run([sys.executable, "-m", "pip", "show", lib], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if result.returncode == 0:
                print(Fore.GREEN + Style.BRIGHT + " [already installed.]")
            else:
                print(Fore.YELLOW + Style.BRIGHT + " [updating...]", end='')
                sys.stdout.flush()
                # Simulate progress
                for _ in range(3):
                    sys.stdout.write(Fore.YELLOW + Style.BRIGHT + " .")
                    sys.stdout.flush()
                    time.sleep(0.5)
                print(Fore.GREEN + Style.BRIGHT + " [installation complete.]")
                subprocess.check_call([sys.executable, "-m", "pip", "install", lib], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            print(Fore.RED + Style.BRIGHT + f"{{lib}}: error during installation.")
            sys.exit(1)

def close_message():
    print(Fore.CYAN + Style.BRIGHT + "Installation complete.")
    print(Fore.CYAN + Style.BRIGHT + "Press Enter to close this window.")

    # Wait for the user to press Enter to close the window
    input()

if __name__ == "__main__":
    install_requirements()
    close_message()
