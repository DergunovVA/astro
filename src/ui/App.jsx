import React from 'react';
import {
  AspectGrid,
  HoraryChartView,
  PlanetTable,
  TransitTimeline,
  ZodiacWheel,
} from './components/index.js';

const demoPlanets = {
  Sun: { longitude: 285.3, sign: 'Capricorn', house: 10, dignity: 'Strong', speed: 1.02, retrograde: false },
  Moon: { longitude: 112.4, sign: 'Cancer', house: 4, dignity: 'Very Strong', speed: 13.1, retrograde: false },
  Mercury: { longitude: 301.5, sign: 'Aquarius', house: 11, dignity: 'Moderate', speed: 0.85, retrograde: false },
  Venus: { longitude: 250.7, sign: 'Sagittarius', house: 9, dignity: 'Moderate', speed: 1.21, retrograde: false },
  Mars: { longitude: 198.2, sign: 'Libra', house: 7, dignity: 'Weak', speed: 0.57, retrograde: false },
  Jupiter: { longitude: 217.6, sign: 'Scorpio', house: 8, dignity: 'Strong', speed: 0.19, retrograde: false },
  Saturn: { longitude: 182.1, sign: 'Libra', house: 7, dignity: 'Strong', speed: -0.04, retrograde: true },
};

const demoHouses = Object.fromEntries(Array.from({ length: 12 }, (_, idx) => [`H${idx + 1}`, (idx * 30 + 12) % 360]));

const demoAspects = [
  { p1: 'Sun', p2: 'Moon', type: 'opposition', orb: 2.1 },
  { p1: 'Moon', p2: 'Jupiter', type: 'trine', orb: 1.4 },
  { p1: 'Mars', p2: 'Saturn', type: 'conjunction', orb: 1.8 },
  { p1: 'Venus', p2: 'Mercury', type: 'sextile', orb: 0.9 },
];

const demoTransits = [
  { date: '2025-01-04', planet: 'Jupiter', natal_planet: 'Sun', aspect: 'trine', orb: 0.6 },
  { date: '2025-02-15', planet: 'Mars', natal_planet: 'Moon', aspect: 'square', orb: 1.2 },
  { date: '2025-03-20', planet: 'Venus', natal_planet: 'Mars', aspect: 'sextile', orb: 0.3 },
  { date: '2025-05-09', planet: 'Saturn', natal_planet: 'Mercury', aspect: 'trine', orb: 0.8 },
];

const demoHorary = {
  question: { text: 'Will the lost ring be recovered?', type: 'lost-item', quesited_house: 2 },
  chart: { local_datetime: '2025-02-14T18:45:00+03:00', place: 'Rehovot, Israel' },
  significators: {
    querent: { planet: 'Venus', sign: 'Pisces', house: 1, dignity: 'Strong', dignity_score: 4 },
    quesited: { planet: 'Mars', sign: 'Scorpio', house: 2, dignity: 'Strong', dignity_score: 5 },
  },
  applying_aspects: [
    { planet1: 'Moon', planet2: 'Mars', type: 'trine', orb: 1.1, timing: { days: 1.6, hours: 38.4, is_applying: true } },
  ],
  separating_aspects: [
    { planet1: 'Venus', planet2: 'Saturn', type: 'square', orb: 2.4 },
  ],
  receptions: [
    { planet1: 'Venus', planet2: 'Mars', type: 'mutual domicile', planet1_sign: 'Scorpio', planet2_sign: 'Taurus' },
  ],
  verdict: { answer: 'yes', confidence: 0.81, rationale: 'Applying Moon-Mars trine with supportive reception.' },
};

const sectionStyle = {
  background: '#0f1b2d',
  border: '1px solid #1f3048',
  borderRadius: 16,
  padding: 20,
  boxShadow: '0 12px 28px rgba(0,0,0,0.24)',
};

export default function App() {
  return (
    <div style={{ padding: 24, display: 'grid', gap: 24 }}>
      <div>
        <h1 style={{ margin: 0 }}>Astrology UI Components</h1>
        <p style={{ color: '#b7c2d6' }}>Demo surface for the FastAPI + React wrapper components.</p>
      </div>

      <section style={sectionStyle}>
        <h2>Zodiac Wheel</h2>
        <ZodiacWheel planets={demoPlanets} houses={demoHouses} aspects={demoAspects} />
      </section>

      <section style={sectionStyle}>
        <h2>Planet Table</h2>
        <PlanetTable planets={demoPlanets} />
      </section>

      <section style={sectionStyle}>
        <h2>Aspect Grid</h2>
        <AspectGrid planets={demoPlanets} aspects={demoAspects} />
      </section>

      <section style={sectionStyle}>
        <h2>Transit Timeline</h2>
        <TransitTimeline transits={demoTransits} />
      </section>

      <section style={sectionStyle}>
        <h2>Horary Chart View</h2>
        <HoraryChartView data={demoHorary} />
      </section>
    </div>
  );
}
