"""
geocoder.py — Address geocoding + current-location detection for FieldSnek.

Backends:
  - Nominatim (free, default)
  - Google Geocoding API (optional, better rural accuracy)

Current location:
  - Desktop: ip-api.com (no perms needed)
  - Android: via Android GPS if PLATFORM == 'android'
"""

import os
import requests

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "fieldsnek-tds/1.0 (matt@aflabs.io)"

try:
    from android.permissions import request_permissions, Permission
    PLATFORM = "android"
except ImportError:
    PLATFORM = "desktop"



def geocode_address_nominatim(addr: str) -> dict:
    """Geocode via OpenStreetMap Nominatim (no API key required)."""
    try:
        resp = requests.get(
            NOMINATIM_URL,
            params={"q": addr, "format": "json", "limit": 1},
            headers={"User-Agent": USER_AGENT},
            timeout=10,
        )
        resp.raise_for_status()
        results = resp.json()
        if results:
            return {
                "address": addr,
                "lat": float(results[0]["lat"]),
                "lng": float(results[0]["lon"]),
            }
    except Exception:
        pass
    return {"address": addr, "lat": None, "lng": None}

def geocode_address_google(addr: str, api_key: str) -> dict:
    resp = requests.get(
        "https://maps.googleapis.com/maps/api/geocode/json",
        params={"address": addr, "key": api_key},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    if data["status"] == "OK":
        loc = data["results"][0]["geometry"]["location"]
        return {"address": addr, "lat": loc["lat"], "lng": loc["lng"]}
    return {"address": addr, "lat": None, "lng": None}

def geocode_addresses(
    addresses: list[str],
    use_google: bool = False,
    google_api_key: str | None = None,
    progress_callback=None,
) -> list[dict]:
    """
    Convert a list of address strings to lat/lng dicts.

    Args:
        addresses:         List of address strings.
        use_google:        Use Google Geocoding API instead of Nominatim.
        google_api_key:    Required when use_google=True.
        progress_callback: Optional callable(done, total) for UI progress bars.

    Returns:
        List of {"address": str, "lat": float|None, "lng": float|None}
    """
    results = []
    key = google_api_key or os.getenv("GOOGLE_MAPS_API_KEY", "")
    for i, addr in enumerate(addresses):
        if use_google and key:
            result = geocode_address_google(addr, key)
        else:
            result = geocode_address_nominatim(addr)
        results.append(result)
        if progress_callback:
            progress_callback(i + 1, len(addresses))
    return results



def get_current_location() -> dict | None:
    """
    Return the device's current location as {"lat": float, "lng": float, "address": "Current Location"}.
    On Android uses GPS; on desktop falls back to IP geolocation.
    Returns None if location cannot be determined.
    """
    if PLATFORM == "android":
        return _android_location()
    return _ip_location()

def _ip_location() -> dict | None:
    """Coarse location via IP (desktop fallback, no API key needed)."""
    try:
        resp = requests.get("http://ip-api.com/json/?fields=lat,lon,status", timeout=5)
        data = resp.json()
        if data.get("status") == "success":
            return {"address": "Current Location", "lat": data["lat"], "lng": data["lon"]}
    except Exception:
        pass
    return None

def _android_location() -> dict | None:
    """GPS location on Android via plyer."""
    try:
        from plyer import gps

        from jnius import autoclass
        Context = autoclass("android.content.Context")
        LocationManager = autoclass("android.location.LocationManager")
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        activity = PythonActivity.mActivity
        lm = activity.getSystemService(Context.LOCATION_SERVICE)
        loc = lm.getLastKnownLocation(LocationManager.GPS_PROVIDER)
        if loc is None:
            loc = lm.getLastKnownLocation(LocationManager.NETWORK_PROVIDER)
        if loc:
            return {"address": "Current Location", "lat": loc.getLatitude(), "lng": loc.getLongitude()}
    except Exception:
        pass

    return _ip_location()
