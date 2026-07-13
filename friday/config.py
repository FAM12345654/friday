"""Configuration constants for the local Friday assistant."""

from pathlib import Path


# Der sichtbare Name in der Oberfläche.
APP_NAME = "Friday"
APP_VERSION = "1.0.0"

# Friday läuft in dieser Phase nur lokal auf dem Rechner.
LOCAL_MODE = True

# Externes Senden bleibt absichtlich deaktiviert. Kalender ist die einzige
# bewusst aktivierte Ausnahme und bleibt pro Termin hart gegatet:
# KALENDER AKTIVIEREN + TERMIN SPEICHERN + Haupt-Policy + Verbindungstest.
ENABLE_REAL_EMAIL = False
ENABLE_REAL_WHATSAPP = False
ENABLE_REAL_SMS = False
ENABLE_REAL_CALENDAR = True
ENABLE_REAL_WEATHER = False
ENABLE_REAL_MUSIC = False

# WhatsApp Read-Bridge bleibt getrennt von echtem WhatsApp-Senden.
# Default: aus. Aktivierung braucht ein eigenes Gate.
ENABLE_WHATSAPP_BRIDGE_READ = False

# Microsoft Graph Mail bleibt read-only und getrennt von echtem E-Mail-Senden.
# Vom Nutzer bewusst aktiviert (MAIL LESEN AKTIVIEREN); Konto-Test war erfolgreich.
ENABLE_MS_MAIL_READ = True

# Gmail/IMAP-Mail bleibt read-only und getrennt von echtem E-Mail-Senden.
# Default: aus. Aktivierung braucht MAIL LESEN AKTIVIEREN.
ENABLE_IMAP_MAIL_READ = False
ENABLE_MAIL_ORGANIZE = False

# Jede Aktion braucht eine Nutzerfreigabe im Vorschaumodus.
REQUIRE_USER_APPROVAL = True

# Feste Demo-Daten für die lokale Anzeige.
DEMO_DATE = "2026-07-05"
USE_REAL_TODAY = True

# Speicherstrategie für diese Version: nur lokale SQLite-Daten.
USE_SQLITE_STORAGE = True

# Demo-Modus nutzt eine getrennte Datenbank mit Seed-Daten.
DEMO_MODE = False

# Obsidian bleibt standardmäßig deaktiviert. Writes brauchen ein eigenes Gate.
OBSIDIAN_VAULT_PATH = ""
OBSIDIAN_WRITE_ENABLED = False
OBSIDIAN_ALLOWED_SUBDIR = "Friday"

# Lokale Modelladapter bleiben standardmäßig deaktiviert.
ENABLE_LOCAL_OLLAMA = True
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "qwen3:8b"
OLLAMA_EMBED_MODEL = "nomic-embed-text"
OLLAMA_TIMEOUT_SECONDS = 30

# Lokale Benachrichtigungen bleiben standardmäßig deaktiviert.
ENABLE_LOCAL_NOTIFICATIONS = False

# E-Mail-Versand bleibt deaktiviert, bis der Nutzer spaeter EMAIL AKTIVIEREN nutzt.
EMAIL_DAILY_SEND_LIMIT = 20

PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_DIR.parent

# Nur die Seed-Dateien liegen im Paket.
DATA_DIR = PACKAGE_DIR / "data"

# Die eigentliche Arbeitsdatenbank liegt im Projektordner.
LOCAL_DATA_DIR = PROJECT_ROOT / "local_data"
DATABASE_NAME = "friday.db"
DATABASE_PATH = LOCAL_DATA_DIR / DATABASE_NAME
DEMO_DATABASE_NAME = "friday_demo.db"
DEMO_DATABASE_PATH = LOCAL_DATA_DIR / DEMO_DATABASE_NAME


def get_database_path() -> Path:
    """Return the active local database path for the current mode."""
    if DEMO_MODE:
        return DEMO_DATABASE_PATH
    return DATABASE_PATH
