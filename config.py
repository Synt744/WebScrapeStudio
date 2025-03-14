import json
from typing import Dict, Optional
from models import ScrapingConfig

class ConfigManager:
    def __init__(self, config_path: str = 'scraper_config.json'):
        self.config_path = config_path
        self.marketplace_configs: Dict[str, ScrapingConfig] = {}
        self.load_config()

    def load_config(self):
        try:
            with open(self.config_path, 'r') as f:
                data = json.load(f)
                self.marketplace_configs = {
                    name: ScrapingConfig(**config)
                    for name, config in data.items()
                }
        except FileNotFoundError:
            self.marketplace_configs = {}

    def save_config(self):
        data = {
            name: {
                'url_pattern': config.url_pattern,
                'selectors': config.selectors,
                'use_selenium': config.use_selenium,
                'headers': config.headers,
                'proxy': config.proxy
            }
            for name, config in self.marketplace_configs.items()
        }
        with open(self.config_path, 'w') as f:
            json.dump(data, f, indent=4)

    def add_marketplace(self, name: str, config: ScrapingConfig):
        self.marketplace_configs[name] = config
        self.save_config()

    def get_marketplace(self, name: str) -> Optional[ScrapingConfig]:
        return self.marketplace_configs.get(name)
