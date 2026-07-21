import React from 'react';

import type { EventRecord } from '../api/client';

type IncidentTableProps = {
  incidents: EventRecord[];
};

export function IncidentTable({ incidents }: IncidentTableProps) {
  if (!incidents.length) {
    return <p>No incidents found.</p>;
  }

  return (
    <table>
      <thead>
        <tr>
          <th>Source</th>
          <th>Type</th>
          <th>Risk</th>
          <th>State</th>
        </tr>
      </thead>
      <tbody>
        {incidents.map((incident) => (
          <tr key={incident.id}>
            <td>{incident.source}</td>
            <td>{incident.incident_type}</td>
            <td>{incident.risk_category}</td>
            <td>{incident.state}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
