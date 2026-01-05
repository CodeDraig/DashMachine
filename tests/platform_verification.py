
import sys
import os
sys.path.append(os.getcwd())

from dashmachine.platform import weather, sonarr, radarr
from unittest.mock import MagicMock, patch

def test_weather():
    print("Testing Weather (Open-Meteo)...")
    # Berlin coordinates
    platform = weather.Platform(latitude=52.52, longitude=13.41, temp_unit="c", wind_speed_unit="kmh")
    
    # We perform a real request to Open-Meteo since it requires no auth
    try:
        output = platform.process()
        if "Weather Error" in output:
            print(f"Weather Logic Failed: {output}")
        elif "theme-primary-text" in output:
            print("Weather Success: Generated HTML with data.")
        else:
            print(f"Weather output unexpected: {output[:100]}...")
    except Exception as e:
        print(f"Weather Exception: {e}")

def test_sonarr_structure():
    print("\nTesting Sonarr Structure...")
    # Test v3 default
    platform_v3 = sonarr.Platform(api_key="test", host="localhost", port="8989")
    if platform_v3.sonarr.endpoint == "/api/v3":
        print("Sonarr Default API Version Correct: /api/v3")
    else:
        print(f"Sonarr Default API Version Incorrect: {platform_v3.sonarr.endpoint}")

    # Test custom version
    platform_v1 = sonarr.Platform(api_key="test", host="localhost", port="8989", api_version="v1")
    if platform_v1.sonarr.endpoint == "/api/v1":
        print("Sonarr Custom API Version Correct: /api/v1")
    else:
        print(f"Sonarr Custom API Version Incorrect: {platform_v1.sonarr.endpoint}")

def test_radarr_structure():
    print("\nTesting Radarr Structure...")
    # Test v3 default
    platform_v3 = radarr.Platform(api_key="test", host="localhost", port="7878")
    if platform_v3.radarr.endpoint == "/api/v3":
        print("Radarr Default API Version Correct: /api/v3")
    else:
        print(f"Radarr Default API Version Incorrect: {platform_v3.radarr.endpoint}")

if __name__ == "__main__":
    # Mock render_template_string to just return the string format
    # But wait, platform.process() calls it. 
    # We can rely on flask being importable as we installed it.
    
    # Using a simple mock context for flask app if needed, 
    # but render_template_string usually requires an app context.
    from flask import Flask
    app = Flask(__name__)

    with app.app_context():
        test_weather()
        test_sonarr_structure()
        test_radarr_structure()
        
        # New Integration Tests (Mocked logic)
        from dashmachine.platform import emby, readarr, sabnzbd, homeassistant
        
        print("\nTesting Emby Structure...")
        emby_plat = emby.Platform(host="http://localhost", api_key="key", value_template="test")
        print(f"Emby initialized: {emby_plat.emby.host}")

        print("\nTesting Readarr Structure...")
        readarr_plat = readarr.Platform(host="localhost", api_key="key", value_template="test")
        print(f"Readarr endpoint logic: {readarr_plat.readarr.endpoint}")
        if readarr_plat.readarr.endpoint == "/api/v1":
             print("Readarr Default API OK")

        print("\nTesting SABnzbd Structure...")
        sab_plat = sabnzbd.Platform(host="http://localhost", api_key="key", value_template="test")
        print(f"SABnzbd initialized: {sab_plat.sabnzbd.host}")

        print("\nTesting Home Assistant Structure...")
        ha_plat = homeassistant.Platform(host="http://localhost", token="tok", entity_id="sensor.test", value_template="test")
        print(f"HA Entity ID: {ha_plat.ha.entity_id}")

