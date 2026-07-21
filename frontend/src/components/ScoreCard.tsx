import React from 'react';

type ScoreCardProps = {
  label: string;
  value: number;
};

export function ScoreCard({ label, value }: ScoreCardProps) {
  return (
    <article>
      <h3>{label}</h3>
      <p>{value.toFixed(1)}</p>
    </article>
  );
}
