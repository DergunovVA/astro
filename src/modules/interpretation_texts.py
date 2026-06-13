"""
Interpretive text blocks for astrological analysis.

Structured descriptions for planets in signs, aspects, dignities,
house placements, and predictive techniques (Russian + English).

All functions return dict with keys:
  - "ru": Russian interpretation
  - "en": English interpretation
  - "keywords": list[str]
"""

from __future__ import annotations
from typing import Dict, List, Any, Optional

# ─────────────────────────────────────────────────────────────────────────────
# PLANETS IN SIGNS — concise interpretations
# ─────────────────────────────────────────────────────────────────────────────

_PLANET_IN_SIGN: Dict[str, Dict[str, Dict]] = {
    "Sun": {
        "Aries":       {"ru": "Солнце в Овне: сильная воля, пионерский дух, импульсивность, жажда лидерства.", "en": "Sun in Aries: strong will, pioneering spirit, impulsive energy, desire to lead.", "keywords": ["leadership", "courage", "initiative", "impulsiveness"]},
        "Taurus":      {"ru": "Солнце в Тельце: упорство, практичность, чувственность, стабильность.", "en": "Sun in Taurus: perseverance, practicality, sensuality, stability.", "keywords": ["patience", "determination", "materialism", "reliability"]},
        "Gemini":      {"ru": "Солнце в Близнецах: любопытство, гибкость ума, многогранность, коммуникабельность.", "en": "Sun in Gemini: curiosity, mental agility, versatility, communicativeness.", "keywords": ["wit", "versatility", "communication", "duality"]},
        "Cancer":      {"ru": "Солнце в Раке: эмоциональная глубина, привязанность к дому, интуиция, защитный инстинкт.", "en": "Sun in Cancer: emotional depth, attachment to home, intuition, nurturing instinct.", "keywords": ["nurturing", "sensitivity", "family", "intuition"]},
        "Leo":         {"ru": "Солнце в Льве: творческая сила, щедрость, стремление к признанию, харизма.", "en": "Sun in Leo: creative power, generosity, desire for recognition, charisma.", "keywords": ["creativity", "pride", "generosity", "self-expression"]},
        "Virgo":       {"ru": "Солнце в Деве: аналитический ум, внимание к деталям, практическое служение, самосовершенствование.", "en": "Sun in Virgo: analytical mind, attention to detail, practical service, self-improvement.", "keywords": ["analysis", "precision", "service", "health"]},
        "Libra":       {"ru": "Солнце в Весах: дипломатичность, стремление к гармонии, партнёрство, эстетическое чутьё.", "en": "Sun in Libra: diplomacy, striving for harmony, partnership, aesthetic sensitivity.", "keywords": ["balance", "fairness", "partnership", "beauty"]},
        "Scorpio":     {"ru": "Солнце в Скорпионе: глубина, интенсивность, трансформация, скрытая сила.", "en": "Sun in Scorpio: depth, intensity, transformation, hidden power.", "keywords": ["transformation", "intensity", "secrets", "power"]},
        "Sagittarius": {"ru": "Солнце в Стрельце: оптимизм, широкий кругозор, философия, стремление к свободе.", "en": "Sun in Sagittarius: optimism, broad outlook, philosophy, love of freedom.", "keywords": ["optimism", "philosophy", "exploration", "freedom"]},
        "Capricorn":   {"ru": "Солнце в Козероге: амбиции, дисциплина, ответственность, долгосрочное планирование.", "en": "Sun in Capricorn: ambition, discipline, responsibility, long-term planning.", "keywords": ["ambition", "discipline", "structure", "authority"]},
        "Aquarius":    {"ru": "Солнце в Водолее: оригинальность, гуманизм, независимость мышления, реформаторский дух.", "en": "Sun in Aquarius: originality, humanitarianism, independent thinking, reformist spirit.", "keywords": ["innovation", "independence", "humanitarianism", "uniqueness"]},
        "Pisces":      {"ru": "Солнце в Рыбах: сострадание, интуиция, творческое воображение, духовное стремление.", "en": "Sun in Pisces: compassion, intuition, creative imagination, spiritual yearning.", "keywords": ["compassion", "intuition", "spirituality", "imagination"]},
    },
    "Moon": {
        "Aries":       {"ru": "Луна в Овне: быстрые эмоции, реактивность, импульсивные чувства, эмоциональная смелость.", "en": "Moon in Aries: quick emotions, reactivity, impulsive feelings, emotional boldness.", "keywords": ["impulsive", "reactive", "emotional courage"]},
        "Taurus":      {"ru": "Луна в Тельце: эмоциональная стабильность, потребность в уюте, чувственность, постоянство.", "en": "Moon in Taurus: emotional stability, need for comfort, sensuality, constancy.", "keywords": ["comfort", "stability", "sensuality", "loyalty"]},
        "Gemini":      {"ru": "Луна в Близнецах: переменчивые настроения, общительность, эмоциональная любознательность.", "en": "Moon in Gemini: changeable moods, sociability, emotional curiosity.", "keywords": ["adaptability", "communication", "restlessness"]},
        "Cancer":      {"ru": "Луна в Раке (экзальтация): глубокая эмпатия, мощная интуиция, привязанность к семье.", "en": "Moon in Cancer (domicile): deep empathy, powerful intuition, family attachment.", "keywords": ["empathy", "nurturing", "intuition", "home"]},
        "Leo":         {"ru": "Луна во Льве: тёплые чувства, потребность в признании, эмоциональная щедрость.", "en": "Moon in Leo: warm feelings, need for appreciation, emotional generosity.", "keywords": ["warmth", "drama", "generosity", "pride"]},
        "Virgo":       {"ru": "Луна в Деве: аналитические чувства, тревога за здоровье, желание быть полезным.", "en": "Moon in Virgo: analytical feelings, health anxiety, desire to be useful.", "keywords": ["worry", "helpfulness", "criticism", "order"]},
        "Libra":       {"ru": "Луна в Весах: потребность в гармонии, эмоциональная дипломатия, страх конфликтов.", "en": "Moon in Libra: need for harmony, emotional diplomacy, conflict avoidance.", "keywords": ["harmony", "diplomacy", "indecision", "beauty"]},
        "Scorpio":     {"ru": "Луна в Скорпионе (падение): интенсивные эмоции, ревность, глубокое чувствование.", "en": "Moon in Scorpio (fall): intense emotions, jealousy, deep feeling.", "keywords": ["intensity", "jealousy", "depth", "transformation"]},
        "Sagittarius": {"ru": "Луна в Стрельце: оптимистичные эмоции, жажда приключений, широкие взгляды.", "en": "Moon in Sagittarius: optimistic emotions, adventurous spirit, broad outlook.", "keywords": ["optimism", "adventure", "restlessness", "faith"]},
        "Capricorn":   {"ru": "Луна в Козероге (изгнание): сдержанность чувств, практичность, эмоциональная ответственность.", "en": "Moon in Capricorn (detriment): emotional restraint, practicality, emotional responsibility.", "keywords": ["restraint", "discipline", "ambition", "reserve"]},
        "Aquarius":    {"ru": "Луна в Водолее: независимость чувств, дружественность, отстранённость.", "en": "Moon in Aquarius: emotional independence, friendliness, detachment.", "keywords": ["detachment", "friendship", "originality", "humanitarian"]},
        "Pisces":      {"ru": "Луна в Рыбах: растворение в эмоциях, мечтательность, сильная эмпатия.", "en": "Moon in Pisces: emotional dissolution, dreaminess, strong empathy.", "keywords": ["empathy", "sensitivity", "fantasy", "compassion"]},
    },
    "Mercury": {
        "Aries":       {"ru": "Меркурий в Овне: быстрые решения, прямолинейное мышление, смелые идеи.", "en": "Mercury in Aries: quick decisions, direct thinking, bold ideas.", "keywords": ["speed", "directness", "initiative"]},
        "Gemini":      {"ru": "Меркурий в Близнецах (домициль): острый ум, многозадачность, коммуникативный талант.", "en": "Mercury in Gemini (domicile): sharp mind, multitasking, communicative talent.", "keywords": ["agility", "wit", "communication"]},
        "Virgo":       {"ru": "Меркурий в Деве (домициль/экзальтация): аналитическая точность, критическое мышление.", "en": "Mercury in Virgo (domicile/exaltation): analytical precision, critical thinking.", "keywords": ["analysis", "precision", "criticism"]},
        "Sagittarius": {"ru": "Меркурий в Стрельце (изгнание): широкие концепции, философское мышление, преувеличение.", "en": "Mercury in Sagittarius (detriment): broad concepts, philosophical thinking, exaggeration.", "keywords": ["philosophy", "generalization", "exaggeration"]},
        "Pisces":      {"ru": "Меркурий в Рыбах (изгнание/падение): интуитивный ум, образное мышление, размытые границы.", "en": "Mercury in Pisces (detriment/fall): intuitive mind, imaginative thinking, blurred boundaries.", "keywords": ["intuition", "imagination", "vagueness"]},
    },
    "Venus": {
        "Taurus":      {"ru": "Венера в Тельце (домициль): чувственность, красота, материальные радости.", "en": "Venus in Taurus (domicile): sensuality, beauty, material pleasures.", "keywords": ["sensuality", "beauty", "pleasure"]},
        "Libra":       {"ru": "Венера в Весах (домициль): изящество, дипломатия, стремление к гармонии.", "en": "Venus in Libra (domicile): grace, diplomacy, desire for harmony.", "keywords": ["grace", "harmony", "partnership"]},
        "Pisces":      {"ru": "Венера в Рыбах (экзальтация): идеалистическая любовь, сострадание, жертвенность.", "en": "Venus in Pisces (exaltation): idealistic love, compassion, self-sacrifice.", "keywords": ["idealism", "compassion", "romance"]},
        "Aries":       {"ru": "Венера в Овне (изгнание): страстная, импульсивная любовь, эгоцентризм в отношениях.", "en": "Venus in Aries (detriment): passionate impulsive love, egocentric in relationships.", "keywords": ["passion", "impulsiveness", "independence"]},
        "Scorpio":     {"ru": "Венера в Скорпионе (изгнание): интенсивность, ревность, трансформирующие отношения.", "en": "Venus in Scorpio (detriment): intensity, jealousy, transformative relationships.", "keywords": ["intensity", "jealousy", "depth"]},
        "Virgo":       {"ru": "Венера в Деве (падение): критичность в любви, практичная привязанность, скромность.", "en": "Venus in Virgo (fall): critical in love, practical affection, modesty.", "keywords": ["practicality", "criticism", "service"]},
    },
    "Mars": {
        "Aries":       {"ru": "Марс в Овне (домициль): первичная сила, смелость, решительность, первопроходец.", "en": "Mars in Aries (domicile): primal force, courage, decisiveness, pioneer.", "keywords": ["strength", "courage", "initiative"]},
        "Scorpio":     {"ru": "Марс в Скорпионе (домициль традиц.): скрытая сила, стратегическая воля, трансформация.", "en": "Mars in Scorpio (trad. domicile): hidden strength, strategic will, transformation.", "keywords": ["strategy", "depth", "intensity"]},
        "Capricorn":   {"ru": "Марс в Козероге (экзальтация): дисциплинированная энергия, целеустремлённость, эффективность.", "en": "Mars in Capricorn (exaltation): disciplined energy, goal-directed, efficiency.", "keywords": ["discipline", "ambition", "efficiency"]},
        "Libra":       {"ru": "Марс в Весах (изгнание): нерешительность в действиях, дипломатичный конфликт.", "en": "Mars in Libra (detriment): indecisive action, diplomatic conflict.", "keywords": ["indecision", "diplomacy", "conflict"]},
        "Cancer":      {"ru": "Марс в Раке (падение): эмоциональная агрессия, защитная реакция, непрямые действия.", "en": "Mars in Cancer (fall): emotional aggression, defensive reactions, indirect action.", "keywords": ["defensiveness", "emotional action", "protection"]},
    },
    "Jupiter": {
        "Sagittarius": {"ru": "Юпитер в Стрельце (домициль): широкая удача, философская мудрость, экспансия.", "en": "Jupiter in Sagittarius (domicile): broad fortune, philosophical wisdom, expansion.", "keywords": ["wisdom", "expansion", "optimism"]},
        "Pisces":      {"ru": "Юпитер в Рыбах (домициль традиц.): духовная щедрость, сострадание, интуитивная мудрость.", "en": "Jupiter in Pisces (trad. domicile): spiritual generosity, compassion, intuitive wisdom.", "keywords": ["spirituality", "generosity", "faith"]},
        "Cancer":      {"ru": "Юпитер в Раке (экзальтация): плодородная удача, поддержка семьи, эмоциональное изобилие.", "en": "Jupiter in Cancer (exaltation): fertile fortune, family support, emotional abundance.", "keywords": ["abundance", "nurturing", "protection"]},
        "Gemini":      {"ru": "Юпитер в Близнецах (изгнание): рассеянная удача, широкое, но поверхностное мышление.", "en": "Jupiter in Gemini (detriment): scattered fortune, broad but superficial thinking.", "keywords": ["versatility", "scattered focus", "curiosity"]},
    },
    "Saturn": {
        "Capricorn":   {"ru": "Сатурн в Козероге (домициль): полная власть структуры, ответственность, карьерный рост.", "en": "Saturn in Capricorn (domicile): full power of structure, responsibility, career achievement.", "keywords": ["discipline", "ambition", "mastery"]},
        "Aquarius":    {"ru": "Сатурн в Водолее (домициль традиц.): социальная ответственность, реформы через структуру.", "en": "Saturn in Aquarius (trad. domicile): social responsibility, reforms through structure.", "keywords": ["social order", "reform", "discipline"]},
        "Libra":       {"ru": "Сатурн в Весах (экзальтация): зрелая справедливость, стабильные партнёрства.", "en": "Saturn in Libra (exaltation): mature justice, stable partnerships.", "keywords": ["justice", "maturity", "partnership"]},
        "Aries":       {"ru": "Сатурн в Овне (падение): ограниченная инициатива, страх конфликта, заблокированная энергия.", "en": "Saturn in Aries (fall): limited initiative, fear of conflict, blocked energy.", "keywords": ["restriction", "inhibition", "delayed action"]},
        "Cancer":      {"ru": "Сатурн в Раке (изгнание): холодность в семье, ограниченное эмоциональное выражение.", "en": "Saturn in Cancer (detriment): coldness in family, limited emotional expression.", "keywords": ["emotional restriction", "duty over feeling", "distance"]},
    },
}

