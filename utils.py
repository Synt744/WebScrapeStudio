import csv
import pandas as pd
from typing import List
from models import Product

def export_to_csv(products: List[Product], filepath: str):
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'Price', 'Description', 'URL', 'Marketplace', 'Created At'])
        for product in products:
            writer.writerow([
                product.name,
                product.price,
                product.description,
                product.url,
                product.marketplace,
                product.created_at
            ])

def export_to_excel(products: List[Product], filepath: str):
    data = {
        'Name': [p.name for p in products],
        'Price': [p.price for p in products],
        'Description': [p.description for p in products],
        'URL': [p.url for p in products],
        'Marketplace': [p.marketplace for p in products],
        'Created At': [p.created_at for p in products]
    }
    df = pd.DataFrame(data)
    df.to_excel(filepath, index=False)
