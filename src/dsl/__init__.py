"""
DSL (Domain Specific Language) для астрологических формул

Модуль предоставляет язык для формулирования астрологических запросов:
- Логические операторы: AND/OR/NOT (и &&/||/!)
- Проверки свойств: Sun.Sign == Aries
- Аспекты: Asp(Mars, Saturn, Conj)
- Агрегаторы: any(planet).Sign == Leo
- Валидацию астрологической корректности

Пример использования:
    from src.dsl import parse_and_validate, execute_formula
    
    # Проверка валидности формулы
    result = parse_and_validate("Sun.Sign == Aries AND Sun.Dignity == Exaltation")
    
    # Выполнение на карте
    from src.core.chart import Chart
    chart = Chart(...)
    matches = execute_formula(chart, "any(planet).Retrograde == True")
"""

from .validator import (
    AstrologicalValidator,
    ValidationError,
    ValidationWarning,
)

__all__ = [
    'AstrologicalValidator',
    'ValidationError',
    'ValidationWarning',
]

__version__ = '1.0.0-alpha'