# For signs not explicitly listed, provide generic text
_GENERIC_PLANET_SIGN = {
    "ru": "{planet} в {sign}: позиция требует индивидуального анализа.",
    "en": "{planet} in {sign}: position requires individual analysis.",
    "keywords": [],
}


def planet_in_sign_text(planet: str, sign: str) -> Dict[str, Any]:
    """Return interpretation text for a planet in a sign.

    Returns:
        {"ru": str, "en": str, "keywords": list[str]}
    """
    return _PLANET_IN_SIGN.get(planet, {}).get(sign, {
        "ru": f"{planet} в {sign}: позиция требует индивидуального анализа.",
        "en": f"{planet} in {sign}: position requires individual analysis.",
        "keywords": [],
    })


# ─────────────────────────────────────────────────────────────────────────────
# ASPECTS — interpretations for planetary pairs
# ─────────────────────────────────────────────────────────────────────────────

_ASPECT_MEANINGS: Dict[str, Dict] = {
    "Conjunction": {
        "ru": "Соединение: слияние энергий двух планет. Интенсивная концентрация, начало нового цикла.",
        "en": "Conjunction: merging of two planetary energies. Intense focus, beginning of a new cycle.",
        "nature": "variable", "keywords": ["fusion", "beginning", "intensity"],
    },
    "Opposition": {
        "ru": "Оппозиция: противостояние, поляризация. Осознание через другого, необходимость баланса.",
        "en": "Opposition: confrontation, polarization. Awareness through others, need for balance.",
        "nature": "challenging", "keywords": ["tension", "awareness", "balance"],
    },
    "Trine": {
        "ru": "Трин: гармоничный поток, природный талант, лёгкость реализации.",
        "en": "Trine: harmonious flow, natural talent, ease of expression.",
        "nature": "harmonious", "keywords": ["ease", "talent", "flow"],
    },
    "Square": {
        "ru": "Квадрат: фрикция, давление, мотивация к росту через конфликт.",
        "en": "Square: friction, pressure, motivation to grow through conflict.",
        "nature": "challenging", "keywords": ["friction", "growth", "challenge"],
    },
    "Sextile": {
        "ru": "Секстиль: благоприятные возможности, сотрудничество, творческий потенциал.",
        "en": "Sextile: favourable opportunities, cooperation, creative potential.",
        "nature": "harmonious", "keywords": ["opportunity", "cooperation", "potential"],
    },
    "Quincunx": {
        "ru": "Квинконс (несекстиль): несовместимость, требующая адаптации; скрытое напряжение.",
        "en": "Quincunx (inconjunct): incompatibility requiring adjustment; hidden tension.",
        "nature": "challenging", "keywords": ["adjustment", "irritation", "tension"],
    },
    "Semi-sextile": {
        "ru": "Полусекстиль: слабое напряжение, требует небольшой коррекции.",
        "en": "Semi-sextile: minor tension requiring slight adjustment.",
        "nature": "minor", "keywords": ["minor tension", "adjustment"],
    },
    "Semi-square": {
        "ru": "Полуквадрат: раздражение, небольшое препятствие, требует внимания.",
        "en": "Semi-square: irritation, minor obstacle requiring attention.",
        "nature": "minor challenging", "keywords": ["minor friction", "irritation"],
    },
    "Sesquiquadrate": {
        "ru": "Полутораквадрат: внутренняя агитация, разочарование, поиск выхода.",
        "en": "Sesquiquadrate: inner agitation, frustration, seeking an outlet.",
        "nature": "minor challenging", "keywords": ["agitation", "frustration"],
    },
    "Quintile": {
        "ru": "Квинтиль (5-я гармоника): творческий дар, уникальный талант.",
        "en": "Quintile (5th harmonic): creative gift, unique talent.",
        "nature": "special", "keywords": ["creativity", "talent", "gift"],
    },
    "Biquintile": {
        "ru": "Биквинтиль: реализация творческого потенциала через опыт.",
        "en": "Biquintile: creative potential realized through experience.",
        "nature": "special", "keywords": ["creativity", "experience"],
    },
    "Septile": {
        "ru": "Септиль (7-я гармоника): кармические связи, судьбоносные встречи.",
        "en": "Septile (7th harmonic): karmic ties, fateful encounters.",
        "nature": "special", "keywords": ["karma", "fate", "spirituality"],
    },
}


