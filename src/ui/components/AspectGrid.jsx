import React, { useMemo } from 'react';

const aspectSymbol = {
  conjunction: '☌',
  opposition: '☍',
  trine: '△',
  square: '□',
  sextile: '✶',
  quincunx: '⚻',
};

export default function AspectGrid({ planets = {}, aspects = [] }) {
  const planetNames = useMemo(() => Object.keys(planets), [planets]);
  const matrix = useMemo(() => {
    const lookup = new Map();
    aspects.forEach((aspect) => {
      lookup.set(`${aspect.p1}:${aspect.p2}`, aspect);
      lookup.set(`${aspect.p2}:${aspect.p1}`, aspect);
    });
    return lookup;
  }, [aspects]);

  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ borderCollapse: 'collapse', color: '#edf2f7', minWidth: 640 }}>
        <thead>
          <tr>
            <th style={{ padding: 10, borderBottom: '1px solid #29415e' }}>Planet</th>
            {planetNames.map((name) => (
              <th key={name} style={{ padding: 10, borderBottom: '1px solid #29415e', minWidth: 68 }}>{name}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {planetNames.map((rowName) => (
            <tr key={rowName}>
              <th style={{ padding: 10, textAlign: 'left', borderBottom: '1px solid rgba(41,65,94,0.45)' }}>{rowName}</th>
              {planetNames.map((colName) => {
                if (rowName === colName) {
                  return <td key={colName} style={{ padding: 10, textAlign: 'center', borderBottom: '1px solid rgba(41,65,94,0.45)', color: '#678' }}>—</td>;
                }
                const aspect = matrix.get(`${rowName}:${colName}`);
                const isHard = ['square', 'opposition'].includes(aspect?.type);
                const tone = !aspect ? '#8d9aad' : isHard ? '#ff8a80' : '#8be28b';
                return (
                  <td key={colName} style={{ padding: 10, textAlign: 'center', borderBottom: '1px solid rgba(41,65,94,0.45)', color: tone }}>
                    {aspect ? `${aspectSymbol[aspect.type] || aspect.type} ${Number(aspect.orb).toFixed(1)}°` : ''}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
