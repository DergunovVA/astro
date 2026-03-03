# ⚪ STAGE 4: FUTURE FEATURES (v0.2+)

**Период:** Апрель-Июнь 2026+ (Q2-Q3)  
**Приоритет:** ⚪ LOW (Future releases)  
**Статус:** 📋 PLANNED  
**Команда:** Full team (phased releases)

---

## 🎯 ЦЕЛИ ЭТАПА

### Главная цель

Реализовать запланированные фичи для будущих версий: Horary Astrology (v0.2), Jyotish support (v0.3), и advanced dignities (v2.0).

### Релизы

- **v0.2** - Horary Astrology & Graph Layer (Apr-May 2026)
- **v0.3** - Jyotish/Sidereal Support (Jun-Jul 2026)
- **v2.0** - Advanced Dignities (Q3+ 2026)

### Метрики успеха

- v0.2: Graph layer operational, horary methods available
- v0.3: Sidereal zodiac calculations accurate
- v2.0: Minor dignities fully implemented

---

## 📋 v0.2: HORARY ASTROLOGY

**Timeline:** April 1 - May 15, 2026 (6 weeks)  
**Priority:** 🟡 HIGH  
**Focus:** Graph layer and horary-specific features

### Task 4.1: Graph Layer Implementation

**Приоритет:** 🟡 HIGH  
**Оценка:** 40 hours  
**Назначено:** Backend Team  
**Статус:** 📋 PLANNED

#### Features

##### 4.1.1: Mutual Receptions

```python
# src/modules/graph_layer.py

class ChartGraph:
    """Graph representation of chart relationships"""

    def add_mutual_reception(self, planet1: str, planet2: str):
        """
        Add mutual reception edge

        Mutual reception: planet1 in planet2's sign AND vice versa
        Example: Venus in Aries (Mars rules) AND Mars in Taurus (Venus rules)
        """
        # Check if mutual reception exists
        p1_sign = self.chart['planets'][planet1]['Sign']
        p2_sign = self.chart['planets'][planet2]['Sign']

        p1_ruler = self._get_sign_ruler(p1_sign)
        p2_ruler = self._get_sign_ruler(p2_sign)

        if p1_ruler == planet2 and p2_ruler == planet1:
            self.graph.add_edge(
                planet1, planet2,
                relation='mutual_reception',
                strength='strong',
                type='harmonious'
            )

    def find_all_receptions(self):
        """Find all mutual receptions in chart"""
        planets = list(self.chart['planets'].keys())
        receptions = []

        for i, p1 in enumerate(planets):
            for p2 in planets[i+1:]:
                if self._is_mutual_reception(p1, p2):
                    receptions.append((p1, p2))
                    self.add_mutual_reception(p1, p2)

        return receptions
```

##### 4.1.2: Dispositor Chains

```python
def build_dispositor_chain(self, planet: str) -> List[str]:
    """
    Build dispositor chain for planet

    Dispositor: ruler of the sign a planet is in
    Chain: planet → its dispositor → dispositor's dispositor → ...

    Example:
      Moon in Gemini → Mercury (rules Gemini)
      Mercury in Pisces → Jupiter (traditional ruler)
      Jupiter in Sagittarius → Jupiter (rules its own sign)
      Chain: Moon → Mercury → Jupiter → Jupiter (final dispositor)
    """
    chain = [planet]
    current = planet
    visited = set([planet])

    while True:
        sign = self.chart['planets'][current]['Sign']
        dispositor = self._get_sign_ruler(sign)

        if dispositor == current:
            # Final dispositor (planet in own sign)
            break

        if dispositor in visited:
            # Mutual reception loop detected
            chain.append(f"{dispositor} (loop)")
            break

        chain.append(dispositor)
        visited.add(dispositor)
        current = dispositor

        if len(chain) > 12:
            # Safety: max 12 iterations
            break

    return chain

def find_final_dispositor(self, planet: str) -> str:
    """Find final dispositor in chain"""
    chain = self.build_dispositor_chain(planet)
    return chain[-1].replace(" (loop)", "")

def analyze_dispositor_tree(self) -> Dict:
    """
    Analyze complete dispositor tree for chart

    Returns:
        {
            'final_dispositors': ['Jupiter', 'Venus'],
            'chains': {
                'Sun': ['Sun', 'Mars', 'Jupiter'],
                'Moon': ['Moon', 'Mercury', 'Jupiter'],
                ...
            },
            'loops': [('Venus', 'Mars')]  # Mutual receptions
        }
    """
    analysis = {
        'final_dispositors': set(),
        'chains': {},
        'loops': []
    }

    for planet in self.chart['planets'].keys():
        chain = self.build_dispositor_chain(planet)
        analysis['chains'][planet] = chain

        final = chain[-1]
        if '(loop)' in final:
            # Extract loop planets
            loop_planet = final.replace(' (loop)', '')
            loop_pair = tuple(sorted([chain[-2], loop_planet]))
            if loop_pair not in analysis['loops']:
                analysis['loops'].append(loop_pair)
        else:
            analysis['final_dispositors'].add(final)

    analysis['final_dispositors'] = list(analysis['final_dispositors'])
    return analysis
```

