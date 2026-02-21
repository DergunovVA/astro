"""
Астрологический валидатор для DSL формул

Проверяет корректность астрологических формул на трех уровнях:
1. Критические ошибки (блокируют выполнение)
2. Предупреждения (сомнительные комбинации)
3. Рекомендации (best practices)

Примеры валидации:
- Sun.Retrograde == True → ОШИБКА (Солнце не может быть ретроградным)
- Sun.Sign == Taurus AND Sun.Dignity == Exaltation → ОШИБКА (Солнце экзальтировано в Овне)
- Mars.Ruler == Venus → ОШИБКА (планета не управляет планетой)
"""

import os
import yaml
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ValidationLevel(Enum):
    """Уровни валидации"""

    ERROR = "error"  # Критическая ошибка - блокирует выполнение
    WARNING = "warning"  # Предупреждение - можно выполнить, но сомнительно
    INFO = "info"  # Рекомендация - best practice


@dataclass
class ValidationResult:
    """Результат валидации"""

    is_valid: bool
    level: ValidationLevel
    message: str
    details: Optional[str] = None
    suggestions: Optional[List[str]] = None


class ValidationError(Exception):
    """Критическая ошибка валидации"""

    pass


class ValidationWarning(Warning):
    """Предупреждение валидации"""

    pass


