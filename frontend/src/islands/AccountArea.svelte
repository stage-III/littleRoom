<script lang="ts">
  import { api, type Booking } from '../lib/api';

  let bookings: Booking[] = $state([]);
  let loading = $state(true);
  let error = $state('');
  let loggingOut = $state(false);

  const dateFmt = new Intl.DateTimeFormat('en-GB', {
    timeZone: 'Europe/London',
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });

  const timeFmt = new Intl.DateTimeFormat('en-GB', {
    timeZone: 'Europe/London',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  });

  function formatBooking(start: string, end: string): { date: string; time: string; duration: string } {
    const s = new Date(start);
    const e = new Date(end);
    const hours = (e.getTime() - s.getTime()) / 3_600_000;
    return {
      date: dateFmt.format(s),
      time: `${timeFmt.format(s)} – ${timeFmt.format(e)}`,
      duration: `${hours}h`,
    };
  }

  function methodLabel(m: string) {
    return m === 'ON_DAY' ? 'Pay on the day' : 'Upfront';
  }

  function statusLabel(s: string) {
    if (s === 'PAID') return 'Paid';
    if (s === 'REFUNDED') return 'Refunded';
    return 'Pending';
  }

  $effect(() => {
    if (!localStorage.getItem('token')) {
      window.location.href = '/login';
      return;
    }

    api.get<Booking[]>('/bookings/mine/')
      .then(data => {
        bookings = [...data].sort(
          (a, b) => new Date(b.start_datetime).getTime() - new Date(a.start_datetime).getTime()
        );
        loading = false;
      })
      .catch((err: { status?: number }) => {
        if (err.status === 401) {
          localStorage.removeItem('token');
          window.location.href = '/login';
        } else {
          error = 'Could not load bookings. Please try again.';
          loading = false;
        }
      });
  });

  async function logout() {
    loggingOut = true;
    try {
      await api.post<unknown>('/auth/logout/', {});
    } finally {
      localStorage.removeItem('token');
      window.location.href = '/';
    }
  }
</script>

<div class="account-wrap">
  <div class="account-header">
    <h1>My Account</h1>
    <button onclick={logout} disabled={loggingOut} class="logout-btn">
      {loggingOut ? 'Logging out…' : 'Log out'}
    </button>
  </div>

  {#if loading}
    <p class="loading-msg">Loading…</p>
  {:else if error}
    <p class="error-banner">{error}</p>
  {:else}
    <section>
      <h2>Your Bookings</h2>
      {#if bookings.length === 0}
        <p class="empty">No bookings yet.</p>
      {:else}
        <ul class="booking-list">
          {#each bookings as booking}
            {@const fmt = formatBooking(booking.start_datetime, booking.end_datetime)}
            <li class="booking-card">
              <div class="booking-room">{booking.room.name}</div>
              <div class="booking-time">
                <span class="booking-date">{fmt.date}</span>
                <span class="booking-hours">{fmt.time} ({fmt.duration})</span>
              </div>
              <div class="booking-meta">
                <span class="tag">{methodLabel(booking.payment_method)}</span>
                <span class="sep">·</span>
                <span class="tag status-{booking.payment_status.toLowerCase()}">{statusLabel(booking.payment_status)}</span>
              </div>
            </li>
          {/each}
        </ul>
      {/if}
    </section>
  {/if}
</div>

<style>
  .account-wrap {
    max-width: 600px;
    margin: 0 auto;
  }

  .account-header {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    margin-bottom: 2.5rem;
  }

  h1 {
    font-family: var(--font-title);
    font-weight: 700;
    font-size: 1.8rem;
    text-transform: lowercase;
    letter-spacing: 0.02em;
    color: var(--accent);
  }

  h2 {
    font-family: var(--font-ui);
    font-weight: 300;
    font-size: 0.95rem;
    text-transform: uppercase;
    color: var(--text-muted);
    letter-spacing: 0.14em;
    margin-bottom: 1.25rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
  }

  .logout-btn {
    background: none;
    border: 1px solid var(--border);
    padding: 0.4rem 0.9rem;
    font-size: 0.7rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    font-family: inherit;
    cursor: pointer;
    color: var(--text-muted);
    transition: border-color 0.15s, color 0.15s;
  }

  .logout-btn:hover:not(:disabled) {
    border-color: var(--text-muted);
    color: var(--text);
  }

  .logout-btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  .loading-msg {
    color: var(--text-faint);
    font-size: 0.875rem;
  }

  .error-banner {
    background: var(--err-bg);
    border: 1px solid var(--err-border);
    color: var(--err-text);
    padding: 0.75rem 1rem;
    font-size: 0.875rem;
  }

  .empty {
    color: var(--text-faint);
    font-size: 0.875rem;
  }

  .booking-list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
  }

  .booking-card {
    border: 1px solid var(--border);
    background: var(--surface);
    padding: 1rem 1.25rem;
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
    transition: border-color 0.15s;
  }

  .booking-card:hover { border-color: var(--accent); }

  .booking-room {
    font-family: var(--font-title);
    font-weight: 700;
    font-size: 1rem;
    text-transform: lowercase;
    letter-spacing: 0.02em;
    color: var(--text);
  }

  .booking-time {
    font-size: 0.85rem;
    color: var(--text-muted);
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
  }

  .booking-date {
    color: var(--text-muted);
  }

  .booking-hours {
    font-variant-numeric: tabular-nums;
    color: var(--silver);
  }

  .booking-meta {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.75rem;
    margin-top: 0.15rem;
    letter-spacing: 0.04em;
  }

  .sep {
    color: var(--text-faint);
  }

  .tag {
    color: var(--text-muted);
  }

  .status-paid { color: var(--ok-text); }
  .status-refunded { color: var(--text-faint); }
  .status-pending { color: var(--warn-text); }
</style>
