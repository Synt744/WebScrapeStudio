import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from typing import List
from models import ScrapingConfig, Product
from scraper import Scraper
from database import Database
from config import ConfigManager
from utils import export_to_csv, export_to_excel
from site_analyzer import ElementSelector
from bot_protection import AdvancedProtectionHandler

class ScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Marketplace Scraper")
        self.root.geometry("800x600")

        # Style configuration
        self.setup_styles()

        self.config_manager = ConfigManager()
        self.captcha_api_key = None
        self.protection_handler = None
        self.selector_entries = {}  # Initialize selector_entries
        self.create_widgets()

        # Apply transparency
        self.root.attributes('-alpha', 0.95)

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Configure dark theme colors
        self.style.configure(".",
            background="#1e1e1e",
            foreground="#ffffff",
            fieldbackground="#2d2d2d"
        )

        # Configure button style
        self.style.configure("Custom.TButton",
            background="#007acc",
            foreground="#ffffff",
            padding=[20, 10],
            font=('Segoe UI', 11, 'bold'),
            borderwidth=2,
            relief="raised"
        )
        self.style.map("Custom.TButton",
            background=[("active", "#0098ff")],
            foreground=[("active", "#ffffff")]
        )

        # Configure Treeview style
        self.style.configure("Treeview",
            background="#2d2d2d",
            foreground="#ffffff",
            fieldbackground="#2d2d2d",
            borderwidth=0
        )
        self.style.configure("Treeview.Heading",
            background="#3d3d3d",
            foreground="#ffffff",
            borderwidth=0
        )

    def create_styled_entry(self, parent, width=50):
        entry = tk.Entry(parent, width=width,
                        bg="#2d2d2d",
                        fg="#ffffff",
                        insertbackground="#ffffff",
                        relief="flat",
                        highlightthickness=1,
                        highlightbackground="#3d3d3d",
                        highlightcolor="#007acc")
        return entry

    def create_styled_text(self, parent, height=5):
        text = tk.Text(parent, height=height,
                      bg="#2d2d2d",
                      fg="#ffffff",
                      insertbackground="#ffffff",
                      relief="flat",
                      highlightthickness=1,
                      highlightbackground="#3d3d3d",
                      highlightcolor="#007acc")
        return text

    def create_widgets(self):
        # Main container
        main_container = ttk.Frame(self.root, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)

        # URL Frame
        url_frame = ttk.LabelFrame(main_container, text="Настройки URL", padding="10")
        url_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(url_frame, text="URL Pattern:").pack(anchor=tk.W)
        self.url_pattern = self.create_styled_entry(url_frame)
        self.url_pattern.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(url_frame, text="URLs (по одному на строку):").pack(anchor=tk.W)
        self.urls_text = self.create_styled_text(url_frame)
        self.urls_text.pack(fill=tk.X)

        # Selectors Frame
        selectors_frame = ttk.LabelFrame(main_container, text="Селекторы", padding="10")
        selectors_frame.pack(fill=tk.X, pady=(0, 10))

        # Initialize selector entries
        for field in ['name', 'price', 'description']:
            ttk.Label(selectors_frame, text=f"{field.title()}:").pack(anchor=tk.W)
            entry = self.create_styled_entry(selectors_frame)
            entry.pack(fill=tk.X, pady=(0, 10))
            self.selector_entries[field] = entry

        # Buttons Frame
        buttons_frame = ttk.Frame(main_container)
        buttons_frame.pack(fill=tk.X, pady=20)

        # Create main action buttons with custom style
        self.create_button(buttons_frame, "Начать парсинг", self.start_scraping)
        self.create_button(buttons_frame, "Анализ страницы", self.analyze_site)
        self.create_button(buttons_frame, "Сохранить настройки", self.save_config)

        # Options Frame
        options_frame = ttk.LabelFrame(main_container, text="Дополнительные настройки", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 10))

        # Add checkboxes and other options
        self.use_selenium = tk.BooleanVar()
        self.handle_cloudflare = tk.BooleanVar()

        ttk.Checkbutton(options_frame, text="Использовать Selenium", 
                       variable=self.use_selenium).pack(anchor=tk.W)
        ttk.Checkbutton(options_frame, text="Обход защиты Cloudflare", 
                       variable=self.handle_cloudflare).pack(anchor=tk.W)

        # CAPTCHA Frame
        captcha_frame = ttk.Frame(options_frame)
        captcha_frame.pack(fill=tk.X, pady=5)

        ttk.Label(captcha_frame, text="2Captcha API Key:").pack(anchor=tk.W)
        self.captcha_key_entry = self.create_styled_entry(captcha_frame)
        self.captcha_key_entry.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(captcha_frame, text="Site CAPTCHA Key:").pack(anchor=tk.W)
        self.site_key_entry = self.create_styled_entry(captcha_frame)
        self.site_key_entry.pack(fill=tk.X)

        # Progress bar
        self.progress = ttk.Progressbar(main_container, mode='determinate')
        self.progress.pack(fill=tk.X, pady=10)

        # Data Treeview
        data_frame = ttk.LabelFrame(main_container, text="Собранные данные", padding="10")
        data_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(data_frame, columns=('Name', 'Price', 'Marketplace', 'Created At'), show='headings', style="Treeview")
        self.tree.heading('Name', text='Название')
        self.tree.heading('Price', text='Цена')
        self.tree.heading('Marketplace', text='Площадка')
        self.tree.heading('Created At', text='Дата')
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)

        # Export Frame
        export_frame = ttk.Frame(data_frame)
        export_frame.pack(fill=tk.X)

        self.create_button(export_frame, "Экспорт CSV", lambda: self.export_data('csv'))
        self.create_button(export_frame, "Экспорт Excel", lambda: self.export_data('excel'))
        self.create_button(export_frame, "Обновить", self.load_data)

    def create_button(self, parent, text, command):
        btn = ttk.Button(parent, text=text, command=command, style="Custom.TButton")
        btn.pack(side=tk.LEFT, padx=5)
        return btn

    def save_config(self):
        name = self.url_pattern.get().split('/')[2]  # Use domain as name
        config = ScrapingConfig(
            url_pattern=self.url_pattern.get(),
            selectors={field: entry.get() for field, entry in self.selector_entries.items()},
            use_selenium=self.use_selenium.get(),
            handle_cloudflare=self.handle_cloudflare.get(),
            captcha_api_key=self.captcha_key_entry.get() or None,
            captcha_site_key=self.site_key_entry.get() or None
        )
        self.config_manager.add_marketplace(name, config)
        messagebox.showinfo("Успех", "Конфигурация сохранена!")

    def start_scraping(self):
        urls = self.urls_text.get("1.0", tk.END).strip().split('\n')
        if not urls:
            messagebox.showerror("Ошибка", "Введите URLs для парсинга")
            return

        config = ScrapingConfig(
            url_pattern=self.url_pattern.get(),
            selectors={field: entry.get() for field, entry in self.selector_entries.items()},
            use_selenium=self.use_selenium.get(),
            handle_cloudflare=self.handle_cloudflare.get(),
            captcha_api_key=self.captcha_key_entry.get() or None,
            captcha_site_key=self.site_key_entry.get() or None
        )

        def scrape_thread():
            scraper = Scraper(config)
            try:
                products = scraper.scrape_products(urls, self.update_progress)
                with Database() as db:
                    for product in products:
                        product.save(db.conn)
                self.root.after(0, lambda: self.scraping_complete(len(products)))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Ошибка", f"Ошибка парсинга: {str(e)}"))
            finally:
                self.root.after(0, self.reset_progress)

        threading.Thread(target=scrape_thread, daemon=True).start()

    def update_progress(self, value):
        self.progress['value'] = value
        self.root.update_idletasks()

    def reset_progress(self):
        self.progress['value'] = 0
        self.root.update_idletasks()

    def scraping_complete(self, count):
        messagebox.showinfo("Успех", f"Собрано {count} товаров!")
        self.load_data()

    def analyze_site(self):
        url = self.url_pattern.get()
        if not url:
            messagebox.showerror("Ошибка", "Введите URL Pattern")
            return

        try:
            if not self.protection_handler:
                self.protection_handler = AdvancedProtectionHandler()

            driver = self.protection_handler.init_browser(headless=False)
            analyzer = ElementSelector(url, driver)

            # Load the page
            driver.get(url)

            # Get selectors through visual selection
            selectors = analyzer.analyze_page()

            # Update selector entries
            for field, selector in selectors.items():
                if field in self.selector_entries:
                    self.selector_entries[field].delete(0, tk.END)
                    self.selector_entries[field].insert(0, selector)

            messagebox.showinfo("Успех", "Анализ страницы завершен!")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка анализа страницы: {str(e)}")
        finally:
            if self.protection_handler:
                self.protection_handler.cleanup()
                self.protection_handler = None

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        with Database() as db:
            products = Product.get_all(db.conn)
            for product in products:
                self.tree.insert('', 'end', values=(
                    product.name,
                    f"${product.price:.2f}",
                    product.marketplace,
                    product.created_at.strftime('%Y-%m-%d %H:%M:%S')
                ))

    def export_data(self, format_type):
        with Database() as db:
            products = Product.get_all(db.conn)
            if not products:
                messagebox.showwarning("Внимание", "Нет данных для экспорта")
                return

            filetypes = [('CSV files', '*.csv')] if format_type == 'csv' else [('Excel files', '*.xlsx')]
            filename = filedialog.asksaveasfilename(
                defaultextension=f".{format_type}",
                filetypes=filetypes
            )

            if filename:
                if format_type == 'csv':
                    export_to_csv(products, filename)
                else:
                    export_to_excel(products, filename)
                messagebox.showinfo("Успех", f"Данные экспортированы в {filename}")