import json
import os

CONFIG_PATH = "config/config.json"

def load_config():
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError("File di configurazione non trovato: config/config.json")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def get_offices():
    return load_config()["offices"]

def get_office_by_name(name):
    for office in get_offices():
        if office["name"] == name:
            return office
    return None

def get_floor(office, floor_name):
    for floor in office["floors"]:
        if floor["name"] == floor_name:
            return floor
    return None

def save_config():
    """Salva il contenuto attuale del config.json (in memoria) sul file."""
    global _config_cache
    if _config_cache is None:
        return  # niente da salvare
    
    
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(_config_cache, f, indent=4, ensure_ascii=False)
