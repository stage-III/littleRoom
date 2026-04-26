import { render, screen } from '@testing-library/svelte';
import { describe, it, expect } from 'vitest';
import StepConfirmation from '../islands/StepConfirmation.svelte';
import type { Booking } from '../lib/api';

const booking: Booking = {
  id: 42,
  room: { id: 1, name: 'Room A', slug: 'room-a' },
  start_datetime: '2026-05-01T09:00:00Z',
  end_datetime: '2026-05-01T11:00:00Z',
  payment_method: 'UPFRONT',
  payment_status: 'PENDING',
  created_at: '2026-04-20T12:00:00Z',
};

describe('StepConfirmation', () => {
  it('shows confirmed heading', () => {
    render(StepConfirmation, { booking, isLoggedIn: false });
    expect(screen.getByText(/booking confirmed/i)).toBeInTheDocument();
  });

  it('shows room name', () => {
    render(StepConfirmation, { booking, isLoggedIn: false });
    expect(screen.getByText('Room A')).toBeInTheDocument();
  });

  it('shows payment method label for UPFRONT', () => {
    render(StepConfirmation, { booking, isLoggedIn: false });
    expect(screen.getByText(/upfront/i)).toBeInTheDocument();
  });

  it('shows payment method label for ON_DAY', () => {
    const onDayBooking: Booking = { ...booking, payment_method: 'ON_DAY' };
    render(StepConfirmation, { booking: onDayBooking, isLoggedIn: false });
    expect(screen.getByText(/pay on the day/i)).toBeInTheDocument();
  });

  it('shows "View your bookings" link when logged in', () => {
    render(StepConfirmation, { booking, isLoggedIn: true });
    expect(screen.getByRole('link', { name: /view your bookings/i })).toBeInTheDocument();
  });

  it('hides "View your bookings" link when not logged in', () => {
    render(StepConfirmation, { booking, isLoggedIn: false });
    expect(screen.queryByRole('link', { name: /view your bookings/i })).not.toBeInTheDocument();
  });

  it('shows "Book another room" button', () => {
    render(StepConfirmation, { booking, isLoggedIn: false });
    expect(screen.getByRole('button', { name: /book another room/i })).toBeInTheDocument();
  });
});
