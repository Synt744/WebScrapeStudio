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

        # Set dark theme
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Using clam as base theme

        # Configure dark theme colors
        self.style.configure(".",
            background="#1e1e1e",
            foreground="#ffffff",
            fieldbackground="#2d2d2d",
            troughcolor="#2d2d2d",
            selectbackground="#007acc",
            selectforeground="#ffffff"
        )

        # Configure specific widget styles
        self.style.configure("TFrame", background="#1e1e1e")
        self.style.configure("TNotebook", background="#1e1e1e", borderwidth=0)
        self.style.configure("TNotebook.Tab",
            background="#2d2d2d",
            foreground="#ffffff",
            padding=[10, 5],
            borderwidth=0
        )
        self.style.map("TNotebook.Tab",
            background=[("selected", "#007acc")],
            foreground=[("selected", "#ffffff")]
        )
        self.style.configure("TButton",
            background="#007acc",
            foreground="#ffffff",
            padding=[10, 5],
            borderwidth=0
        )
        self.style.map("TButton",
            background=[("active", "#0098ff")],
            foreground=[("active", "#ffffff")]
        )

        # Configure root window
        self.root.configure(bg="#1e1e1e")

        self.config_manager = ConfigManager()
        self.captcha_api_key = None
        self.protection_handler = None
        self.create_widgets()

        # Apply transparency
        self.root.attributes('-alpha', 0.95)

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
        # Notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Scraping tab
        scraping_frame = ttk.Frame(notebook)
        notebook.add(scraping_frame, text='Scraping')

        # Configuration section
        title_label = ttk.Label(scraping_frame, text="Marketplace Configuration",
                              font=('Segoe UI', 12, 'bold'))
        title_label.pack(pady=10)

        config_frame = ttk.Frame(scraping_frame)
        config_frame.pack(fill='x', padx=10)

        ttk.Label(config_frame, text="URL Pattern:").pack()
        self.url_pattern = self.create_styled_entry(config_frame)
        self.url_pattern.pack(pady=(0, 10))

        ttk.Label(config_frame, text="URLs (one per line):").pack()
        self.urls_text = self.create_styled_text(config_frame)
        self.urls_text.pack(fill='x', pady=(0, 10))

        # Selectors frame
        selectors_frame = ttk.LabelFrame(scraping_frame, text="Selectors", padding=10)
        selectors_frame.pack(fill='x', padx=10, pady=5)

        self.selector_entries = {}
        for field in ['name', 'price', 'description']:
            ttk.Label(selectors_frame, text=f"{field.title()} Selector:").pack()
            entry = self.create_styled_entry(selectors_frame)
            entry.pack(pady=(0, 10))
            self.selector_entries[field] = entry

        # Options frame
        options_frame = ttk.LabelFrame(scraping_frame, text="Options", padding=10)
        options_frame.pack(fill='x', padx=10, pady=5)

        # Selenium checkbox
        self.use_selenium = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Use Selenium", variable=self.use_selenium).pack(anchor='w')

        # Cloudflare protection
        self.handle_cloudflare = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Handle Cloudflare Protection", 
                       variable=self.handle_cloudflare).pack(anchor='w')

        # CAPTCHA frame
        captcha_frame = ttk.Frame(options_frame)
        captcha_frame.pack(fill='x', pady=5)

        ttk.Label(captcha_frame, text="2Captcha API Key:").pack(anchor='w')
        self.captcha_key_entry = self.create_styled_entry(captcha_frame)
        self.captcha_key_entry.pack(fill='x', pady=(0, 5))

        ttk.Label(captcha_frame, text="Site CAPTCHA Key:").pack(anchor='w')
        self.site_key_entry = self.create_styled_entry(captcha_frame)
        self.site_key_entry.pack(fill='x')


        # Control buttons
        buttons_frame = ttk.Frame(scraping_frame)
        buttons_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(buttons_frame, text="Start Scraping", command=self.start_scraping).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Save Config", command=self.save_config).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Анализ сайта", command=self.analyze_site).pack(side='left', padx=5)

        # Progress bar
        self.progress = ttk.Progressbar(scraping_frame, mode='determinate')
        self.progress.pack(fill='x', padx=10, pady=10)

        # Data tab
        data_frame = ttk.Frame(notebook)
        notebook.add(data_frame, text='Data')

        # Treeview style
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

        # Treeview for data display
        self.tree = ttk.Treeview(data_frame, columns=('Name', 'Price', 'Marketplace', 'Created At'), show='headings')
        self.tree.heading('Name', text='Name')
        self.tree.heading('Price', text='Price')
        self.tree.heading('Marketplace', text='Marketplace')
        self.tree.heading('Created At', text='Created At')
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)

        # Export buttons
        export_frame = ttk.Frame(data_frame)
        export_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(export_frame, text="Export CSV", command=lambda: self.export_data('csv')).pack(side='left', padx=5)
        ttk.Button(export_frame, text="Export Excel", command=lambda: self.export_data('excel')).pack(side='left', padx=5)
        ttk.Button(export_frame, text="Refresh Data", command=self.load_data).pack(side='left', padx=5)

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
        messagebox.showinfo("Success", "Configuration saved successfully!")

    def start_scraping(self):
        urls = self.urls_text.get("1.0", tk.END).strip().split('\n')
        if not urls:
            messagebox.showerror("Error", "Please enter URLs to scrape")
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
                self.root.after(0, lambda: messagebox.showerror("Error", f"Scraping failed: {str(e)}"))
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
        messagebox.showinfo("Success", f"Scraped {count} products successfully!")
        self.load_data()

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
                messagebox.showwarning("Warning", "No data to export")
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
                messagebox.showinfo("Success", f"Data exported to {filename}")

    def analyze_site(self):
        url = self.url_pattern.get()
        if not url:
            messagebox.showerror("Error", "Please enter URL Pattern first")
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

            messagebox.showinfo("Success", "Site analysis completed successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to analyze site: {str(e)}")
        finally:
            if self.protection_handler:
                self.protection_handler.cleanup()
                self.protection_handler = None