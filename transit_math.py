# Transit calculation (stub)
from core_math import calc_natal
from typing import Dict

def calc_transit(date: str, time: str, place: str) -> Dict:
    # For demo: just return current planet positions (should compare to natal)
    return calc_natal(date, time, place)
