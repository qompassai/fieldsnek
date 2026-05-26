"""
config/settings.py — Runtime configuration for OnTrack.

Values are loaded from the environment (.env file or system env).
Wrapped in try/except so Android sandbox doesn't crash on missing .env.
"""

import os
from typing import Final

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass

GOOGLE_MAPS_API_KEY: str = os.getenv('GOOGLE_MAPS_API_KEY', '')
OSRM_BASE_URL: str = os.getenv('OSRM_BASE_URL', 'http://router.project-osrm.org')
ARCGIS_ITEM_ID: str = os.getenv('ARCGIS_ITEM_ID', '')
APP_VERSION: Final[str] = '2.0.0'
APP_NAME: Final[str] = 'OnTrack'
ORG_NAME: Final[str] = 'TDS Telecom'
