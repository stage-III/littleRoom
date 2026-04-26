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
    font-size: 1.8rem;
    letter-spacing: -0.03em;
  }

  h2 {
    font-size: 1.1rem;
    font-weight: 600;
    letter-spacing: -0.01em;
    margin-bottom: 1.25rem;
    color: #444;
    text-transform: uppercase;
    font-size: 0.75rem;
    letter-spacing: 0.08em;
  }

  .logout-btn {
    background: none;
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    padding: 0.4rem 0.9rem;
    font-size: 0.875rem;
    font-family: inherit;
    cursor: pointer;
    color: #555;
    transition: border-color 0.15s, color 0.15s;
  }

  .logout-btn:hover:not(:disabled) {
    border-color: #1a1a1a;
    color: #1a1a1a;
  }

  .logout-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .loading-msg {
    color: #888;
  }

  .error-banner {
    background: #fff0f0;
    border: 1px solid #fcc;
    color: #c00;
    padding: 0.75rem 1rem;
    border-radius: 4px;
    font-size: 0.9rem;
  }

  .empty {
    color: #888;
  }

  .booking-list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .booking-card {
    border: 1px solid #e5e5e5;
    border-radius: 6px;
    padding: 1rem 1.25rem;
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
  }

  .booking-room {
    font-weight: 600;
    font-size: 1rem;
  }

  .booking-time {
    font-size: 0.9rem;
    color: #333;
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
  }

  .booking-date {
    color: #555;
  }

  .booking-hours {
    font-variant-numeric: tabular-nums;
  }

  .booking-meta {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.8rem;
    margin-top: 0.15rem;
  }

  .sep {
    color: #bbb;
  }

  .tag {
    color: #555;
  }

  .status-paid { color: #2a7a2a; }
  .status-refunded { color: #888; }
  .status-pending { color: #b06000; }
</style>
