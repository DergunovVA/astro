import React from 'react';

const card = {
  background: '#111c2d',
  border: '1px solid #22344d',
  borderRadius: 12,
  padding: 16,
};

const verdictColors = {
  yes: '#3bb273',
  no: '#d94f4f',
  maybe: '#d0ab2f',
};

const AspectList = ({ title, items = [] }) => (
  <div style={card}>
    <h4 style={{ marginTop: 0 }}>{title}</h4>
    {items.length === 0 ? <div style={{ color: '#94a6c0' }}>No entries.</div> : items.map((item, index) => (
      <div key={`${item.planet1}-${item.planet2}-${index}`} style={{ padding: '8px 0', borderTop: index ? '1px solid rgba(148,166,192,0.18)' : 'none' }}>
        <strong>{item.planet1} {item.type} {item.planet2}</strong>
        <div style={{ color: '#9fb1c9', fontSize: 13 }}>Orb: {item.orb}° {item.timing?.is_applying ? `• ${item.timing.days} days` : ''}</div>
      </div>
    ))}
  </div>
);

export default function HoraryChartView({ data = {} }) {
  const question = data.question || {};
  const chart = data.chart || {};
  const significators = data.significators || {};
  const verdict = data.verdict || { answer: 'maybe', confidence: 0, rationale: 'No verdict supplied.' };

  return (
    <div style={{ display: 'grid', gap: 16 }}>
      <div style={{ ...card, display: 'grid', gap: 6 }}>
        <h3 style={{ margin: 0 }}>{question.text || 'Horary Question'}</h3>
        <div style={{ color: '#9fb1c9' }}>Type: {question.type || '—'} · Quesited house: {question.quesited_house ?? '—'}</div>
        <div style={{ color: '#9fb1c9' }}>{chart.local_datetime || chart.utc_datetime || 'Time unavailable'} · {chart.place || chart.name || 'Place unavailable'}</div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16 }}>
        {Object.entries(significators).map(([label, value]) => (
          <div key={label} style={card}>
            <div style={{ color: '#9fb1c9', textTransform: 'capitalize', marginBottom: 8 }}>{label}</div>
            <div style={{ fontSize: 22, fontWeight: 700 }}>{value.planet || '—'}</div>
            <div>{value.sign || '—'} · House {value.house ?? '—'}</div>
            <div style={{ color: '#9fb1c9' }}>{value.dignity || '—'} ({value.dignity_score ?? 0})</div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16 }}>
        <AspectList title="Applying aspects" items={data.applying_aspects} />
        <AspectList title="Separating aspects" items={data.separating_aspects} />
      </div>

      <div style={card}>
        <h4 style={{ marginTop: 0 }}>Receptions</h4>
        {(data.receptions || []).length === 0 ? <div style={{ color: '#94a6c0' }}>No receptions found.</div> : data.receptions.map((reception, index) => (
          <div key={`${reception.planet1}-${reception.planet2}-${index}`} style={{ padding: '8px 0', borderTop: index ? '1px solid rgba(148,166,192,0.18)' : 'none' }}>
            <strong>{reception.planet1} ↔ {reception.planet2}</strong>
            <div style={{ color: '#9fb1c9', fontSize: 13 }}>{reception.type}</div>
          </div>
        ))}
      </div>

      <div style={{ ...card, borderColor: verdictColors[verdict.answer] || '#22344d' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12 }}>
          <h4 style={{ margin: 0 }}>Verdict</h4>
          <span style={{ color: verdictColors[verdict.answer] || '#d0ab2f', fontWeight: 700, textTransform: 'uppercase' }}>{verdict.answer}</span>
        </div>
        <div style={{ marginTop: 8, color: '#9fb1c9' }}>Confidence: {Math.round((verdict.confidence || 0) * 100)}%</div>
        <p style={{ marginBottom: 0 }}>{verdict.rationale}</p>
      </div>
    </div>
  );
}
