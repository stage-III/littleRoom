import { render, screen } from '@testing-library/svelte';
import { userEvent } from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import StepSlot from '../islands/StepSlot.svelte';
import type { AvailableRoom } from '../lib/api';

const room: AvailableRoom = {
  room_id: 1,
  name: 'Room A',
  slug: 'room-a',
  hourly_rate: '15.00',
  slots: [
    { start_time: '2026-05-01T09:00:00Z', max_hours: 3 },
    { start_time: '2026-05-01T10:00:00Z', max_hours: 2 },
  ],
};

describe('StepSlot', () => {
  it('renders slot buttons for each slot', () => {
    render(StepSlot, { room, minBookingHours: 1, onConfirm: vi.fn(), onBack: vi.fn() });
    // Two time-slot buttons should exist
    const buttons = screen.getAllByRole('button');
    // Back + Next + 2 slot buttons = 4, but Next is disabled initially
    const slotButtons = buttons.filter(b => !['← Back', 'Next →'].includes(b.textContent?.trim() ?? ''));
    expect(slotButtons).toHaveLength(2);
  });

  it('Next button is disabled before a slot is chosen', () => {
    render(StepSlot, { room, minBookingHours: 1, onConfirm: vi.fn(), onBack: vi.fn() });
    expect(screen.getByText('Next →')).toBeDisabled();
  });

  it('shows duration options after selecting a slot', async () => {
    render(StepSlot, { room, minBookingHours: 1, onConfirm: vi.fn(), onBack: vi.fn() });
    const slotBtns = screen.getAllByRole('button').filter(
      b => !['← Back', 'Next →'].includes(b.textContent?.trim() ?? '')
    );
    await userEvent.click(slotBtns[0]); // first slot: max_hours=3
    expect(screen.getByText('1h')).toBeInTheDocument();
    expect(screen.getByText('2h')).toBeInTheDocument();
    expect(screen.getByText('3h')).toBeInTheDocument();
  });

  it('shows price summary after selecting slot and duration', async () => {
    render(StepSlot, { room, minBookingHours: 1, onConfirm: vi.fn(), onBack: vi.fn() });
    const slotBtns = screen.getAllByRole('button').filter(
      b => !['← Back', 'Next →'].includes(b.textContent?.trim() ?? '')
    );
    await userEvent.click(slotBtns[0]);
    await userEvent.click(screen.getByText('2h'));
    expect(screen.getByText(/£30\.00/)).toBeInTheDocument();
  });

  it('calls onConfirm with the selected slot and hours', async () => {
    const onConfirm = vi.fn();
    render(StepSlot, { room, minBookingHours: 1, onConfirm, onBack: vi.fn() });
    const slotBtns = screen.getAllByRole('button').filter(
      b => !['← Back', 'Next →'].includes(b.textContent?.trim() ?? '')
    );
    await userEvent.click(slotBtns[0]);
    await userEvent.click(screen.getByText('1h'));
    await userEvent.click(screen.getByText('Next →'));
    expect(onConfirm).toHaveBeenCalledWith(room.slots[0], 1);
  });

  it('calls onBack when back is clicked', async () => {
    const onBack = vi.fn();
    render(StepSlot, { room, minBookingHours: 1, onConfirm: vi.fn(), onBack });
    await userEvent.click(screen.getByText('← Back'));
    expect(onBack).toHaveBeenCalled();
  });

  it('respects minBookingHours — no shorter options shown', async () => {
    render(StepSlot, { room, minBookingHours: 2, onConfirm: vi.fn(), onBack: vi.fn() });
    const slotBtns = screen.getAllByRole('button').filter(
      b => !['← Back', 'Next →'].includes(b.textContent?.trim() ?? '')
    );
    await userEvent.click(slotBtns[0]);
    expect(screen.queryByText('1h')).not.toBeInTheDocument();
    expect(screen.getByText('2h')).toBeInTheDocument();
  });
});