##### 4.1.3: Aspect Relationships Graph

```python
def add_aspect_edges(self):
    """Add aspect relationships as graph edges"""
    aspects = self.chart.get('aspects', [])

    for aspect in aspects:
        planet1 = aspect['planet1']
        planet2 = aspect['planet2']
        aspect_type = aspect['type']  # Conjunction, Trine, etc.
        orb = aspect['orb']

        # Determine aspect strength based on orb
        if orb < 1.0:
            strength = 'very_strong'
        elif orb < 3.0:
            strength = 'strong'
        elif orb < 5.0:
            strength = 'moderate'
        else:
            strength = 'weak'

        # Harmonious vs challenging
        harmonious = aspect_type in ['Trine', 'Sextile', 'Conjunction']

        self.graph.add_edge(
            planet1, planet2,
            relation='aspect',
            aspect_type=aspect_type,
            orb=orb,
            strength=strength,
            harmonious=harmonious
        )
```

##### 4.1.4: Graph Visualization Export

```python
def export_graphviz(self, filename: str):
    """Export graph to Graphviz DOT format"""
    import networkx as nx
    from networkx.drawing.nx_agraph import write_dot

    # Add visual attributes
    for node in self.graph.nodes():
        self.graph.nodes[node]['shape'] = 'circle'
        self.graph.nodes[node]['style'] = 'filled'
        self.graph.nodes[node]['fillcolor'] = self._get_planet_color(node)

    for u, v, data in self.graph.edges(data=True):
        if data['relation'] == 'mutual_reception':
            data['color'] = 'green'
            data['style'] = 'bold'
        elif data['relation'] == 'aspect':
            data['color'] = 'blue' if data['harmonious'] else 'red'
            data['label'] = data['aspect_type']

    write_dot(self.graph, filename)

def export_json(self) -> Dict:
    """Export graph as JSON for web visualization"""
    import networkx as nx
    from networkx.readwrite import json_graph

    return json_graph.node_link_data(self.graph)
```

#### Acceptance Criteria

- ✅ Mutual receptions detected
- ✅ Dispositor chains calculated
- ✅ Aspect relationships graphed
- ✅ Visualization exports work
- ✅ Test coverage > 90%

---

### Task 4.2: Horary-Specific Methods

**Приоритет:** 🟢 MEDIUM  
**Оценка:** 24 hours  
**Назначено:** Domain Expert  
**Статус:** 📋 PLANNED

#### Features

##### 4.2.1: Essential Dignities Score

