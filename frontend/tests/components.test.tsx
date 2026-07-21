import { render, screen } from '@testing-library/react';
import React from 'react';

import { IncidentTable } from '../src/components/IncidentTable';
import { ScoreCard } from '../src/components/ScoreCard';

it('renders score card value', () => {
  render(<ScoreCard label="risk_score" value={42.3} />);
  expect(screen.getByText('risk_score')).toBeInTheDocument();
  expect(screen.getByText('42.3')).toBeInTheDocument();
});

it('renders incident rows', () => {
  render(
    <IncidentTable
      incidents={[
        {
          id: 'evt-1',
          system_id: 'sys-1',
          source: 'webhook',
          content: 'warning',
          risk_category: 'high',
          state: 'open',
          incident_type: 'policy-violation'
        }
      ]}
    />
  );
  expect(screen.getByText('policy-violation')).toBeInTheDocument();
});
