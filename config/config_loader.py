import json
import os

# Percorso del file config.json
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

# Cache interna
_config_cache = None


def load_config():
    """Carica il file config.json in memoria (con caching)."""
    global _config_cache

    if _config_cache is None:
        if not os.path.exists(CONFIG_PATH):
            raise FileNotFoundError(f"config.json non trovato in {CONFIG_PATH}")

        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            _config_cache = json.load(f)

    return _config_cache


def reload_config():
    """Forza il ricaricamento del file JSON (serve dopo modifiche)."""
    global _config_cache
    _config_cache = None
    return load_config()


def save_config():
    """Salva la cache nel file config.json."""
    global _config_cache

    if _config_cache is None:
        return

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(_config_cache, f, indent=4, ensure_ascii=False)


def get_offices():
    """Restituisce la lista degli uffici."""
    config = load_config()
    return config.get("offices", [])


def get_office_by_name(name_or_id):
    """
    Restituisce un ufficio cercando sia per 'name' che per 'id'.
    Compatibile con il tuo JSON reale.
    """
    config = load_config()

    for office in config.get("offices", []):
        if office.get("name") == name_or_id:
            return office
        if office.get("id") == name_or_id:
            return office

    return None


def get_office_by_index(index):
    """Restituisce un ufficio tramite indice."""
    offices = get_offices()
    if 0 <= index < len(offices):
        return offices[index]
    return None


def get_floor(office, floor_name):
    """Restituisce un piano dato un ufficio e il nome del piano."""
    if not office:
        return None

    for floor in office.get("floors", []):
        if floor.get("name") == floor_name:
            return floor

    return None


def get_floor_by_index(office, index):
    """Restituisce un piano tramite indice."""
    if not office:
        return None

    floors = office.get("floors", [])
    if 0 <= index < len(floors):
        return floors[index]

    return None