def aspect_text(aspect_name: str) -> Dict[str, Any]:
    """Return interpretation text for an aspect type."""
    return _ASPECT_MEANINGS.get(aspect_name, {
        "ru": f"Аспект {aspect_name}: требует индивидуального анализа.",
        "en": f"Aspect {aspect_name}: requires individual analysis.",
        "nature": "unknown", "keywords": [],
    })


# ─────────────────────────────────────────────────────────────────────────────
# ESSENTIAL DIGNITY LEVELS
# ─────────────────────────────────────────────────────────────────────────────

_DIGNITY_TEXTS: Dict[str, Dict] = {
    "Domicile": {
        "ru": "Домициль: планета у себя дома — максимальная сила, чистое выражение природы.",
        "en": "Domicile: planet in its home sign — maximum strength, pure expression of nature.",
        "score_hint": "+5", "keywords": ["strength", "power", "natural expression"],
    },
    "Exaltation": {
        "ru": "Экзальтация: планета возвышена — особая сила и блеск, превосходные результаты.",
        "en": "Exaltation: planet is elevated — special power and brilliance, excellent outcomes.",
        "score_hint": "+4", "keywords": ["brilliance", "excellence", "elevated"],
    },
    "Triplicity": {
        "ru": "Триплицитет: планета в согласии со стихией — поддержка окружения.",
        "en": "Triplicity: planet in harmony with its element — support from surroundings.",
        "score_hint": "+3", "keywords": ["support", "harmony", "element"],
    },
    "Term": {
        "ru": "Термы: планета в своих терминах — умеренная поддержка.",
        "en": "Term: planet within its terms — moderate support.",
        "score_hint": "+2", "keywords": ["moderate strength", "terms"],
    },
    "Face": {
        "ru": "Лицо (декан): планета в своём декане — слабая, но реальная сила.",
        "en": "Face (decan): planet in its face — weak but real dignity.",
        "score_hint": "+1", "keywords": ["weak dignity", "decan"],
    },
    "Peregrine": {
        "ru": "Перегрин (странник): планета без существенного достоинства — слабая поддержка.",
        "en": "Peregrine (wanderer): planet without essential dignity — little support.",
        "score_hint": "-5", "keywords": ["weakness", "wandering", "no support"],
    },
    "Detriment": {
        "ru": "Изгнание (детримент): планета ослаблена — затруднённое выражение.",
        "en": "Detriment: planet weakened — expression is hampered.",
        "score_hint": "-5", "keywords": ["weakness", "difficulty", "restraint"],
    },
    "Fall": {
        "ru": "Падение: планета в наиболее слабой позиции — качества подавлены.",
        "en": "Fall: planet in its weakest position — qualities are suppressed.",
        "score_hint": "-4", "keywords": ["suppression", "difficulty", "weakness"],
    },
    "Neutral": {
        "ru": "Нейтральная позиция: нет особых достоинств или слабостей.",
        "en": "Neutral position: no special dignities or debilities.",
        "score_hint": "0", "keywords": ["neutral", "average"],
    },
}


