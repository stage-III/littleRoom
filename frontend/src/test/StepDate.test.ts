import { render, screen, waitFor } from '@testing-library/svelte';
import { userEvent } from '@testing-library/user-event';
import { describe, it, expect, vi, afterEach } from 'vitest';
import StepDate from '../islands/StepDate.svelte';
import type { AvailabilityResponse } from '../lib/api';

// Mock the api module
vi.mock('../lib/api', async () => {
  const actual = await vi.importActual<typeof import('../lib/api')>('../lib/api');
  return { ...actual, api: { get: vi.fn(), post: vi.fn() } };
});

import { api } from '../lib/api';

const openAvail: AvailabilityResponse = {
  is_open: true,
  date: '2026-05-01',
  open_time: '09:00',
  close_time: '22:00',
  rooms: [
    { room_id: 1, name: 'Room A', slug: 'room-a', hourly_rate: '15.00', slots: [{ start_time: '2026-05-01T09:00:00Z', max_hours: 2 }] },
  ],
};

const closedAvail: AvailabilityResponse = {
  is_open: false,
  date: '2026-05-01',
  rooms: [],
};

const noSlotsAvail: AvailabilityResponse = {
  is_open: true,
  date: '2026-05-01',
  open_time: '09:00',
  close_time: '22:00',
  rooms: [
    { room_id: 1, name: 'Room A', slug: 'room-a', hourly_rate: '15.00', slots: [] },
  ],
};

afterEach(() => vi.clearAllMocks());

describe('StepDate', () => {
  it('renders date input and check button', () => {
    render(StepDate, { initialDate: '2026-05-01', minDate: '2026-05-01', onConfirm: vi.fn() });
    expect(screen.getByLabelText('Date')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /check availability/i })).toBeInTheDocument();
  });

  it('button is disabled when date is empty', async () => {
    render(StepDate, { initialDate: '', minDate: '', onConfirm: vi.fn() });
    expect(screen.getByRole('button', { name: /check availability/i })).toBeDisabled();
  });

  it('calls onConfirm with date and availability on success', async () => {
    vi.mocked(api.get).mockResolvedValueOnce(openAvail);
    const onConfirm = vi.fn();
    render(StepDate, { initialDate: '2026-05-01', minDate: '2026-05-01', onConfirm });
    await userEvent.click(screen.getByRole('button', { name: /check availability/i }));
    await waitFor(() => expect(onConfirm).toHaveBeenCalledWith('2026-05-01', openAvail));
  });

  it('shows closed notice when studio is closed', async () => {
    vi.mocked(api.get).mockResolvedValueOnce(closedAvail);
    render(StepDate, { initialDate: '2026-05-01', minDate: '2026-05-01', onConfirm: vi.fn() });
    await userEvent.click(screen.getByRole('button', { name: /check availability/i }));
    await waitFor(() => expect(screen.getByText(/studio is closed/i)).toBeInTheDocument());
  });

  it('shows fully booked notice when no slots', async () => {
    vi.mocked(api.get).mockResolvedValueOnce(noSlotsAvail);
    render(StepDate, { initialDate: '2026-05-01', minDate: '2026-05-01', onConfirm: vi.fn() });
    await userEvent.click(screen.getByRole('button', { name: /check availability/i }));
    await waitFor(() => expect(screen.getByText(/fully booked/i)).toBeInTheDocument());
  });

  it('shows error notice on API failure', async () => {
    vi.mocked(api.get).mockRejectedValueOnce(new Error('network error'));
    render(StepDate, { initialDate: '2026-05-01', minDate: '2026-05-01', onConfirm: vi.fn() });
    await userEvent.click(screen.getByRole('button', { name: /check availability/i }));
    await waitFor(() => expect(screen.getByText(/could not load/i)).toBeInTheDocument());
  });
});
