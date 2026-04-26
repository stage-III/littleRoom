import { render, screen } from '@testing-library/svelte';
import { userEvent } from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import StepRoom from '../islands/StepRoom.svelte';
import type { AvailabilityResponse } from '../lib/api';

const baseAvailability: AvailabilityResponse = {
  is_open: true,
  date: '2026-05-01',
  open_time: '09:00',
  close_time: '22:00',
  rooms: [
    {
      room_id: 1,
      name: 'Room A',
      slug: 'room-a',
      hourly_rate: '15.00',
      slots: [
        { start_time: '2026-05-01T09:00:00Z', max_hours: 3 },
        { start_time: '2026-05-01T10:00:00Z', max_hours: 2 },
      ],
    },
    {
      room_id: 2,
      name: 'Room B',
      slug: 'room-b',
      hourly_rate: '20.00',
      slots: [
        { start_time: '2026-05-01T09:00:00Z', max_hours: 4 },
      ],
    },
  ],
};

describe('StepRoom', () => {
  it('renders a card for each room with slots', () => {
    render(StepRoom, { availability: baseAvailability, onConfirm: vi.fn(), onBack: vi.fn() });
    expect(screen.getByText('Room A')).toBeInTheDocument();
    expect(screen.getByText('Room B')).toBeInTheDocument();
  });

  it('shows hourly rate and slot count', () => {
    render(StepRoom, { availability: baseAvailability, onConfirm: vi.fn(), onBack: vi.fn() });
    expect(screen.getByText(/£15\.00\/hr/)).toBeInTheDocument();
    expect(screen.getByText(/2 slots available/)).toBeInTheDocument();
    expect(screen.getByText(/1 slot available/)).toBeInTheDocument();
  });

  it('calls onConfirm with the clicked room', async () => {
    const onConfirm = vi.fn();
    render(StepRoom, { availability: baseAvailability, onConfirm, onBack: vi.fn() });
    await userEvent.click(screen.getByText('Room A').closest('button')!);
    expect(onConfirm).toHaveBeenCalledWith(baseAvailability.rooms[0]);
  });

  it('shows a no-rooms notice when all rooms have no slots', () => {
    const noSlots: AvailabilityResponse = {
      ...baseAvailability,
      rooms: [{ room_id: 1, name: 'Room A', slug: 'room-a', hourly_rate: '15.00', slots: [] }],
    };
    render(StepRoom, { availability: noSlots, onConfirm: vi.fn(), onBack: vi.fn() });
    expect(screen.getByText(/no rooms available/i)).toBeInTheDocument();
  });

  it('calls onBack when back is clicked', async () => {
    const onBack = vi.fn();
    render(StepRoom, { availability: baseAvailability, onConfirm: vi.fn(), onBack });
    await userEvent.click(screen.getByText(/back/i));
    expect(onBack).toHaveBeenCalled();
  });
});
