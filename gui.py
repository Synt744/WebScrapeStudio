import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from typing import List
from models import ScrapingConfig, Product
from scraper import Scraper
from database import Database
from config import ConfigManager
from utils import export_to_csv, export_to_excel

class ScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Marketplace Scraper")
        self.root.geometry("800x600")
        
        self.config_manager = ConfigManager()
        self.create_widgets()

    def create_widgets(self):
        # Notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(expand=True, fill='both', padx=5, pady=5)

        # Scraping tab
        scraping_frame = ttk.Frame(notebook)
        notebook.add(scraping_frame, text='Scraping')
        
        # Configuration section
        ttk.Label(scraping_frame, text="Marketplace Configuration").pack(pady=5)
        
        config_frame = ttk.Frame(scraping_frame)
        config_frame.pack(fill='x', padx=5)
        
        ttk.Label(config_frame, text="URL Pattern:").pack()
        self.url_pattern = tk.Entry(config_frame, width=50)
        self.url_pattern.pack()
        
        ttk.Label(config_frame, text="URLs (one per line):").pack()
        self.urls_text = tk.Text(config_frame, height=5)
        self.urls_text.pack(fill='x')
        
        # Selectors frame
        selectors_frame = ttk.LabelFrame(scraping_frame, text="Selectors")
        selectors_frame.pack(fill='x', padx=5, pady=5)
        
        self.selector_entries = {}
        for field in ['name', 'price', 'description']:
            ttk.Label(selectors_frame, text=f"{field.title()} Selector:").pack()
            entry = tk.Entry(selectors_frame, width=50)
            entry.pack()
            self.selector_entries[field] = entry
        
        # Options frame
        options_frame = ttk.LabelFrame(scraping_frame, text="Options")
        options_frame.pack(fill='x', padx=5, pady=5)
        
        self.use_selenium = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Use Selenium", variable=self.use_selenium).pack()
        
        # Control buttons
        buttons_frame = ttk.Frame(scraping_frame)
        buttons_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(buttons_frame, text="Start Scraping", command=self.start_scraping).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Save Config", command=self.save_config).pack(side='left', padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(scraping_frame, mode='determinate')
        self.progress.pack(fill='x', padx=5, pady=5)
        
        # Data tab
        data_frame = ttk.Frame(notebook)
        notebook.add(data_frame, text='Data')
        
        # Treeview for data display
        self.tree = ttk.Treeview(data_frame, columns=('Name', 'Price', 'Marketplace', 'Created At'), show='headings')
        self.tree.heading('Name', text='Name')
        self.tree.heading('Price', text='Price')
        self.tree.heading('Marketplace', text='Marketplace')
        self.tree.heading('Created At', text='Created At')
        self.tree.pack(fill='both', expand=True)
        
        # Export buttons
        export_frame = ttk.Frame(data_frame)
        export_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(export_frame, text="Export CSV", command=lambda: self.export_data('csv')).pack(side='left', padx=5)
        ttk.Button(export_frame, text="Export Excel", command=lambda: self.export_data('excel')).pack(side='left', padx=5)
        ttk.Button(export_frame, text="Refresh Data", command=self.load_data).pack(side='left', padx=5)

    def save_config(self):
        name = self.url_pattern.get().split('/')[2]  # Use domain as name
        config = ScrapingConfig(
            url_pattern=self.url_pattern.get(),
            selectors={field: entry.get() for field, entry in self.selector_entries.items()},
            use_selenium=self.use_selenium.get()
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
            use_selenium=self.use_selenium.get()
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
