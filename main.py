import tkinter as tk
from gui import ScraperGUI
import sys
import os
import subprocess
import pkg_resources
import platform

def check_dependencies():
    """Проверка и установка необходимых зависимостей"""
    required = {
        'selenium',
        'beautifulsoup4',
        'pandas',
        'requests',
        'undetected-chromedriver',
        '2captcha-python'
    }

    installed = {pkg.key for pkg in pkg_resources.working_set}
    missing = required - installed

    if missing:
        print("Установка необходимых зависимостей...")
        python = sys.executable
        subprocess.check_call([python, '-m', 'pip', 'install', *missing], stdout=subprocess.DEVNULL)

def check_chrome():
    """Проверка наличия Chrome"""
    if platform.system() == 'Windows':
        chrome_paths = [
            os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe")
        ]
    else:
        chrome_paths = [
            '/usr/bin/google-chrome',
            '/usr/bin/google-chrome-stable',
            '/usr/bin/chrome',
            '/usr/bin/chromium-browser'
        ]

    chrome_installed = any(os.path.exists(path) for path in chrome_paths)
    if not chrome_installed:
        print("ВНИМАНИЕ: Google Chrome не установлен!")
        print("Пожалуйста, установите Chrome для корректной работы программы.")
        print("Ссылка для загрузки: https://www.google.com/chrome/")
        sys.exit(1)

def main():
    try:
        # Проверка зависимостей при запуске
        check_dependencies()
        check_chrome()

        # Запуск основного приложения
        root = tk.Tk()
        app = ScraperGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"Ошибка при запуске программы: {str(e)}")
        input("Нажмите Enter для выхода...")
        sys.exit(1)

if __name__ == "__main__":
    main()