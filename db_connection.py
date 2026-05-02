import mysql.connector
import os

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "db_config.txt")

def _read_config(path):
    config = {}
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                config[key.strip()] = value.strip()
    return config

def get_connection():
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(
            f"Config file not found: {CONFIG_FILE}\n"
            "Please create db_config.txt with username, password, database, host, port."
        )
    cfg = _read_config(CONFIG_FILE)
    return mysql.connector.connect(
        host=cfg.get("host", "localhost"),
        port=int(cfg.get("port", 3306)),
        user=cfg["username"],
        password=cfg["password"],
        database=cfg["database"],
    )
