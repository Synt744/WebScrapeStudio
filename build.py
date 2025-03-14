
import PyInstaller.__main__
import platform
import os

def build_installer():
    # Общие параметры для всех платформ
    params = [
        'main.py',  # Главный скрипт
        '--name=DesktopScraper',  # Имя приложения
        '--onefile',  # Собрать в один файл
        '--noconsole',  # Без консоли
        '--icon=generated-icon.png',  # Иконка
        # Добавляем все необходимые модули
        '--hidden-import=selenium',
        '--hidden-import=beautifulsoup4',
        '--hidden-import=pandas',
        '--hidden-import=requests',
        '--hidden-import=undetected_chromedriver',
        '--hidden-import=2captcha-python',
        '--add-data=generated-icon.png:.'
    ]
    
    # Запускаем сборку
    PyInstaller.__main__.run(params)

if __name__ == "__main__":
    build_installer()
