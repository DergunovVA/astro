import React, { useMemo } from 'react';
import { extent, scaleTime, timeFormat, timeMonth } from 'd3';

const aspectColors = {
  trine: '#3bb273',
  sextile: '#56c5a8',
  conjunction: '#d2d6e3',
  square: '#d94f4f',
  opposition: '#ff7a66',
};

export default function TransitTimeline({ transits = [] }) {
  const parsed = useMemo(
    () => transits
      .map((transit) => ({ ...transit, parsedDate: new Date(transit.date) }))
      .filter((transit) => !Number.isNaN(transit.parsedDate.getTime()))
      .sort((a, b) => a.parsedDate - b.parsedDate),
    [transits],
  );

  const rows = useMemo(() => Array.from(new Set(parsed.map((item) => `${item.planet} ${item.aspect} ${item.natal_planet}`))), [parsed]);
  const domain = parsed.length
    ? extent(parsed, (item) => item.parsedDate)
    : [new Date(new Date().getFullYear(), 0, 1), new Date(new Date().getFullYear(), 11, 31)];

  const width = 920;
  const left = 180;
  const right = 30;
  const top = 40;
  const rowHeight = 48;
  const height = top + Math.max(rows.length, 1) * rowHeight + 30;
  const x = scaleTime().domain(domain).range([left, width - right]);
  const monthTicks = timeMonth.every(1).range(domain[0], domain[1]);

  return (
    <div style={{ overflowX: 'auto' }}>
      <svg viewBox={`0 0 ${width} ${height}`} width="100%" style={{ minWidth: 720 }}>
        {monthTicks.map((tick) => (
          <g key={tick.toISOString()}>
            <line x1={x(tick)} y1={top - 10} x2={x(tick)} y2={height - 18} stroke="#203249" strokeWidth="1" />
            <text x={x(tick)} y={20} fill="#b7c2d6" fontSize="11" textAnchor="middle">{timeFormat('%b')(tick)}</text>
          </g>
        ))}

        {rows.map((row, rowIndex) => {
          const y = top + rowIndex * rowHeight + 12;
          return (
            <g key={row}>
              <text x={left - 12} y={y + 4} textAnchor="end" fill="#edf2f7" fontSize="12">{row}</text>
              <line x1={left} y1={y} x2={width - right} y2={y} stroke="#29415e" strokeWidth="1" />
            </g>
          );
        })}

        {parsed.map((transit) => {
          const rowKey = `${transit.planet} ${transit.aspect} ${transit.natal_planet}`;
          const rowIndex = rows.indexOf(rowKey);
          const cy = top + rowIndex * rowHeight + 12;
          const radius = Math.max(5, 12 - Number(transit.orb || 0) * 2);
          return (
            <g key={`${rowKey}-${transit.date}`}>
              <circle cx={x(transit.parsedDate)} cy={cy} r={radius} fill={aspectColors[transit.aspect] || '#d2d6e3'} opacity="0.95" />
              <title>{`${transit.date}: ${transit.planet} ${transit.aspect} ${transit.natal_planet} (orb ${transit.orb}°)`}</title>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
