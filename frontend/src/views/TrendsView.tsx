import React, { useEffect, useState } from 'react';

import { apiClient, type MetricAverage } from '../api/client';
import { ScoreCard } from '../components/ScoreCard';

type TrendsViewProps = {
  systemId?: string;
};

export function TrendsView({ systemId }: TrendsViewProps) {
  const [trends, setTrends] = useState<MetricAverage[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const response = await apiClient.listMetricTrends(systemId);
        setTrends(response.averages);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load trends');
      } finally {
        setLoading(false);
      }
    }

    void load();
  }, [systemId]);

  if (loading) return <p>Loading trends...</p>;
  if (error) return <p role="alert">{error}</p>;
  if (!trends.length) return <p>No trend data available.</p>;

  return (
    <section>
      <h2>Metric Trends</h2>
      {trends.map((trend) => (
        <ScoreCard key={trend.metric_id} label={trend.metric_name} value={trend.average} />
      ))}
    </section>
  );
}
