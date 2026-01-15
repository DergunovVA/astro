# Solar return calculation (stub)
from core_math import calc_natal
from typing import Dict

def calc_solar(year: int, natal_date: str, natal_time: str, place: str) -> Dict:
    # For demo: just return natal for Jan 1 of given year
    date = f"{year}-01-01"
    return calc_natal(date, natal_time, place)
