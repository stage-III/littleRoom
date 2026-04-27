<script lang="ts">
  import type { Booking } from "../lib/api";

  let {
    booking,
    isLoggedIn,
  }: {
    booking: Booking;
    isLoggedIn: boolean;
  } = $props();

  const timeFmt = new Intl.DateTimeFormat("en-GB", {
    timeZone: "Europe/London",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });

  const dateFmt = new Intl.DateTimeFormat("en-GB", {
    timeZone: "Europe/London",
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  const start = $derived(new Date(booking.start_datetime));
  const end = $derived(new Date(booking.end_datetime));

  const methodLabel = $derived(
    booking.payment_method === "ON_DAY" ? "Pay on the day" : "Upfront",
  );
</script>

<div class="confirmation">
  <div class="panel">
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
    <button class="btn-primary" onclick={() => window.location.reload()}
      >Book another room</button
    >
  </div>
</div>

<style>
  .confirmation {
    max-width: 420px;
  }

  .panel {
    background: var(--ok-bg);
    border: 1px solid var(--ok-border);
    padding: 2rem 2rem 1.75rem;
    text-align: center;
    margin-bottom: 1.75rem;
  }

  h2 {
    font-family: var(--font-title);
    font-weight: 700;
    font-size: 1.8rem;
    text-transform: lowercase;
    letter-spacing: 0.02em;
    color: var(--ok-text);
    margin-bottom: 1.5rem;
  }

  .booking-room {
    font-family: var(--font-title);
    font-weight: 700;
    font-size: 1.4rem;
    text-transform: lowercase;
    letter-spacing: 0.02em;
    color: var(--text);
    margin-bottom: 0.4rem;
  }

  .booking-date,
  .booking-time {
    font-size: 1.05rem;
    color: var(--text-muted);
    margin-bottom: 0.25rem;
    letter-spacing: 0.03em;
  }

  .booking-payment {
    font-size: 1.05rem;
    color: var(--text-faint);
    margin-top: 0.6rem;
    letter-spacing: 0.06em;
  }

  .actions {
    display: flex;
    gap: 0.75rem;
    justify-content: center;
    flex-wrap: wrap;
  }

  .btn-primary {
    padding: 0.65rem 1.5rem;
    background: var(--accent);
    color: var(--accent-fg);
    border: 1px solid var(--accent);
    font-size: 1.05rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    font-family: inherit;
    cursor: pointer;
    transition: background 0.15s;
  }

  .btn-primary:hover {
    background: var(--accent-hover);
    border-color: var(--accent-hover);
  }

  .btn-secondary {
    padding: 0.65rem 1.5rem;
    background: transparent;
    color: var(--text-muted);
    border: 1px solid var(--border);
    font-size: 1.05rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    transition:
      border-color 0.15s,
      color 0.15s;
  }

  .btn-secondary:hover {
    border-color: var(--accent);
    color: var(--text);
  }
</style>
