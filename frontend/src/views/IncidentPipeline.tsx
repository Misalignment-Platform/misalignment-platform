import React, { useEffect, useState } from 'react';

import { apiClient, type EventRecord } from '../api/client';
import { IncidentTable } from '../components/IncidentTable';

export function IncidentPipeline() {
  const [events, setEvents] = useState<EventRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        setEvents(await apiClient.listEvents());
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load incidents');
      } finally {
        setLoading(false);
      }
    }

    void load();
  }, []);

  if (loading) return <p>Loading incidents...</p>;
  if (error) return <p role="alert">{error}</p>;

  return (
    <section>
      <h2>Incident Pipeline</h2>
      <IncidentTable incidents={events} />
    </section>
  );
}
