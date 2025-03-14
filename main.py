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
    """Проверка наличия Chromium/Chrome"""
    if platform.system() == 'Windows':
        chrome_paths = [
            os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe")
        ]
    else:  # Linux/Unix
        chrome_paths = [
            '/usr/bin/chromium',
            '/usr/bin/chromium-browser',
            '/usr/bin/google-chrome',
            '/usr/bin/google-chrome-stable'
        ]

    chrome_installed = any(os.path.exists(path) for path in chrome_paths)
    if not chrome_installed:
        print("ВНИМАНИЕ: Chromium/Google Chrome не установлен!")
        print("Установка системных зависимостей...")
        if platform.system() == 'Windows':
            print("Пожалуйста, установите Chrome для работы программы.")
            print("Ссылка для загрузки: https://www.google.com/chrome/")
            sys.exit(1)
        else:
            try:
                # На Linux попробуем установить через пакетный менеджер
                subprocess.check_call(['which', 'chromium'])
            except subprocess.CalledProcessError:
                print("Не удалось найти Chromium. Пожалуйста, установите его вручную.")
                sys.exit(1)

def main():
    try:
        # Проверка зависимостей при запуске
        print("Проверка зависимостей...")
        check_dependencies()
        check_chrome()

        print("Запуск приложения...")
        # Запуск основного приложения
        root = tk.Tk()
        app = ScraperGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"Ошибка при запуске программы: {str(e)}")
        print("Подробности ошибки:", str(sys.exc_info()))
        input("Нажмите Enter для выхода...")
        sys.exit(1)

if __name__ == "__main__":
    main()