import React, { useEffect, useState } from 'react';

import { apiClient, type MetricAverage, type SystemRecord } from '../api/client';
import { ScoreCard } from '../components/ScoreCard';

export function SystemOverview() {
  const [systems, setSystems] = useState<SystemRecord[]>([]);
  const [metrics, setMetrics] = useState<MetricAverage[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const systemResults = await apiClient.listSystems();
        setSystems(systemResults);
        if (systemResults.length > 0) {
          const trends = await apiClient.listMetricTrends(systemResults[0].id);
          setMetrics(trends.averages);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load systems');
      } finally {
        setLoading(false);
      }
    }

    void load();
  }, []);

  if (loading) return <p>Loading systems...</p>;
  if (error) return <p role="alert">{error}</p>;
  if (!systems.length) return <p>No systems registered.</p>;

  return (
    <section>
      <h2>System Overview</h2>
      <p>{systems[0].name}</p>
      <div>
        {metrics.map((metric) => (
          <ScoreCard key={metric.metric_id} label={metric.metric_name} value={metric.average} />
        ))}
      </div>
    </section>
  );
}
