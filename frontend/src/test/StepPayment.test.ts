import { render, screen } from '@testing-library/svelte';
import { userEvent } from '@testing-library/user-event';
import { describe, it, expect, vi, afterEach } from 'vitest';
import StepPayment from '../islands/StepPayment.svelte';
import type { AvailableRoom, Slot } from '../lib/api';

vi.mock('@stripe/stripe-js', () => ({ loadStripe: vi.fn().mockResolvedValue(null) }));

const room: AvailableRoom = {
  room_id: 1,
  name: 'Room A',
  slug: 'room-a',
  hourly_rate: '15.00',
  slots: [],
};

const slot: Slot = {
  start_time: '2026-05-01T09:00:00Z',
  max_hours: 3,
};

const baseProps = {
  room,
  slot,
  durationHours: 2,
  isLoggedIn: false,
  submitting: false,
  error: '',
  onConfirm: vi.fn(),
  onBack: vi.fn(),
};

describe('StepPayment', () => {
  it('shows room name and total price', () => {
    render(StepPayment, baseProps);
    expect(screen.getByText('Room A')).toBeInTheDocument();
    expect(screen.getByText(/£30\.00/)).toBeInTheDocument();
  });

  it('shows duration in summary', () => {
    render(StepPayment, baseProps);
    expect(screen.getByText('2h')).toBeInTheDocument();
  });

  it('shows guest name and email fields when not logged in', () => {
    render(StepPayment, baseProps);
    expect(screen.getByLabelText('Name')).toBeInTheDocument();
    expect(screen.getByLabelText('Email')).toBeInTheDocument();
  });

  it('hides guest fields when logged in', () => {
    render(StepPayment, { ...baseProps, isLoggedIn: true });
    expect(screen.queryByLabelText('Name')).not.toBeInTheDocument();
    expect(screen.queryByLabelText('Email')).not.toBeInTheDocument();
  });

  it('confirm button disabled for guest until name and email filled', async () => {
    render(StepPayment, baseProps);
    const submit = screen.getByRole('button', { name: /confirm booking/i });
    expect(submit).toBeDisabled();
    await userEvent.type(screen.getByLabelText('Name'), 'Alice');
    expect(submit).toBeDisabled();
    await userEvent.type(screen.getByLabelText('Email'), 'alice@example.com');
    expect(submit).not.toBeDisabled();
  });

  it('confirm button enabled immediately when logged in', () => {
    render(StepPayment, { ...baseProps, isLoggedIn: true });
    expect(screen.getByRole('button', { name: /confirm booking/i })).not.toBeDisabled();
  });

  it('hides "Pay on the day" option for guests', () => {
    render(StepPayment, baseProps);
    expect(screen.queryByLabelText(/pay on the day/i)).not.toBeInTheDocument();
  });

  it('shows "Pay on the day" option when logged in', () => {
    render(StepPayment, { ...baseProps, isLoggedIn: true });
    expect(screen.getByLabelText(/pay on the day/i)).toBeInTheDocument();
  });

  it('shows error banner when error prop is set', () => {
    render(StepPayment, { ...baseProps, error: 'This slot is no longer available.' });
    expect(screen.getByText('This slot is no longer available.')).toBeInTheDocument();
  });

  it('calls onConfirm with payment method, guest details, and undefined confirmPayment when no Stripe key', async () => {
    const onConfirm = vi.fn();
    render(StepPayment, { ...baseProps, onConfirm });
    await userEvent.type(screen.getByLabelText('Name'), 'Bob');
    await userEvent.type(screen.getByLabelText('Email'), 'bob@example.com');
    await userEvent.click(screen.getByRole('button', { name: /confirm booking/i }));
    expect(onConfirm).toHaveBeenCalledWith('UPFRONT', 'bob@example.com', 'Bob', undefined);
  });

  it('disables buttons while submitting', () => {
    render(StepPayment, { ...baseProps, isLoggedIn: true, submitting: true });
    expect(screen.getByText('Confirming…')).toBeDisabled();
    expect(screen.getByText('← Back')).toBeDisabled();
  });

  it('calls onBack when back is clicked', async () => {
    const onBack = vi.fn();
    render(StepPayment, { ...baseProps, isLoggedIn: true, onBack });
    await userEvent.click(screen.getByText('← Back'));
    expect(onBack).toHaveBeenCalled();
  });
});

describe('StepPayment — Stripe card element', () => {
  afterEach(() => {
    vi.unstubAllEnvs();
    vi.clearAllMocks();
  });

  it('does not render card element container without a Stripe key', () => {
    render(StepPayment, { ...baseProps, isLoggedIn: true });
    expect(document.querySelector('.card-element')).not.toBeInTheDocument();
  });

  it('renders card element container when Stripe key is present and UPFRONT selected', () => {
    vi.stubEnv('PUBLIC_STRIPE_KEY', 'pk_test_xxx');
    render(StepPayment, { ...baseProps, isLoggedIn: true });
    expect(document.querySelector('.card-element')).toBeInTheDocument();
  });

  it('does not render card element container when ON_DAY selected', async () => {
    vi.stubEnv('PUBLIC_STRIPE_KEY', 'pk_test_xxx');
    render(StepPayment, { ...baseProps, isLoggedIn: true });
    await userEvent.click(screen.getByLabelText(/pay on the day/i));
    expect(document.querySelector('.card-element')).not.toBeInTheDocument();
  });
});
