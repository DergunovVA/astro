import React, { useMemo } from 'react';

const PLANET_GLYPHS = {
  Sun: '☉', Moon: '☽', Mercury: '☿', Venus: '♀', Mars: '♂', Jupiter: '♃', Saturn: '♄',
  Uranus: '♅', Neptune: '♆', Pluto: '♇', 'North Node': '☊', Chiron: '⚷', Proserpina: '⯓',
};

const SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'];

const deriveSign = (longitude = 0) => SIGNS[Math.floor((((longitude % 360) + 360) % 360) / 30)];
const degreeInSign = (longitude = 0) => ((((longitude % 360) + 360) % 360) % 30).toFixed(2);

export default function PlanetTable({ planets = {} }) {
  const rows = useMemo(
    () => Object.entries(planets)
      .map(([name, data]) => ({
        name,
        longitude: Number(data.longitude || 0),
        sign: data.sign || deriveSign(Number(data.longitude || 0)),
        degree: degreeInSign(Number(data.longitude || 0)),
        house: data.house ?? '—',
        dignity: data.dignity ?? '—',
        speed: data.speed ?? '—',
        retrograde: Boolean(data.retrograde),
      }))
      .sort((a, b) => a.longitude - b.longitude),
    [planets],
  );

  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', color: '#eef3fb' }}>
        <thead>
          <tr>
            {['Planet', 'Symbol', 'Sign', 'Degree', 'House', 'Dignity', 'Speed', 'Retrograde'].map((label) => (
              <th key={label} style={{ textAlign: 'left', padding: '12px 10px', borderBottom: '1px solid #29415e', color: '#aab9ce' }}>{label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.name} style={{ borderBottom: '1px solid rgba(41,65,94,0.45)' }}>
              <td style={{ padding: '12px 10px' }}>{row.name}</td>
              <td style={{ padding: '12px 10px', fontSize: 20 }}>{PLANET_GLYPHS[row.name] || '•'}</td>
              <td style={{ padding: '12px 10px' }}>{row.sign}</td>
              <td style={{ padding: '12px 10px' }}>{row.degree}°</td>
              <td style={{ padding: '12px 10px' }}>{row.house}</td>
              <td style={{ padding: '12px 10px' }}>{row.dignity}</td>
              <td style={{ padding: '12px 10px' }}>{typeof row.speed === 'number' ? row.speed.toFixed(3) : row.speed}</td>
              <td style={{ padding: '12px 10px', color: row.retrograde ? '#ff8a80' : '#8be28b' }}>{row.retrograde ? 'Yes' : 'No'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