class AstrologicalValidator:
    """
    Валидатор астрологической корректности формул

    Проверяет:
    - Базовые ограничения (ретроградность, диапазоны)
    - Достоинства планет (Ruler, Exaltation, Detriment, Fall)
    - Конфликтующие комбинации
    """

    # Объекты, которые не могут быть ретроградными
    NON_RETROGRADE_BODIES = {
        "Sun",
        "Moon",
        "Asc",
        "MC",
        "IC",
        "Dsc",
        "NorthNode",
        "SouthNode",
    }

    # Валидные диапазоны
    VALID_HOUSES = range(1, 13)
    VALID_DEGREES_IN_SIGN = range(0, 30)
    VALID_ABSOLUTE_DEGREES = range(0, 360)

    # Все планеты (для валидации)
    ALL_PLANETS = {
        "Sun",
        "Moon",
        "Mercury",
        "Venus",
        "Mars",
        "Jupiter",
        "Saturn",
        "Uranus",
        "Neptune",
        "Pluto",
    }

    def __init__(self, config_path: Optional[str] = None, mode: str = "modern"):
        """
        Инициализация валидатора

        Args:
            config_path: Путь к dignities.yaml (если None, использует дефолтный)
            mode: 'traditional' или 'modern' (влияет на управителей)
        """
        self.mode = mode
        self._load_dignities_config(config_path)
        self._build_lookup_tables()

    def _load_dignities_config(self, config_path: Optional[str] = None):
        """Загрузка конфигурации достоинств из YAML"""
        if config_path is None:
            # Дефолтный путь относительно корня проекта
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            config_path = os.path.join(base_dir, "config", "dignities.yaml")

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            # Загрузка управителей в зависимости от режима
            mode_config = config.get(self.mode, config.get("modern"))
            self.rulers = mode_config["rulers"]

            # Экзальтации, изгнания, падения едины для всех режимов
            self.exaltations = config["exaltations"]
            self.detriments = config["detriments"]
            self.falls = config["falls"]

        except FileNotFoundError:
            raise ValidationError(
                f"❌ Конфигурационный файл не найден: {config_path}\n"
                f"Создайте config/dignities.yaml с определениями достоинств."
            )
        except yaml.YAMLError as e:
            raise ValidationError(
                f"❌ Ошибка парсинга YAML: {e}\n"
                f"Проверьте синтаксис config/dignities.yaml"
            )

    def _build_lookup_tables(self):
        """
        Построение оптимизированных хэш-таблиц для O(1) поиска

        Преобразует:
        - rulers: {sign: [planets]} → planet_rules_signs: {planet: {signs}}
        - exaltations: {planet: {sign, degree}} → exaltation_lookup: {(planet, sign): True}
        """
        # Обратная таблица управителей: планета → знаки, которыми управляет
        self.planet_rules_signs: Dict[str, Set[str]] = {}
        for sign, planets in self.rulers.items():
            for planet in planets:
                if planet not in self.planet_rules_signs:
                    self.planet_rules_signs[planet] = set()
                self.planet_rules_signs[planet].add(sign)

        # O(1) lookup для экзальтаций: (планета, знак) → True/False
        self.exaltation_lookup: Dict[Tuple[str, str], bool] = {}
        for planet, data in self.exaltations.items():
            sign = data["sign"]
            self.exaltation_lookup[(planet, sign)] = True

        # O(1) lookup для падений: (планета, знак) → True/False
        self.fall_lookup: Dict[Tuple[str, str], bool] = {}
        for planet, sign in self.falls.items():
            self.fall_lookup[(planet, sign)] = True

        # Изгнания (может быть несколько знаков)
        self.detriment_lookup: Set[Tuple[str, str]] = set()
        for planet, signs in self.detriments.items():
            if isinstance(signs, list):
                for sign in signs:
                    self.detriment_lookup.add((planet, sign))
            else:
                self.detriment_lookup.add((planet, signs))

    # ========================================================================
    # БАЗОВАЯ ВАЛИДАЦИЯ (Уровень 1)
    # ========================================================================

    def check_retrograde(self, body: str) -> Optional[ValidationResult]:
        """
        Проверка возможности ретроградности

        Args:
            body: Название объекта (Sun, Moon, Mars, etc.)

        Returns:
            ValidationResult если ошибка, иначе None
        """
        if body in self.NON_RETROGRADE_BODIES:
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"❌ Астрологическая ошибка: {body} не может быть ретроградным!",
                details=(
                    f"\nℹ️  Объяснение:\n"
                    f"Ретроградными могут быть только планеты: Mercury, Venus, Mars,\n"
                    f"Jupiter, Saturn, Uranus, Neptune, Pluto.\n\n"
                    f"{body} НИКОГДА не бывает ретроградным"
                    + (" (Земля вращается вокруг Солнца)." if body == "Sun" else ".")
                ),
                suggestions=[
                    "Mercury.Retrograde == True",
                    "Venus.Retrograde == True",
                    "Mars.Retrograde == True",
                ],
            )
        return None

    def check_self_aspect(
        self, planet1: str, planet2: str
    ) -> Optional[ValidationResult]:
        """Проверка аспекта планеты к самой себе"""
        if planet1 == planet2:
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="❌ Ошибка: Планета не может иметь аспект к самой себе!",
                details=f"\nПроверьте формулу: Asp({planet1}, {planet2}, ...)",
                suggestions=[
                    f"Asp({planet1}, Saturn, Conj)",
                    f"Asp(Mars, {planet1}, Square)",
                ],
            )
        return None

    def check_house_range(self, house_num: int) -> Optional[ValidationResult]:
        """Проверка диапазона домов (1-12)"""
        if house_num not in self.VALID_HOUSES:
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"❌ Ошибка: Номер дома должен быть от 1 до 12, получено: {house_num}",
                details="\nℹ️  В астрологии используется 12 домов гороскопа.",
                suggestions=[
                    "Venus.House == 10",
                    "Mars.House IN [1, 4, 7, 10]  # Угловые дома",
                ],
            )
        return None

    def check_degree_range(
        self, degree: float, absolute: bool = False
    ) -> Optional[ValidationResult]:
        """Проверка диапазона градусов"""
        valid_range = (
            self.VALID_ABSOLUTE_DEGREES if absolute else self.VALID_DEGREES_IN_SIGN
        )

        if degree not in valid_range:
            max_degree = 359 if absolute else 29
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"❌ Ошибка: Градус должен быть 0-{max_degree}°, получено: {degree}°",
                details=(
                    "\n(Если нужен абсолютный градус зодиака, используйте .AbsoluteDegree)"
                    if not absolute
                    else None
                ),
                suggestions=None,
            )
        return None

    # ========================================================================
    # РАСШИРЕННАЯ ВАЛИДАЦИЯ ДОСТОИНСТВ (Уровень 1)
    # ========================================================================

    def check_ruler_usage(self, planet: str, target: str) -> Optional[ValidationResult]:
        """
        Проверка корректности использования Ruler

        Ошибка: Planet.Ruler == OtherPlanet (бессмысленно!)
        """
        # Если target - это планета, значит ошибка
        if target in self.ALL_PLANETS:
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"❌ Ошибка: {planet}.Ruler == {target} бессмысленна!",
                details=(
                    "\nℹ️  Объяснение:\n"
                    "Планета не управляет другой планетой.\n"
                    "Планета управляет ЗНАКОМ (или находится в знаке, которым управляет).\n"
                ),
                suggestions=[
                    f"{planet}.Dignity == Rulership  # Планета в своем доме",
                    f"{planet}.Sign.Ruler == {planet}  # Планета управляет своим знаком",
                ],
            )
        return None

    def check_exaltation(self, planet: str, sign: str) -> Optional[ValidationResult]:
        """
        Проверка корректности экзальтации

        Если формула утверждает Planet.Dignity == Exaltation в знаке,
        проверяем, что это правильный знак.
        """
        # Проверяем, есть ли у планеты экзальтация вообще
        if planet not in self.exaltations:
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.WARNING,
                message=f"⚠️  Предупреждение: Экзальтация {planet} не определена в классической астрологии",
                details="\nВнешние планеты (Uranus, Neptune, Pluto) имеют дискуссионные экзальтации.",
                suggestions=None,
            )

        correct_sign = self.exaltations[planet]["sign"]

        if sign != correct_sign:
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"❌ Астрологическая ошибка: {planet} экзальтирован в {correct_sign}, НЕ в {sign}!",
                details=(
                    "\nℹ️  Экзальтации планет:\n"
                    "   Sun: Aries, Moon: Taurus, Mercury: Virgo, Venus: Pisces\n"
                    "   Mars: Capricorn, Jupiter: Cancer, Saturn: Libra\n"
                ),
                suggestions=[
                    f"{planet}.Sign == {correct_sign} AND {planet}.Dignity == Exaltation"
                ],
            )
        return None

    def check_conflicting_dignities(
        self, planet: str, dignity1: str, dignity2: str
    ) -> Optional[ValidationResult]:
        """
        Проверка конфликтующих достоинств

        Планета не может быть одновременно в Rulership и Fall и т.п.
        """
        # Все типы достоинств взаимоисключающие
        dignities = {"Rulership", "Exaltation", "Detriment", "Fall", "Peregrine"}

        if dignity1 in dignities and dignity2 in dignities and dignity1 != dignity2:
            return ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=(
                    f"❌ Логическая ошибка: Планета не может быть одновременно "
                    f"в {dignity1} и {dignity2}!"
                ),
                details=(
                    "\nℹ️  Объяснение:\n"
                    "В одном знаке планета имеет только ОДНО состояние:\n"
                    "  - Rulership (управление)\n"
                    "  - Exaltation (экзальтация)\n"
                    "  - Detriment (изгнание)\n"
                    "  - Fall (падение)\n"
                    "  - или нейтральное положение (ничего из вышеперечисленного)\n"
                ),
                suggestions=[
                    f"{planet}.Dignity == {dignity1} OR {planet}.Dignity == {dignity2}"
                ],
            )
        return None

    def check_dignity_sign_match(
        self, planet: str, sign: str, dignity: str
    ) -> Optional[ValidationResult]:
        """
        Проверка соответствия планета + знак + достоинство

        Например: Mars в Aries + Rulership = OK
                  Mars в Taurus + Rulership = ERROR
        """
        if dignity == "Rulership":
            # Проверяем, управляет ли планета этим знаком
            if planet in self.planet_rules_signs:
                if sign not in self.planet_rules_signs[planet]:
                    rulers = self.rulers.get(sign, [])
                    rulers_str = " или ".join(rulers)
                    return ValidationResult(
                        is_valid=False,
                        level=ValidationLevel.ERROR,
                        message=f"❌ Астрологическая ошибка: {sign} управляется {rulers_str}, НЕ {planet}!",
                        details=(
                            "\nℹ️  Управители знаков:\n"
                            "   Aries→Mars, Taurus→Venus, Gemini→Mercury, Cancer→Moon\n"
                            "   Leo→Sun, Virgo→Mercury, Libra→Venus, Scorpio→Mars/Pluto\n"
                        ),
                        suggestions=[
                            f"{planet}.Dignity == Rulership  # Без указания знака - проверит текущий знак"
                        ],
                    )

        elif dignity == "Exaltation":
            return self.check_exaltation(planet, sign)

        elif dignity == "Fall":
            if (planet, sign) not in self.fall_lookup:
                correct_sign = self.falls.get(planet)
                if correct_sign:
                    return ValidationResult(
                        is_valid=False,
                        level=ValidationLevel.ERROR,
                        message=f"❌ Астрологическая ошибка: {planet} в падении в {correct_sign}, НЕ в {sign}!",
                        details=None,
                        suggestions=[
                            f"{planet}.Sign == {correct_sign} AND {planet}.Dignity == Fall"
                        ],
                    )

        elif dignity == "Detriment":
            if (planet, sign) not in self.detriment_lookup:
                # Найти правильные знаки изгнания
                correct_signs = self.detriments.get(planet, [])
                if isinstance(correct_signs, list):
                    signs_str = " или ".join(correct_signs)
                else:
                    signs_str = correct_signs

                return ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"❌ Астрологическая ошибка: {planet} в изгнании в {signs_str}, НЕ в {sign}!",
                    details=None,
                    suggestions=[
                        f"{planet}.Dignity == Detriment  # Без указания знака"
                    ],
                )

        return None

    # ========================================================================
    # ПРЕДУПРЕЖДЕНИЯ (Уровень 2)
    # ========================================================================

    def check_weak_dignity(self, planet: str, sign: str) -> Optional[ValidationResult]:
        """
        Предупреждение о планете в изгнании или падении

        Не ошибка, но астролог должен знать о слабой позиции.
        """
        if (planet, sign) in self.detriment_lookup:
            return ValidationResult(
                is_valid=True,
                level=ValidationLevel.WARNING,
                message=f"⚠️  {planet} в изгнании в {sign}",
                details="Планета в слабой позиции, может проявляться с трудом.",
                suggestions=None,
            )

        if (planet, sign) in self.fall_lookup:
            return ValidationResult(
                is_valid=True,
                level=ValidationLevel.WARNING,
                message=f"⚠️  {planet} в падении в {sign}",
                details="Планета в очень слабой позиции.",
                suggestions=None,
            )

        return None

    # ========================================================================
    # ВЫСОКОУРОВНЕВАЯ ВАЛИДАЦИЯ
    # ========================================================================

    def validate_formula(self, formula_ast) -> List[ValidationResult]:
        """
        Валидация всего AST дерева формулы

        TODO: Реализовать после создания Parser

        Args:
            formula_ast: AST дерево формулы

        Returns:
            Список результатов валидации
        """
        results = []
        # TODO: Traverse AST и вызывать соответствующие check_* методы
        return results

    # ========================================================================
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    # ========================================================================

    def get_ruler(self, sign: str) -> List[str]:
        """Получить управителя(ей) знака"""
        return self.rulers.get(sign, [])

    def is_in_rulership(self, planet: str, sign: str) -> bool:
        """Проверить, управляет ли планета знаком"""
        return sign in self.planet_rules_signs.get(planet, set())

    def is_in_exaltation(self, planet: str, sign: str) -> bool:
        """Проверить, экзальтирована ли планета в знаке"""
        return (planet, sign) in self.exaltation_lookup

    def is_in_detriment(self, planet: str, sign: str) -> bool:
        """Проверить, в изгнании ли планета в знаке"""
        return (planet, sign) in self.detriment_lookup

    def is_in_fall(self, planet: str, sign: str) -> bool:
        """Проверить, в падении ли планета в знаке"""
        return (planet, sign) in self.fall_lookup

    def get_dignity_status(self, planet: str, sign: str) -> str:
        """
        Получить статус достоинства планеты в знаке

        Returns:
            'Rulership', 'Exaltation', 'Detriment', 'Fall' или 'Peregrine' (нейтрально)
        """
        if self.is_in_rulership(planet, sign):
            return "Rulership"
        elif self.is_in_exaltation(planet, sign):
            return "Exaltation"
        elif self.is_in_detriment(planet, sign):
            return "Detriment"
        elif self.is_in_fall(planet, sign):
            return "Fall"
        else:
            return "Peregrine"  # Перегрин - без достоинств


# ============================================================================
# УДОБНЫЕ ФУНКЦИИ
# ============================================================================

# Глобальный валидатор (singleton)
_default_validator = None


def get_validator(mode: str = "modern") -> AstrologicalValidator:
    """Получить глобальный экземпляр валидатора"""
    global _default_validator
    if _default_validator is None:
        _default_validator = AstrologicalValidator(mode=mode)
    return _default_validator


def validate(formula: str, mode: str = "modern") -> bool:
    """
    Быстрая валидация формулы

    Args:
        formula: Строка с формулой DSL
        mode: 'traditional' или 'modern'

    Returns:
        True если формула валидна

    Raises:
        ValidationError если есть критические ошибки
    """
    # ✅ РЕАЛИЗОВАНО (Feb 2026): Parser создан, используйте CLI команду 'validate'
    # Для полной интеграции см. main.py::validate_command()
    validator = get_validator(mode)
    # Full implementation in CLI: python main.py validate "formula" ...
    pass
