import React, { useEffect, useState } from 'react';

import { apiClient, type MetricAverage } from '../api/client';
import { PolicyComplianceChart } from '../components/PolicyComplianceChart';

type PolicyViewProps = {
  policyId?: string;
};

export function PolicyView({ policyId }: PolicyViewProps) {
  const [trends, setTrends] = useState<MetricAverage[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const response = await apiClient.listPolicyMetrics(policyId);
        setTrends(response.averages);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load policy trends');
      } finally {
        setLoading(false);
      }
    }

    void load();
  }, [policyId]);

  if (loading) return <p>Loading policy data...</p>;
  if (error) return <p role="alert">{error}</p>;

  return (
    <section>
      <h2>Policy Governance</h2>
      <PolicyComplianceChart data={trends} />
    </section>
  );
}
