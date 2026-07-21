import { render, screen, waitFor } from '@testing-library/react';
import React from 'react';
import { afterEach, vi } from 'vitest';

import { IncidentPipeline } from '../src/views/IncidentPipeline';
import { SystemOverview } from '../src/views/SystemOverview';

afterEach(() => {
  vi.restoreAllMocks();
});

it('shows loading then systems', async () => {
  const fetchMock = vi
    .spyOn(globalThis, 'fetch')
    .mockResolvedValueOnce(
      new Response(JSON.stringify([{ id: 'sys-1', name: 'Core', description: '', status: 'active' }]), {
        status: 200
      })
    )
    .mockResolvedValueOnce(
      new Response(JSON.stringify({ averages: [{ metric_id: 'm1', metric_name: 'risk_score', average: 88 }] }), {
        status: 200
      })
    );

  render(<SystemOverview />);
  expect(screen.getByText('Loading systems...')).toBeInTheDocument();

  await waitFor(() => expect(screen.getByText('Core')).toBeInTheDocument());
  expect(fetchMock).toHaveBeenCalledTimes(2);
});

it('renders empty incident state', async () => {
  vi.spyOn(globalThis, 'fetch').mockResolvedValue(
    new Response(JSON.stringify([]), {
      status: 200
    })
  );

  render(<IncidentPipeline />);
  await waitFor(() => expect(screen.getByText('No incidents found.')).toBeInTheDocument());
});
