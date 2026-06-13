import React, { useMemo } from 'react';

const SIGNS = [
  { name: 'Aries', glyph: '♈', element: 'Fire', color: '#cf4b43' },
  { name: 'Taurus', glyph: '♉', element: 'Earth', color: '#7b5e3b' },
  { name: 'Gemini', glyph: '♊', element: 'Air', color: '#d0ab2f' },
  { name: 'Cancer', glyph: '♋', element: 'Water', color: '#2f75c8' },
  { name: 'Leo', glyph: '♌', element: 'Fire', color: '#cf4b43' },
  { name: 'Virgo', glyph: '♍', element: 'Earth', color: '#7b5e3b' },
  { name: 'Libra', glyph: '♎', element: 'Air', color: '#d0ab2f' },
  { name: 'Scorpio', glyph: '♏', element: 'Water', color: '#2f75c8' },
  { name: 'Sagittarius', glyph: '♐', element: 'Fire', color: '#cf4b43' },
  { name: 'Capricorn', glyph: '♑', element: 'Earth', color: '#7b5e3b' },
  { name: 'Aquarius', glyph: '♒', element: 'Air', color: '#d0ab2f' },
  { name: 'Pisces', glyph: '♓', element: 'Water', color: '#2f75c8' },
];

const PLANET_GLYPHS = {
  Sun: '☉', Moon: '☽', Mercury: '☿', Venus: '♀', Mars: '♂', Jupiter: '♃', Saturn: '♄',
  Uranus: '♅', Neptune: '♆', Pluto: '♇', 'North Node': '☊', Chiron: '⚷', Proserpina: '⯓',
};

const harmonious = new Set(['trine', 'sextile']);
const challenging = new Set(['square', 'opposition']);

const polarPoint = (cx, cy, radius, longitude) => {
  const radians = ((longitude - 90) * Math.PI) / 180;
  return {
    x: cx + radius * Math.cos(radians),
    y: cy + radius * Math.sin(radians),
  };
};

const arcPath = (cx, cy, outerRadius, innerRadius, start, end) => {
  const startOuter = polarPoint(cx, cy, outerRadius, start);
  const endOuter = polarPoint(cx, cy, outerRadius, end);
  const startInner = polarPoint(cx, cy, innerRadius, start);
  const endInner = polarPoint(cx, cy, innerRadius, end);
  return [
    `M ${startOuter.x} ${startOuter.y}`,
    `A ${outerRadius} ${outerRadius} 0 0 1 ${endOuter.x} ${endOuter.y}`,
    `L ${endInner.x} ${endInner.y}`,
    `A ${innerRadius} ${innerRadius} 0 0 0 ${startInner.x} ${startInner.y}`,
    'Z',
  ].join(' ');
};

export default function ZodiacWheel({ planets = {}, houses = {}, aspects = [] }) {
  const size = 520;
  const center = size / 2;
  const sectorOuter = 240;
  const sectorInner = 165;
  const planetRadius = 138;
  const aspectRadius = 120;

  const planetEntries = useMemo(() => Object.entries(planets), [planets]);

  const planetPoints = useMemo(
    () => Object.fromEntries(
      planetEntries.map(([name, data]) => [name, polarPoint(center, center, aspectRadius, Number(data.longitude || 0))]),
    ),
    [planetEntries],
  );

  return (
    <div style={{ display: 'grid', placeItems: 'center', gap: 12 }}>
      <svg viewBox={`0 0 ${size} ${size}`} width="100%" style={{ maxWidth: 520 }}>
        <circle cx={center} cy={center} r={sectorOuter} fill="#08111f" stroke="#d6dee8" strokeWidth="2" />
        <circle cx={center} cy={center} r={sectorInner} fill="#102038" stroke="#304867" strokeWidth="1.5" />
        <circle cx={center} cy={center} r={aspectRadius} fill="transparent" stroke="#22324a" strokeWidth="1" />

        {SIGNS.map((sign, idx) => {
          const start = idx * 30;
          const end = start + 30;
          const labelPoint = polarPoint(center, center, (sectorOuter + sectorInner) / 2, start + 15);
          return (
            <g key={sign.name}>
              <path d={arcPath(center, center, sectorOuter, sectorInner, start, end)} fill={sign.color} opacity="0.6" stroke="#0f1b2d" strokeWidth="1" />
              <text x={labelPoint.x} y={labelPoint.y} fill="#f8fbff" textAnchor="middle" dominantBaseline="middle" fontSize="22">
                {sign.glyph}
              </text>
            </g>
          );
        })}

        {Object.entries(houses).map(([house, longitude]) => {
          const outer = polarPoint(center, center, sectorOuter, Number(longitude));
          const label = polarPoint(center, center, sectorOuter + 14, Number(longitude));
          return (
            <g key={house}>
              <line x1={center} y1={center} x2={outer.x} y2={outer.y} stroke="#8ba5c7" strokeWidth={house === 'H1' || house === 'H10' ? 2.5 : 1.2} opacity="0.85" />
              <text x={label.x} y={label.y} fill="#b9c8da" fontSize="10" textAnchor="middle" dominantBaseline="middle">{house}</text>
            </g>
          );
        })}

        {aspects.map((aspect, index) => {
          const p1 = planetPoints[aspect.p1];
          const p2 = planetPoints[aspect.p2];
          if (!p1 || !p2) return null;
          let stroke = '#c0c8d6';
          if (harmonious.has(aspect.type)) stroke = '#3bb273';
          if (challenging.has(aspect.type)) stroke = '#d94f4f';
          return (
            <line
              key={`${aspect.p1}-${aspect.p2}-${index}`}
              x1={p1.x}
              y1={p1.y}
              x2={p2.x}
              y2={p2.y}
              stroke={stroke}
              strokeWidth="1.5"
              opacity="0.85"
            />
          );
        })}

        {planetEntries.map(([name, data]) => {
          const longitude = Number(data.longitude || 0);
          const point = polarPoint(center, center, planetRadius, longitude);
          return (
            <g key={name}>
              <circle cx={point.x} cy={point.y} r="9" fill="#f6f1d3" stroke="#22324a" strokeWidth="1.5" />
              <text x={point.x} y={point.y} fill="#0f1b2d" textAnchor="middle" dominantBaseline="middle" fontSize="12" fontWeight="700">
                {PLANET_GLYPHS[name] || name.slice(0, 2)}
              </text>
            </g>
          );
        })}
      </svg>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, justifyContent: 'center', color: '#c5d0df', fontSize: 12 }}>
        <span>Fire: red</span>
        <span>Earth: brown</span>
        <span>Air: yellow</span>
        <span>Water: blue</span>
      </div>
    </div>
  );
}
