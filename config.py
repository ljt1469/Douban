import json
import os

class Config:
    def __init__(self):
        self.load_config()
    
    def load_config(self):
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            self.subscriptions_file = config.get('subscriptions_file')
            self.update_interval = config.get('update_interval', 24 * 60 * 60)  # Default to 24 hours