```python
# src/core/dignities.py

def calculate_essential_dignity_score(planet: str, sign: str) -> int:
    """
    Calculate essential dignity score (traditional system)

    Scores:
      Ruler: +5
      Exaltation: +4
      Triplicity: +3
      Term: +2
      Face: +1
      Detriment: -5
      Fall: -4
      Peregrine: 0
    """
    score = 0

    if is_ruler(planet, sign):
        score += 5
    elif is_exaltation(planet, sign):
        score += 4
    elif is_fall(planet, sign):
        score -= 4
    elif is_detriment(planet, sign):
        score -= 5
    else:
        # Check triplicity, term, face
        if is_triplicity(planet, sign):
            score += 3
        if is_term(planet, sign):
            score += 2
        if is_face(planet, sign):
            score += 1

    return score
```

##### 4.2.2: Accidental Dignities

```python
def calculate_accidental_dignity_score(planet_data: Dict) -> int:
    """
    Calculate accidental dignity score

    Positive:
      Angular house (1,4,7,10): +4
      Succedent (2,5,8,11): +2
      Direct motion: +4
      Fast in motion: +2

    Negative:
      Cadent house (3,6,9,12): -1
      Retrograde: -5
      Slow in motion: -2
      Combust (within 8° of Sun): -5
      Under the beams (within 17° of Sun): -4
    """
    score = 0
    house = planet_data['House']

    # House strength
    if house in [1, 4, 7, 10]:
        score += 4
    elif house in [2, 5, 8, 11]:
        score += 2
    else:
        score -= 1

    # Motion
    if planet_data.get('Retrograde', False):
        score -= 5
    else:
        score += 4

    # Speed
    speed = planet_data.get('Speed', 0)
    if speed > average_speed(planet_data['name']):
        score += 2
    elif speed < average_speed(planet_data['name']) * 0.5:
        score -= 2

    # Combust/Under beams
    sun_pos = get_sun_position()
    distance_from_sun = abs(planet_data['AbsoluteDegree'] - sun_pos)

    if distance_from_sun < 8:
        score -= 5
    elif distance_from_sun < 17:
        score -= 4

    return score
```

##### 4.2.3: Horary Questions Analysis

```python
# src/modules/horary.py

class HoraryAnalyzer:
    """Analyze horary questions"""

    def analyze_question(self, chart: Dict, question_type: str) -> Dict:
        """
        Analyze horary question

        Question types:
          - 'will_it_happen': Yes/No outcome
          - 'when': Timing prediction
          - 'lost_object': Location of lost item
          - 'relationship': Relationship outcome
        """
        if question_type == 'will_it_happen':
            return self._analyze_yes_no(chart)
        elif question_type == 'when':
            return self._analyze_timing(chart)
        # ... more types

    def _analyze_yes_no(self, chart: Dict) -> Dict:
        """
        Yes/No question analysis

        Factors:
          - Mutual receptions between querent/quesited
          - Applying aspects
          - Translation of light
          - Collection of light
        """
        querent = self._get_querent_significator(chart)
        quesited = self._get_quesited_significator(chart)

        # Check for perfection of aspect
        aspect = self._find_applying_aspect(querent, quesited)

        result = {
            'answer': None,  # 'yes', 'no', 'uncertain'
            'confidence': 0.0,
            'factors': []
        }

        if aspect and aspect['applying']:
            result['answer'] = 'yes'
            result['confidence'] += 0.6
            result['factors'].append(f"Applying {aspect['type']} aspect")

        # Check mutual reception
        if self._has_mutual_reception(querent, quesited):
            result['answer'] = 'yes'
            result['confidence'] += 0.3
            result['factors'].append("Mutual reception present")

        # ... more factors

        return result
```

#### Acceptance Criteria

- ✅ Essential dignities scored
- ✅ Accidental dignities scored
- ✅ Horary analysis methods work
- ✅ Documentation comprehensive

---

## 📋 v0.3: JYOTISH/SIDEREAL SUPPORT

**Timeline:** June 1 - July 31, 2026 (8 weeks)  
**Priority:** 🟢 MEDIUM  
**Focus:** Sidereal zodiac calculations

### Task 4.3: Sidereal Zodiac Calculations

**Приоритет:** 🟢 MEDIUM  
**Оценка:** 32 hours  
**Назначено:** Calc Team  
**Статус:** 📋 PLANNED

