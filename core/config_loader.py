import json
import os
from pathlib import Path
from selenium.webdriver.common.by import By

class ConfigLoader:
    """
    Loads website configuration dynamically from JSON files.
    Ensures that locators map to Selenium 'By' strategies.
    """
    
    _config_data = {}
    
    @staticmethod
    def load_config(website_id: str = None):
        """Loads a specific website JSON configuration"""
        base_dir = Path(__file__).resolve().parent.parent
        
        if website_id is None:
            active_run_file = base_dir / "config" / "active_run.json"
            if active_run_file.exists():
                with open(active_run_file, "r") as f:
                    data = json.load(f)
                    website_id = data.get("website_id", "saucedemo")
            else:
                website_id = "saucedemo" # Default
                
        config_path = base_dir / "config" / "websites" / f"{website_id}.json"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found for website: {website_id} at {config_path}")
            
        with open(config_path, 'r', encoding='utf-8') as file:
            ConfigLoader._config_data = json.load(file)
            
    @staticmethod
    def get(key: str, default=None):
        """Gets a top-level key from the config"""
        return ConfigLoader._config_data.get(key, default)
        
    @staticmethod
    def get_locator(page: str, element: str):
        """
        Returns a tuple of (By.<STRATEGY>, "locator_value") dynamically.
        """
        try:
            strategy, value = ConfigLoader._config_data['locators'][page][element]
            
            # Map string to Selenium By attribute dynamically
            strategy = strategy.lower().replace(" ", "_")
            if strategy == "id":
                by = By.ID
            elif strategy == "xpath":
                by = By.XPATH
            elif strategy == "css_selector" or strategy == "css":
                by = By.CSS_SELECTOR
            elif strategy == "class_name":
                by = By.CLASS_NAME
            elif strategy == "name":
                by = By.NAME
            elif strategy == "tag_name":
                by = By.TAG_NAME
            elif strategy == "link_text":
                by = By.LINK_TEXT
            elif strategy == "partial_link_text":
                by = By.PARTIAL_LINK_TEXT
            else:
                raise ValueError(f"Unknown locator strategy: {strategy}")
                
            return (by, value)
        except KeyError as e:
            raise KeyError(f"Locator not found in config: Page='{page}', Element='{element}'") from e

    @staticmethod
    def get_credentials():
        return ConfigLoader._config_data.get('credentials', {})
        
    @staticmethod
    def get_settings():
        return ConfigLoader._config_data.get('settings', {})
