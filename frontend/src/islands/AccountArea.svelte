<script lang="ts">
  import { api, type Booking, type StudioSettings } from '../lib/api';

  let bookings: Booking[] = $state([]);
  let settings = $state<StudioSettings | null>(null);
  let loading = $state(true);
  let error = $state('');
  let loggingOut = $state(false);
  let cancellingId = $state<number | null>(null);
  let cancelError = $state('');

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

    Promise.all([
      api.get<Booking[]>('/bookings/mine/'),
      api.get<StudioSettings>('/settings/'),
    ])
      .then(([bookingData, settingsData]) => {
        bookings = [...bookingData].sort(
          (a, b) => new Date(b.start_datetime).getTime() - new Date(a.start_datetime).getTime()
        );
        settings = settingsData;
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

  function isCancellable(booking: Booking): boolean {
    if (booking.is_cancelled) return false;
    if (!settings) return false;
    const cutoff = new Date(booking.start_datetime);
    cutoff.setDate(cutoff.getDate() - settings.min_cancellation_notice_days);
    return new Date() < cutoff;
  }

  async function cancelBooking(booking: Booking) {
    const notice = settings?.min_cancellation_notice_days ?? 1;
    if (!confirm(`Cancel this booking? ${booking.payment_status === 'PAID' ? 'You will be refunded.' : ''}\n\nNote: cancellations must be made at least ${notice} day(s) before the session.`)) return;
    cancellingId = booking.id;
    cancelError = '';
    try {
      const updated = await api.post<Booking>(`/bookings/${booking.id}/cancel/`, {});
      bookings = bookings.map(b => b.id === updated.id ? updated : b);
    } catch (err: unknown) {
      const e = err as { data?: { detail?: string } };
      cancelError = e.data?.detail ?? 'Could not cancel booking. Please try again.';
    } finally {
      cancellingId = null;
    }
  }

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
      {#if cancelError}
        <p class="error-banner">{cancelError}</p>
      {/if}
      {#if bookings.length === 0}
        <p class="empty">No bookings yet.</p>
      {:else}
        <ul class="booking-list">
          {#each bookings as booking}
            {@const fmt = formatBooking(booking.start_datetime, booking.end_datetime)}
            <li class="booking-card" class:cancelled={booking.is_cancelled}>
              <div class="booking-room">{booking.room.name}</div>
              <div class="booking-time">
                <span class="booking-date">{fmt.date}</span>
                <span class="booking-hours">{fmt.time} ({fmt.duration})</span>
              </div>
              <div class="booking-footer">
                <div class="booking-meta">
                  {#if booking.is_cancelled}
                    <span class="tag status-cancelled">Cancelled</span>
                    {#if booking.payment_status === 'REFUNDED'}
                      <span class="sep">·</span>
                      <span class="tag status-refunded">Refunded</span>
                    {:else if booking.payment_status === 'PAID'}
                      <span class="sep">·</span>
                      <span class="tag status-pending">Refund pending</span>
                    {/if}
                  {:else}
                    <span class="tag">{methodLabel(booking.payment_method)}</span>
                    <span class="sep">·</span>
                    <span class="tag status-{booking.payment_status.toLowerCase()}">{statusLabel(booking.payment_status)}</span>
                  {/if}
                  <span class="sep">·</span>
                  <span class="booking-cost">£{booking.total_cost}</span>
                </div>
                {#if isCancellable(booking)}
                  <button
                    class="cancel-btn"
                    disabled={cancellingId === booking.id}
                    onclick={() => cancelBooking(booking)}
                  >
                    {cancellingId === booking.id ? 'Cancelling…' : 'Cancel'}
                  </button>
                {/if}
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
    font-size: 2rem;
    text-transform: lowercase;
    letter-spacing: 0.02em;
    color: var(--accent);
  }

  h2 {
    font-family: var(--font-ui);
    font-weight: 300;
    font-size: 1.4rem;
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
    font-size: 0.97rem;
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
    color: var(--text-muted);
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
    color: var(--text-muted);
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
    font-size: 1.4rem;
    text-transform: lowercase;
    letter-spacing: 0.02em;
    color: var(--text);
  }

  .booking-time {
    font-size: 1.05rem;
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

  .booking-cost {
    font-variant-numeric: tabular-nums;
    color: var(--text-muted);
  }

  .booking-meta {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.95rem;
    margin-top: 0.15rem;
    letter-spacing: 0.04em;
  }

  .sep {
    color: var(--text-muted);
  }

  .tag {
    color: var(--text-muted);
  }

  .status-paid { color: var(--ok-text); }
  .status-refunded { color: var(--text-muted); }
  .status-pending { color: var(--warn-text); }
  .status-cancelled { color: var(--text-muted); }

  .booking-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
    margin-top: 0.15rem;
  }

  .cancel-btn {
    background: none;
    border: 1px solid var(--border);
    padding: 0.25rem 0.75rem;
    font-size: 0.85rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-family: inherit;
    cursor: pointer;
    color: var(--text-muted);
    transition: border-color 0.15s, color 0.15s;
    flex-shrink: 0;
  }

  .cancel-btn:hover:not(:disabled) {
    border-color: var(--err-border);
    color: var(--err-text);
  }

  .cancel-btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  .booking-card.cancelled {
    opacity: 0.5;
  }
</style>