#### Features

##### 4.3.1: Ayanamsa Support

```python
# src/calc/sidereal.py

AYANAMSAS = {
    'lahiri': 'Lahiri (Chitrapaksha)',
    'raman': 'B.V. Raman',
    'krishnamurti': 'Krishnamurti',
    'fagan_bradley': 'Fagan-Bradley (Western)',
}

def calculate_ayanamsa(jd: float, ayanamsa_type: str = 'lahiri') -> float:
    """
    Calculate ayanamsa (precession correction) for given Julian Day

    Args:
        jd: Julian Day
        ayanamsa_type: Type of ayanamsa to use

    Returns:
        Ayanamsa in degrees
    """
    import swisseph as swe

    ayanamsa_ids = {
        'lahiri': swe.SIDM_LAHIRI,
        'raman': swe.SIDM_RAMAN,
        'krishnamurti': swe.SIDM_KRISHNAMURTI,
        'fagan_bradley': swe.SIDM_FAGAN_BRADLEY,
    }

    swe.set_sid_mode(ayanamsa_ids[ayanamsa_type])
    return swe.get_ayanamsa(jd)

def tropical_to_sidereal(tropical_long: float, jd: float,
                         ayanamsa_type: str = 'lahiri') -> float:
    """Convert tropical longitude to sidereal"""
    ayanamsa = calculate_ayanamsa(jd, ayanamsa_type)
    sidereal_long = (tropical_long - ayanamsa) % 360
    return sidereal_long
```

##### 4.3.2: Nakshatra Calculations

```python
# src/models/nakshatra.py

NAKSHATRAS = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini',
    'Mrigashira', 'Ardra', 'Punarvasu', 'Pushya',
    'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
    'Hasta', 'Chitra', 'Swati', 'Vishakha',
    'Anuradha', 'Jyeshtha', 'Mula', 'Purva Ashadha',
    'Uttara Ashadha', 'Shravana', 'Dhanishta', 'Shatabhisha',
    'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
]

def get_nakshatra(sidereal_longitude: float) -> Dict:
    """
    Get nakshatra for sidereal longitude

    Each nakshatra = 13°20' (360° / 27)
    """
    nakshatra_width = 360.0 / 27
    nakshatra_index = int(sidereal_longitude / nakshatra_width)
    nakshatra_name = NAKSHATRAS[nakshatra_index]

    # Pada (quarter) within nakshatra
    nakshatra_degree = sidereal_longitude % nakshatra_width
    pada = int(nakshatra_degree / (nakshatra_width / 4)) + 1

    return {
        'nakshatra': nakshatra_name,
        'pada': pada,
        'degree_in_nakshatra': nakshatra_degree,
        'index': nakshatra_index
    }
```

##### 4.3.3: Vimshottari Dasa

```python
def calculate_vimshottari_dasa(moon_nakshatra_index: int,
                                birth_jd: float) -> List[Dict]:
    """
    Calculate Vimshottari Dasa periods

    Dasa periods (in years):
      Ketu: 7, Venus: 20, Sun: 6, Moon: 10, Mars: 7,
      Rahu: 18, Jupiter: 16, Saturn: 19, Mercury: 17
    """
    dasa_lords = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars',
                  'Rahu', 'Jupiter', 'Saturn', 'Mercury']
    dasa_years = [7, 20, 6, 10, 7, 18, 16, 19, 17]

    # Starting dasa lord based on birth nakshatra
    start_lord_index = moon_nakshatra_index % 9

    periods = []
    current_jd = birth_jd

    for i in range(9):
        lord_index = (start_lord_index + i) % 9
        lord = dasa_lords[lord_index]
        years = dasa_years[lord_index]

        periods.append({
            'lord': lord,
            'start_date': jd_to_date(current_jd),
            'end_date': jd_to_date(current_jd + years * 365.25),
            'years': years
        })

        current_jd += years * 365.25

    return periods
```

#### Acceptance Criteria