def dignity_level_text(dignity_level: str) -> Dict[str, Any]:
    """Return text for an essential dignity level."""
    return _DIGNITY_TEXTS.get(dignity_level, {
        "ru": f"Состояние '{dignity_level}': аналитическая оценка.",
        "en": f"Dignity '{dignity_level}': analytical assessment.",
        "score_hint": "?", "keywords": [],
    })


# ─────────────────────────────────────────────────────────────────────────────
# ACCIDENTAL DIGNITIES — Cazimi, Combust, Hayz, etc.
# ─────────────────────────────────────────────────────────────────────────────

_SOLAR_CONDITION_TEXTS: Dict[str, Dict] = {
    "cazimi": {
        "ru": "Казими: планета в сердце Солнца (±17') — сильнейшее случайное достоинство (+5).",
        "en": "Cazimi: planet in the heart of the Sun (±17') — strongest accidental dignity (+5).",
        "keywords": ["cazimi", "heart of sun", "very strong"],
    },
    "combust": {
        "ru": "Сожжённая: планета в пределах 8° от Солнца — значительно ослаблена (-5).",
        "en": "Combust: planet within 8° of the Sun — significantly weakened (-5).",
        "keywords": ["combust", "weakened", "sun proximity"],
    },
    "under_beams": {
        "ru": "Под лучами: планета в пределах 17° от Солнца — частично ослаблена (-4).",
        "en": "Under the Beams: planet within 17° of the Sun — partially weakened (-4).",
        "keywords": ["under beams", "weakened", "sun proximity"],
    },
    "free": {
        "ru": "Свободна от лучей Солнца — нет солярного ослабления.",
        "en": "Free from the Sun's beams — no solar debility.",
        "keywords": ["free", "unaffected"],
    },
}


