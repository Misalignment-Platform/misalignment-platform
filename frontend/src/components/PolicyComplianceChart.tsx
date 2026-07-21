import React from 'react';

import type { MetricAverage } from '../api/client';

type PolicyComplianceChartProps = {
  data: MetricAverage[];
};

export function PolicyComplianceChart({ data }: PolicyComplianceChartProps) {
  if (!data.length) {
    return <p>No policy trend data.</p>;
  }

  return (
    <ul>
      {data.map((entry) => (
        <li key={entry.metric_id}>
          <strong>{entry.metric_name}</strong>: {entry.average.toFixed(1)}
        </li>
      ))}
    </ul>
  );
}
