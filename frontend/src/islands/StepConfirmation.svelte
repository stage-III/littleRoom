<script lang="ts">
  import type { Booking } from '../lib/api';

  let { booking, isLoggedIn }: {
    booking: Booking;
    isLoggedIn: boolean;
  } = $props();

  const timeFmt = new Intl.DateTimeFormat('en-GB', {
    timeZone: 'Europe/London',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  });

  const dateFmt = new Intl.DateTimeFormat('en-GB', {
    timeZone: 'Europe/London',
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });

  const start = $derived(new Date(booking.start_datetime));
  const end = $derived(new Date(booking.end_datetime));

  const methodLabel = $derived(booking.payment_method === 'ON_DAY' ? 'Pay on the day' : 'Upfront');
</script>

<div class="confirmation">
  <div class="panel">
    <div class="tick">✓</div>
    <h2>Booking confirmed!</h2>
    <p class="booking-room">{booking.room.name}</p>
    <p class="booking-date">{dateFmt.format(start)}</p>
    <p class="booking-time">{timeFmt.format(start)} – {timeFmt.format(end)}</p>
    <p class="booking-payment">{methodLabel} · Pending</p>
  </div>

  <div class="actions">
    {#if isLoggedIn}
      <a href="/account" class="btn-secondary">View your bookings</a>
    {/if}
    <button class="btn-primary" onclick={() => window.location.reload()}>Book another room</button>
  </div>
</div>

<style>
  .confirmation { max-width: 420px; }

  .panel {
    background: #f0faf0;
    border: 1px solid #b0ddb0;
    border-radius: 8px;
    padding: 2rem 2rem 1.75rem;
    text-align: center;
    margin-bottom: 1.5rem;
  }

  .tick {
    font-size: 2rem;
    color: #2a7a2a;
    margin-bottom: 0.75rem;
  }

  h2 {
    font-size: 1.3rem;
    font-weight: 600;
    letter-spacing: -0.02em;
    margin-bottom: 1.25rem;
  }

  .booking-room {
    font-weight: 600;
    font-size: 1rem;
    margin-bottom: 0.3rem;
  }

  .booking-date,
  .booking-time {
    font-size: 0.9rem;
    color: #444;
    margin-bottom: 0.25rem;
  }

  .booking-payment {
    font-size: 0.8rem;
    color: #888;
    margin-top: 0.5rem;
  }

  .actions {
    display: flex;
    gap: 0.75rem;
    justify-content: center;
    flex-wrap: wrap;
  }

  .btn-primary {
    padding: 0.65rem 1.5rem;
    background: #1a1a1a;
    color: #fff;
    border: none;
    border-radius: 4px;
    font-size: 0.9rem;
    font-family: inherit;
    cursor: pointer;
    transition: background 0.15s;
  }

  .btn-primary:hover { background: #333; }

  .btn-secondary {
    padding: 0.65rem 1.5rem;
    background: #fff;
    color: #1a1a1a;
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    font-size: 0.9rem;
    transition: border-color 0.15s;
  }

  .btn-secondary:hover { border-color: #1a1a1a; }
</style>