def solar_condition_text(condition: str) -> Dict[str, Any]:
    """Return text for Cazimi/Combust/Under Beams/Free condition."""
    return _SOLAR_CONDITION_TEXTS.get(condition, {
        "ru": f"Состояние '{condition}' относительно Солнца.",
        "en": f"Solar condition '{condition}'.",
        "keywords": [],
    })


# ─────────────────────────────────────────────────────────────────────────────
# HOUSE MEANINGS
# ─────────────────────────────────────────────────────────────────────────────

_HOUSE_TEXTS: Dict[int, Dict] = {
    1:  {"ru": "1-й дом (Асцендент): личность, тело, внешность, начало жизни.", "en": "1st house (Ascendant): personality, body, appearance, life beginnings.", "keywords": ["self", "identity", "body", "appearance"]},
    2:  {"ru": "2-й дом: ресурсы, деньги, ценности, материальная безопасность.", "en": "2nd house: resources, money, values, material security.", "keywords": ["money", "values", "resources", "security"]},
    3:  {"ru": "3-й дом: коммуникация, братья/сёстры, короткие поездки, обучение.", "en": "3rd house: communication, siblings, short trips, learning.", "keywords": ["communication", "siblings", "travel", "learning"]},
    4:  {"ru": "4-й дом (IC): дом, семья, корни, конец жизни.", "en": "4th house (IC): home, family, roots, end of life.", "keywords": ["home", "family", "roots", "origins"]},
    5:  {"ru": "5-й дом: творчество, дети, романтика, удовольствия, игра.", "en": "5th house: creativity, children, romance, pleasures, play.", "keywords": ["creativity", "children", "romance", "fun"]},
    6:  {"ru": "6-й дом: здоровье, работа, служение, болезни, распорядок дня.", "en": "6th house: health, work, service, illness, daily routine.", "keywords": ["health", "work", "service", "routine"]},
    7:  {"ru": "7-й дом (Десцендент): партнёрство, брак, открытые враги, договоры.", "en": "7th house (Descendant): partnership, marriage, open enemies, contracts.", "keywords": ["partnership", "marriage", "others", "contracts"]},
    8:  {"ru": "8-й дом: смерть, трансформация, наследство, чужие ресурсы, тайное.", "en": "8th house: death, transformation, inheritance, shared resources, secrets.", "keywords": ["death", "transformation", "secrets", "shared resources"]},
    9:  {"ru": "9-й дом: путешествия, высшее образование, философия, иностранное.", "en": "9th house: travel, higher education, philosophy, foreign affairs.", "keywords": ["travel", "philosophy", "education", "foreign"]},
    10: {"ru": "10-й дом (МС): карьера, статус, репутация, публичная жизнь.", "en": "10th house (MC): career, status, reputation, public life.", "keywords": ["career", "status", "authority", "reputation"]},
    11: {"ru": "11-й дом: друзья, союзники, группы, надежды, социальные сети.", "en": "11th house: friends, allies, groups, hopes, social networks.", "keywords": ["friendship", "groups", "hopes", "community"]},
    12: {"ru": "12-й дом: скрытые враги, изоляция, тайны, самоуничтожение, духовность.", "en": "12th house: hidden enemies, isolation, secrets, self-undoing, spirituality.", "keywords": ["hidden", "isolation", "spirituality", "karma"]},
}


