import json
from datetime import datetime
import swisseph as swe

# Read JSON data
with open("natal_rehovot.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Получаем метаданные
meta = data["input_metadata"]
lat = meta["coordinates"]["lat"]
lon = meta["coordinates"]["lon"]
utc_str = meta["utc_datetime"]  # Format: 1982-01-08T11:40:00+00:00

# Парсим UTC время
dt = datetime.fromisoformat(utc_str.replace("+00:00", ""))
jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0)

# Вычисляем дома (Плацидус)
cusps, ascmc = swe.houses(jd, lat, lon, b"P")

# ASC = ascmc[0], MC = ascmc[1]
asc_lon = ascmc[0]
mc_lon = ascmc[1]


def lon_to_sign_degree(lon):
    """Конвертирует абсолютную долготу в знак и градусы"""
    signs = [
        "Aries",
        "Taurus",
        "Gemini",
        "Cancer",
        "Leo",
        "Virgo",
        "Libra",
        "Scorpio",
        "Sagittarius",
        "Capricorn",
        "Aquarius",
        "Pisces",
    ]
    sign_idx = int(lon / 30)
    degree = lon % 30
    return signs[sign_idx], degree


print("=== УГЛЫ (РЕХОВОТ) ===")
asc_sign, asc_deg = lon_to_sign_degree(asc_lon)
mc_sign, mc_deg = lon_to_sign_degree(mc_lon)
print(f"ASC: {asc_sign} {asc_deg:.2f}° ({asc_lon:.2f}°)")
print(f"MC:  {mc_sign} {mc_deg:.2f}° ({mc_lon:.2f}°)")

print("\n=== КУСПЫ ДОМОВ ===")
for i, cusp in enumerate(cusps, 1):
    sign, deg = lon_to_sign_degree(cusp)
    print(f"Дом {i:2}: {sign:12} {deg:5.2f}° ({cusp:6.2f}°)")

print("\n=== ПЛАНЕТЫ ===")
for fact in data["facts"]:
    if fact["type"] == "planet_in_sign":
        obj = fact["object"]
        sign = fact["value"]
        lon = fact["details"]["longitude"]
        house = fact["details"].get("house", "?")
        retro = "℞" if fact["details"].get("retrograde") else ""

        # Преобразуем абсолютную долготу в градусы в знаке
        degree_in_sign = lon % 30
        print(f"{obj:12} {sign:12} {degree_in_sign:5.2f}° дом {house:2} {retro}")