- ✅ Ayanamsa calculations accurate
- ✅ Nakshatra determination correct
- ✅ Dasa periods calculated
- ✅ Integration with existing system

---

## 📋 v2.0: ADVANCED DIGNITIES

**Timeline:** Q3 2026+ (12+ weeks)  
**Priority:** ⚪ LOW  
**Focus:** Minor dignities and advanced traditional astrology

### Task 4.4: Minor Dignities

**Приоритет:** ⚪ LOW  
**Оценка:** 40 hours  
**Назначено:** Research + Dev Team  
**Статус:** 📋 PLANNED

#### Features

##### 4.4.1: Triplicities (Elemental Rulers)

```python
# config/dignities_v2.yaml

triplicities:
  Fire:  # Aries, Leo, Sagittarius
    day_ruler: Sun
    night_ruler: Jupiter
    participating: Saturn

  Earth:  # Taurus, Virgo, Capricorn
    day_ruler: Venus
    night_ruler: Moon
    participating: Mars

  Air:  # Gemini, Libra, Aquarius
    day_ruler: Saturn
    night_ruler: Mercury
    participating: Jupiter

  Water:  # Cancer, Scorpio, Pisces
    day_ruler: Venus
    night_ruler: Mars
    participating: Moon
```

##### 4.4.2: Terms (Egyptian System)

```python
# Data from traditional texts
EGYPTIAN_TERMS = {
    'Aries': [
        {'planet': 'Jupiter', 'from': 0, 'to': 6},
        {'planet': 'Venus', 'from': 6, 'to': 12},
        {'planet': 'Mercury', 'from': 12, 'to': 20},
        {'planet': 'Mars', 'from': 20, 'to': 25},
        {'planet': 'Saturn', 'from': 25, 'to': 30},
    ],
    # ... all 12 signs
}

def get_term_ruler(sign: str, degree: float) -> str:
    """Get term ruler for planet at given degree in sign"""
    terms = EGYPTIAN_TERMS[sign]
    for term in terms:
        if term['from'] <= degree < term['to']:
            return term['planet']
    return None
```

##### 4.4.3: Faces/Decans

```python
DECAN_RULERS = {
    'Aries': ['Mars', 'Sun', 'Venus'],
    'Taurus': ['Mercury', 'Moon', 'Saturn'],
    # ... etc
}

def get_decan_ruler(sign: str, degree: float) -> str:
    """
    Get decan (face) ruler
    Each decan = 10°
    """
    decan_index = int(degree / 10)
    return DECAN_RULERS[sign][decan_index]
```

#### Acceptance Criteria

- ✅ Triplicities implemented
- ✅ Terms calculated correctly
- ✅ Faces/decans working
- ✅ Historical accuracy verified

---

## 📊 RELEASE SCHEDULE

### v0.2 Milestoneche

```
Week 1-2: Graph layer foundation
Week 3-4: Mutual receptions & dispositors
Week 5-6: Horary methods & testing
Week 7: Documentation & release prep
Week 8: v0.2 Release!
```

### v0.3 Milestones

```
Week 1-2: Ayanamsa calculations
Week 3-4: Nakshatra system
Week 5-6: Dasa calculations
Week 7-8: Integration & testing
Week 9: v0.3 Release!
```

### v2.0 Milestones

```
Month 1: Research traditional texts
Month 2: Implement triplicities & terms
Month 3: Testing & validation
Month 4: v2.0 Release!
```

---

## 🎯 SUCCESS CRITERIA

### v0.2 Complete When:

- [ ] Graph layer works
- [ ] All horary methods tested
- [ ] Documentation complete
- [ ] 95% test coverage

### v0.3 Complete When:

- [ ] Sidereal calculations accurate
- [ ] Nakshatra system working
- [ ] Dasa periods correct
- [ ] Integration seamless

### v2.0 Complete When:

- [ ] All minor dignities implemented
- [ ] Historical accuracy verified
- [ ] Comprehensive testing done
- [ ] User guide complete

---

_Created: 2026-02-20_  
_Planned Start: Q2 2026_  
_Target: Q3 2026_