def house_text(house_number: int) -> Dict[str, Any]:
    """Return thematic text for a house number (1-12)."""
    return _HOUSE_TEXTS.get(house_number, {
        "ru": f"{house_number}-й дом: специфический анализ.",
        "en": f"House {house_number}: specific analysis required.",
        "keywords": [],
    })


# ─────────────────────────────────────────────────────────────────────────────
# PROFECTIONS
# ─────────────────────────────────────────────────────────────────────────────

_PROFECTION_HOUSE_THEMES: Dict[int, Dict] = {
    1:  {"ru": "Год Асцендента: период обновления личности, нового начала и физического самовыражения.", "en": "Ascendant year: renewal of self, new beginnings, physical self-expression."},
    2:  {"ru": "Год 2-го дома: финансовые вопросы, ресурсы, переоценка ценностей.", "en": "2nd house year: financial matters, resources, reassessment of values."},
    3:  {"ru": "Год 3-го дома: общение, обучение, связи с братьями/сёстрами, поездки.", "en": "3rd house year: communication, learning, sibling connections, short travel."},
    4:  {"ru": "Год IC: дом и семья в центре внимания; возможные переезды или семейные события.", "en": "IC year: home and family in focus; possible moves or family events."},
    5:  {"ru": "Год 5-го дома: творческий расцвет, романтика, дети, развлечения.", "en": "5th house year: creative flourishing, romance, children, entertainment."},
    6:  {"ru": "Год 6-го дома: здоровье, работа, служение; риск болезней и перегрузок.", "en": "6th house year: health, work, service; risk of illness and overwork."},
    7:  {"ru": "Год Десцендента: партнёрство, брак, открытое противостояние.", "en": "Descendant year: partnerships, marriage, open opposition."},
    8:  {"ru": "Год 8-го дома: трансформация, наследства, кризисы и возрождение.", "en": "8th house year: transformation, inheritances, crises and rebirth."},
    9:  {"ru": "Год 9-го дома: путешествия, духовный поиск, высшее образование.", "en": "9th house year: travel, spiritual quest, higher education."},
    10: {"ru": "Год МС: карьерный пик, публичное признание, смена статуса.", "en": "MC year: career peak, public recognition, change of status."},
    11: {"ru": "Год 11-го дома: друзья, союзники, достижение целей, групповая работа.", "en": "11th house year: friends, allies, achievement of goals, group work."},
    12: {"ru": "Год 12-го дома: уединение, скрытые дела, внутренняя работа, духовное развитие.", "en": "12th house year: retreat, hidden matters, inner work, spiritual development."},
}


