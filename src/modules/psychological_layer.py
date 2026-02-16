"""
Psychological Layer: Глубинная психология по натальной карте

Анализирует не очевидные психологические паттерны:
- Тени (подавленные качества)
- Демоны (деструктивные паттерны)
- Позывы (неосознанные мотивации)
- Доказухи (компенсаторное поведение)
- Мести (обиды, желание компенсировать)

Основан на юнгианской психологии + астрология (Подводный, Андреев)
"""

from typing import Dict, List, Any
from models.facts_models import Fact


class PsychologicalPattern:
    """Психологический паттерн"""

    def __init__(
        self,
        pattern_type: str,  # shadow, demon, impulse, prove, revenge
        planet: str,
        sign: str,
        house: int,
        aspects: List[str],
        description: str,
        manifestation: str,
        work_with: str,
    ):
        self.pattern_type = pattern_type
        self.planet = planet
        self.sign = sign
        self.house = house
        self.aspects = aspects
        self.description = description
        self.manifestation = manifestation
        self.work_with = work_with

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.pattern_type,
            "planet": self.planet,
            "sign": self.sign,
            "house": self.house,
            "aspects": self.aspects,
            "description": self.description,
            "manifestation": self.manifestation,
            "work_with": self.work_with,
        }


class PsychologicalAnalyzer:
    """Анализатор психологических паттернов"""

    # Планетарные тени (подавленные качества)
    PLANET_SHADOWS = {
        "Sun": {
            "shadow": "Подавленное желание быть в центре внимания",
            "demon": "Страх быть незамеченным, обесцененным",
            "impulse": "Компульсивная потребность в признании",
        },
        "Moon": {
            "shadow": "Подавленные эмоции и потребности",
            "demon": "Страх отвержения, эмоциональная зависимость",
            "impulse": "Неосознанная привязанность к материнскому образу",
        },
        "Mercury": {
            "shadow": 'Невысказанные мысли, "неправильные" идеи',
            "demon": 'Страх быть непонятым, "глупым"',
            "impulse": "Компульсивная необходимость объяснять",
        },
        "Venus": {
            "shadow": 'Подавленные желания, "неправильная" любовь',
            "demon": "Страх быть нелюбимым, отвергнутым",
            "impulse": "Неосознанные манипуляции через обаяние",
        },
        "Mars": {
            "shadow": "Подавленная агрессия и сексуальность",
            "demon": "Страх собственной силы или бессилия",
            "impulse": "Компульсивная борьба, доказывание силы",
        },
        "Jupiter": {
            "shadow": "Подавленная жадность, экспансия",
            "demon": 'Страх ограничений, "маленькой жизни"',
            "impulse": "Неосознанное раздувание значимости",
        },
        "Saturn": {
            "shadow": "Подавленная потребность в контроле",
            "demon": "Страх хаоса, потери статуса",
            "impulse": "Компульсивный перфекционизм",
        },
        "Uranus": {
            "shadow": "Подавленная уникальность, бунтарство",
            "demon": 'Страх быть "как все" или изгоем',
            "impulse": "Компульсивное эпатирование",
        },
        "Neptune": {
            "shadow": "Подавленные фантазии и иллюзии",
            "demon": "Страх реальности, трезвости",
            "impulse": "Неосознанный эскапизм",
        },
        "Pluto": {
            "shadow": "Подавленное желание власти",
            "demon": "Страх бессилия, уничтожения",
            "impulse": "Компульсивный контроль через страх",
        },
    }

    # Дома и психологические темы
    HOUSE_SHADOWS = {
        1: "Подавленная идентичность (кто я на самом деле?)",
        2: "Подавленная самооценка (я недостаточно ценен)",
        3: "Подавленное общение (что я не могу сказать)",
        4: "Подавленные корни (семейные тайны)",
        5: "Подавленная креативность (я не могу творить)",
        6: "Подавленное тело (болезнь как сигнал)",
        7: "Подавленная потребность в другом",
        8: "Подавленная сексуальность/смерть",
        9: "Подавленный поиск смысла",
        10: "Подавленное призвание (не та профессия)",
        11: "Подавленная уникальность (не вписываюсь)",
        12: "Подавленное бессознательное (что я не хочу знать)",
    }

    # Напряженные аспекты = психологические конфликты
    ASPECT_CONFLICTS = {
        "square": {
            "conflict": "Внутренний конфликт (90°)",
            "pattern": "Две части психики борются друг с другом",
        },
        "opposition": {
            "conflict": "Полярность (180°)",
            "pattern": "Качание между крайностями",
        },
    }

    def __init__(self, calc_result: Dict[str, Any], facts: List[Fact]):
        self.calc_result = calc_result
        self.facts = facts
        self.planets = calc_result["planets"]
        self.houses = calc_result["houses"]
        self.aspects = calc_result.get("aspects", [])

    def analyze_shadows(self) -> List[PsychologicalPattern]:
        """Анализ теней (подавленных качеств)"""
        shadows = []

        # Планеты в домах
        for fact in self.facts:
            if fact.type == "planet_in_sign":
                planet = fact.object
                sign = fact.value
                house = (fact.details or {}).get("house", 0)

                if planet in self.PLANET_SHADOWS:
                    shadow_data = self.PLANET_SHADOWS[planet]
                    house_shadow = self.HOUSE_SHADOWS.get(house, "Неизвестная сфера")

                    # Находим напряженные аспекты этой планеты
                    hard_aspects = self._get_hard_aspects(planet)

                    pattern = PsychologicalPattern(
                        pattern_type="shadow",
                        planet=planet,
                        sign=sign,
                        house=house,
                        aspects=hard_aspects,
                        description=shadow_data["shadow"],
                        manifestation=f"{house_shadow}. {self._get_sign_flavor(sign, 'shadow')}",
                        work_with=self._get_shadow_work(planet, house, hard_aspects),
                    )
                    shadows.append(pattern)

        return shadows

    def analyze_demons(self) -> List[PsychologicalPattern]:
        """Анализ демонов (деструктивных паттернов)"""
        demons = []

        # Напряженные аспекты = внутренние демоны
        for fact in self.facts:
            if fact.type == "aspect":
                # aspect_type в value, не в details
                aspect_type = fact.value

                if aspect_type in ["square", "opposition"]:
                    # Парсим планеты из object (например, "Sun-Mars")
                    planets = fact.object.split("-")
                    if len(planets) == 2:
                        planet1 = planets[0].strip()
                        planet2 = planets[1].strip()

                        demon_desc = self._get_demon_from_aspect(
                            planet1, planet2, aspect_type
                        )

                        if demon_desc:
                            pattern = PsychologicalPattern(
                                pattern_type="demon",
                                planet=f"{planet1}-{planet2}",
                                sign="",
                                house=0,
                                aspects=[aspect_type],
                                description=demon_desc["description"],
                                manifestation=demon_desc["manifestation"],
                                work_with=demon_desc["healing"],
                            )
                            demons.append(pattern)

        return demons

    def analyze_impulses(self) -> List[PsychologicalPattern]:
        """Анализ позывов (неосознанных мотиваций)"""
        impulses = []

        for fact in self.facts:
            if fact.type == "planet_in_sign":
                planet = fact.object
                sign = fact.value
                house = (fact.details or {}).get("house", 0)

                if planet in self.PLANET_SHADOWS:
                    impulse_data = self.PLANET_SHADOWS[planet]

                    # Retrograde планеты = особо сильные неосознанные паттерны
                    is_retrograde = (fact.details or {}).get("retrograde", False)

                    impulse_desc = impulse_data["impulse"]
                    if is_retrograde:
                        impulse_desc += (
                            " (УСИЛЕНО РЕТРОГРАДНОСТЬЮ - паттерн из прошлого)"
                        )

                    pattern = PsychologicalPattern(
                        pattern_type="impulse",
                        planet=planet,
                        sign=sign,
                        house=house,
                        aspects=[],
                        description=impulse_desc,
                        manifestation=self._get_impulse_manifestation(planet, house),
                        work_with="Осознать паттерн через медитацию, терапию, астрологию",
                    )
                    impulses.append(pattern)

        return impulses

    def analyze_proofs(self) -> List[PsychologicalPattern]:
        """Анализ доказух (компенсаторное поведение)"""
        proofs = []

        # "Доказухи" возникают когда планета в падении/изгнании
        # или имеет много напряженных аспектов

        DIFFICULT_PLACEMENTS = {
            ("Sun", "Aquarius"): "Постоянное доказывание уникальности",
            ("Sun", "Libra"): "Постоянное доказывание значимости через других",
            ("Moon", "Capricorn"): 'Постоянное доказывание "я справляюсь"',
            ("Moon", "Scorpio"): "Постоянное доказывание силы чувств",
            ("Mercury", "Pisces"): "Постоянное доказывание интеллекта",
            ("Venus", "Aries"): "Постоянное доказывание привлекательности",
            ("Venus", "Virgo"): "Постоянное доказывание полезности",
            ("Mars", "Cancer"): "Постоянное доказывание силы",
            ("Mars", "Libra"): "Постоянное доказывание правоты",
            ("Jupiter", "Gemini"): "Постоянное доказывание мудрости",
            ("Saturn", "Cancer"): "Постоянное доказывание ответственности",
        }

        for fact in self.facts:
            if fact.type == "planet_in_sign":
                planet = fact.object
                sign = fact.value
                house = (fact.details or {}).get("house", 0)

                key = (planet, sign)
                if key in DIFFICULT_PLACEMENTS:
                    proof_desc = DIFFICULT_PLACEMENTS[key]

                    pattern = PsychologicalPattern(
                        pattern_type="proof",
                        planet=planet,
                        sign=sign,
                        house=house,
                        aspects=self._get_hard_aspects(planet),
                        description=proof_desc,
                        manifestation=self._get_proof_manifestation(planet, house),
                        work_with="Принять, что нечего доказывать. Ценность изначальна.",
                    )
                    proofs.append(pattern)

        return proofs

    def analyze_revenges(self) -> List[PsychologicalPattern]:
        """Анализ местей (обиды, желание компенсировать)"""
        revenges = []

        # "Мести" связаны с:
        # 1. Плутон (желание отомстить)
        # 2. Марс (агрессивная месть)
        # 3. Сатурн (холодная месть, "докажу вам")
        # 4. Хирон (месть из раны)

        REVENGE_PLANETS = ["Pluto", "Mars", "Saturn", "Chiron"]

        for fact in self.facts:
            if fact.type == "planet_in_sign":
                planet = fact.object

                if planet in REVENGE_PLANETS:
                    sign = fact.value
                    house = (fact.details or {}).get("house", 0)
                    hard_aspects = self._get_hard_aspects(planet)

                    # Только если есть напряженные аспекты (активация мести)
                    if hard_aspects:
                        revenge_desc = self._get_revenge_pattern(planet, sign, house)

                        pattern = PsychologicalPattern(
                            pattern_type="revenge",
                            planet=planet,
                            sign=sign,
                            house=house,
                            aspects=hard_aspects,
                            description=revenge_desc["description"],
                            manifestation=revenge_desc["manifestation"],
                            work_with=revenge_desc["healing"],
                        )
                        revenges.append(pattern)

        return revenges

    def get_full_analysis(self) -> Dict[str, List[Dict[str, Any]]]:
        """Полный психологический анализ"""
        return {
            "shadows": [p.to_dict() for p in self.analyze_shadows()],
            "demons": [p.to_dict() for p in self.analyze_demons()],
            "impulses": [p.to_dict() for p in self.analyze_impulses()],
            "proofs": [p.to_dict() for p in self.analyze_proofs()],
            "revenges": [p.to_dict() for p in self.analyze_revenges()],
        }

    # Вспомогательные методы

    def _get_hard_aspects(self, planet: str) -> List[str]:
        """Получить напряженные аспекты планеты"""
        hard = []
        for fact in self.facts:
            if fact.type == "aspect":
                # Проверяем что планета участвует в аспекте
                if planet in fact.object:
                    aspect_type = fact.value
                    if aspect_type in ["square", "opposition"]:
                        # Извлечь вторую планету из object (например "Sun-Mars")
                        planets = fact.object.split("-")
                        if len(planets) == 2:
                            other = (
                                planets[1].strip()
                                if planets[0].strip() == planet
                                else planets[0].strip()
                            )
                            hard.append(f"{aspect_type} {other}")
        return hard

    def _get_sign_flavor(self, sign: str, pattern_type: str) -> str:
        """Получить окраску знака для паттерна"""
        # Упрощенная версия
        SIGN_FLAVORS = {
            "Aries": "Импульсивно, через действие",
            "Taurus": "Упрямо, материально",
            "Gemini": "Ментально, через слова",
            "Cancer": "Эмоционально, через семью",
            "Leo": "Драматично, через эго",
            "Virgo": "Перфекционистски, через критику",
            "Libra": "Через отношения, баланс",
            "Scorpio": "Интенсивно, через контроль",
            "Sagittarius": "Философски, через поиск смысла",
            "Capricorn": "Через статус, достижения",
            "Aquarius": "Через отстранение, бунт",
            "Pisces": "Через жертвенность, иллюзии",
        }
        return SIGN_FLAVORS.get(sign, "")

    def _get_shadow_work(self, planet: str, house: int, aspects: List[str]) -> str:
        """Работа с тенью"""
        work = f"Признать подавленное качество {planet}. "

        if house in [1, 10]:
            work += "Интегрировать в публичную идентичность."
        elif house in [4, 8, 12]:
            work += "Проработать через психотерапию, глубинную работу."
        else:
            work += "Постепенно проявлять в безопасных условиях."

        if aspects:
            work += f" Особое внимание к конфликтам: {', '.join(aspects[:2])}"

        return work

    def _get_demon_from_aspect(
        self, planet1: str, planet2: str, aspect: str
    ) -> Dict[str, str]:
        """Демон из напряженного аспекта"""
        # Специфичные комбинации
        DEMON_COMBOS = {
            ("Sun", "Saturn", "square"): {
                "description": 'Демон недостойности: "Я недостаточно хорош"',
                "manifestation": "Хронический перфекционизм, страх неудачи, блокировка самовыражения",
                "healing": "Разделить Я и Достижения. Отцовская фигура (проработать).",
            },
            ("Moon", "Saturn", "square"): {
                "description": 'Демон холодной матери: "Меня не любят"',
                "manifestation": "Эмоциональная черствость, страх близости, депрессия",
                "healing": "Материнская рана (терапия). Разрешить себе чувствовать.",
            },
            ("Sun", "Pluto", "square"): {
                "description": "Демон уничтожения эго: страх быть уничтоженным",
                "manifestation": "Борьба за власть, манипуляции, страх потери контроля",
                "healing": "Принять смерть старого Я. Трансформация через кризис.",
            },
            ("Mars", "Pluto", "square"): {
                "description": "Демон насилия: неконтролируемый гнев",
                "manifestation": "Подавленная ярость → взрывы, саморазрушение",
                "healing": "Конструктивные выходы для агрессии (спорт, творчество).",
            },
            ("Moon", "Neptune", "opposition"): {
                "description": "Демон слияния: потеря границ",
                "manifestation": "Созависимость, иллюзии в отношениях, эскапизм",
                "healing": "Укрепление границ. Трезвость вместо иллюзий.",
            },
        }

        # Проверяем прямую комбинацию
        key = (planet1, planet2, aspect)
        if key in DEMON_COMBOS:
            return DEMON_COMBOS[key]

        # Проверяем обратную
        key_reverse = (planet2, planet1, aspect)
        if key_reverse in DEMON_COMBOS:
            return DEMON_COMBOS[key_reverse]

        # Общий паттерн для неизвестных комбинаций
        conflict = self.ASPECT_CONFLICTS.get(aspect, {})
        return {
            "description": f"{planet1} vs {planet2}: {conflict.get('conflict', 'конфликт')}",
            "manifestation": conflict.get("pattern", "Внутреннее напряжение"),
            "healing": "Найти баланс между противоположностями",
        }

    def _get_impulse_manifestation(self, planet: str, house: int) -> str:
        """Как проявляется неосознанный позыв"""
        HOUSE_AREAS = {
            1: "В самоощущении, поведении",
            2: "В деньгах, самооценке",
            3: "В общении, обучении",
            4: "В семье, доме",
            5: "В творчестве, детях, романах",
            6: "В работе, здоровье",
            7: "В отношениях, партнерствах",
            8: "В сексе, кризисах, чужих деньгах",
            9: "В философии, путешествиях",
            10: "В карьере, публичности",
            11: "В дружбе, группах, мечтах",
            12: "В изоляции, духовности, тайнах",
        }
        return HOUSE_AREAS.get(house, "В неизвестной сфере")

    def _get_proof_manifestation(self, planet: str, house: int) -> str:
        """Как проявляется доказуха"""
        manifestations = {
            "Sun": "Постоянная демонстрация достижений, нарциссизм",
            "Moon": 'Гиперопека, "я самый заботливый"',
            "Mercury": 'Умничание, "я самый умный"',
            "Venus": 'Обольщение, "я самый привлекательный"',
            "Mars": 'Агрессивная конкуренция, "я самый сильный"',
            "Jupiter": 'Высокомерие, "я знаю истину"',
            "Saturn": 'Трудоголизм, "я самый ответственный"',
        }
        base = manifestations.get(planet, "Компенсаторное поведение")
        area = self._get_impulse_manifestation(planet, house)
        return f"{base}. {area}"

    def _get_revenge_pattern(
        self, planet: str, sign: str, house: int
    ) -> Dict[str, str]:
        """Паттерн мести"""
        REVENGE_PATTERNS = {
            "Pluto": {
                "description": "Месть через уничтожение (психологическое или реальное)",
                "manifestation": 'Долго помню обиды. Стратегическая месть. "Око за око".',
                "healing": "Прощение = освобождение от яда. Трансформация боли в силу.",
            },
            "Mars": {
                "description": "Импульсивная месть (вспышки гнева)",
                "manifestation": "Быстрая агрессия в ответ на обиду. Физическое насилие (риск).",
                "healing": "Конструктивные каналы для гнева. Спорт, творчество.",
            },
            "Saturn": {
                "description": 'Холодная месть ("я докажу, что вы ошибались")',
                "manifestation": "Годами строю успех, чтобы показать обидчикам. Успех = месть.",
                "healing": "Строить для себя, не для доказательства другим.",
            },
            "Chiron": {
                "description": "Месть из раны (причинить ту же боль)",
                "manifestation": "Раненый ранит других. Цикл передачи травмы.",
                "healing": "Исцелить рану = прервать цикл. Стать целителем, не мстителем.",
            },
        }

        pattern = REVENGE_PATTERNS.get(
            planet,
            {
                "description": "Паттерн мести",
                "manifestation": "Желание компенсировать обиду",
                "healing": "Прощение и принятие",
            },
        )

        # Добавляем специфику знака
        sign_flavor = self._get_sign_flavor(sign, "revenge")
        pattern["manifestation"] += f" {sign_flavor}"

        return pattern


def get_psychological_analysis(
    calc_result: Dict[str, Any], facts: List[Fact]
) -> Dict[str, Any]:
    """
    Получить психологический анализ карты

    Args:
        calc_result: результат calc_natal()
        facts: список фактов из facts_from_calculation()

    Returns:
        Dict с тенями, демонами, позывами, доказухами, местями
    """
    analyzer = PsychologicalAnalyzer(calc_result, facts)
    return analyzer.get_full_analysis()
