from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Dict, Optional
import tkinter as tk
from tkinter import ttk
import json

class ElementSelector:
    def __init__(self, url: str, driver: Optional[webdriver.Chrome] = None):
        self.url = url
        self.driver = driver
        self.selected_elements = {}
        
    def get_unique_selector(self, element) -> str:
        """Generate a unique CSS selector for the element"""
        # Try ID first
        if element.get_attribute('id'):
            return f"#{element.get_attribute('id')}"
            
        # Try class
        classes = element.get_attribute('class')
        if classes:
            class_selector = '.'.join(classes.split())
            if len(self.driver.find_elements(By.CSS_SELECTOR, f".{class_selector}")) == 1:
                return f".{class_selector}"
                
        # Generate path
        path = []
        current = element
        while current.tag_name != 'html':
            tag = current.tag_name
            siblings = current.find_elements(By.XPATH, f"preceding-sibling::{tag}")
            if siblings:
                tag += f":nth-of-type({len(siblings) + 1})"
            path.insert(0, tag)
            current = current.find_element(By.XPATH, '..')
        return ' > '.join(path)

    def highlight_element(self, element):
        """Highlight selected element on the page"""
        self.driver.execute_script("""
            var element = arguments[0];
            var original_style = element.getAttribute('style');
            element.setAttribute('style', original_style + '; border: 2px solid red; background-color: yellow;');
            setTimeout(function(){
                element.setAttribute('style', original_style);
            }, 2000);
        """, element)

    def select_elements(self) -> Dict[str, str]:
        """Open interactive window for element selection"""
        window = tk.Toplevel()
        window.title("Element Selector")
        window.geometry("400x300")
        
        # Style configuration
        style = ttk.Style()
        style.configure("Select.TButton", 
                       padding=10, 
                       font=('Segoe UI', 10))
        
        # Instructions
        ttk.Label(window, 
                 text="Выберите элементы для парсинга:\n" +
                      "1. Нажмите кнопку для выбора элемента\n" +
                      "2. Кликните по нужному элементу на странице\n" +
                      "3. Подтвердите выбор",
                 justify=tk.LEFT,
                 padding=10).pack(fill='x')
        
        def create_selector_button(field_name: str):
            def select_action():
                window.iconify()  # Minimize selector window
                # Wait for click and get element
                element = WebDriverWait(self.driver, 30).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "body"))
                )
                self.highlight_element(element)
                selector = self.get_unique_selector(element)
                self.selected_elements[field_name] = selector
                # Update button text
                button.configure(text=f"{field_name.title()}: Выбрано")
                window.deiconify()  # Restore selector window
                
            button = ttk.Button(window, 
                              text=f"Выбрать {field_name}", 
                              command=select_action,
                              style="Select.TButton")
            button.pack(pady=5, padx=10, fill='x')
            
        # Create buttons for each field
        for field in ['name', 'price', 'description']:
            create_selector_button(field)
            
        # Finish button
        ttk.Button(window, 
                  text="Завершить выбор", 
                  command=window.destroy,
                  style="Select.TButton").pack(pady=20)
        
        window.wait_window()  # Wait until window is closed
        return self.selected_elements

    def analyze_page(self) -> Dict[str, str]:
        """
        Analyze page and return selectors for important elements
        """
        try:
            return self.select_elements()
        finally:
            if self.driver:
                self.driver.quit()