def profection_year_text(house: int) -> Dict[str, Any]:
    """Return interpretive text for an annual profection house."""
    return _PROFECTION_HOUSE_THEMES.get(house, {
        "ru": f"Профекция на {house}-й дом: специальный анализ.",
        "en": f"Profection to house {house}: specific analysis.",
    })


# ─────────────────────────────────────────────────────────────────────────────
# COMBINED CHART SUMMARY
# ─────────────────────────────────────────────────────────────────────────────

def generate_chart_summary(
    asc_sign: str,
    sun_sign: str,
    moon_sign: str,
    stelliums: Optional[List[str]] = None,
    dominant_element: Optional[str] = None,
    is_day_chart: bool = True,
) -> Dict[str, str]:
    """Generate a brief overall chart summary paragraph.

    Args:
        asc_sign: Ascendant sign name.
        sun_sign: Sun sign name.
        moon_sign: Moon sign name.
        stelliums: List of signs/houses with 3+ planets.
        dominant_element: Most common element (Fire/Earth/Air/Water).
        is_day_chart: True if Sun above horizon at birth.

    Returns:
        {"ru": str, "en": str}
    """
    sun_txt = planet_in_sign_text("Sun", sun_sign)
    moon_txt = planet_in_sign_text("Moon", moon_sign)

    sect = "дневного" if is_day_chart else "ночного"
    sect_en = "diurnal" if is_day_chart else "nocturnal"

    ru = (
        f"Натальная карта {sect} типа. Асцендент в {asc_sign}. "
        f"Солнце в {sun_sign}: {sun_txt['ru']} "
        f"Луна в {moon_sign}: {moon_txt['ru']}"
    )
    en = (
        f"{sect_en.capitalize()} chart. Ascendant in {asc_sign}. "
        f"Sun in {sun_sign}: {sun_txt['en']} "
        f"Moon in {moon_sign}: {moon_txt['en']}"
    )

    if dominant_element:
        el_ru = {"Fire": "огонь", "Earth": "земля", "Air": "воздух", "Water": "вода"}
        ru += f" Доминирующая стихия: {el_ru.get(dominant_element, dominant_element)}."
        en += f" Dominant element: {dominant_element}."

    if stelliums:
        stellium_str = ", ".join(stelliums)
        ru += f" Стеллиум(ы) в: {stellium_str}."
        en += f" Stellium(s) in: {stellium_str}."

    return {"ru": ru, "en": en}
