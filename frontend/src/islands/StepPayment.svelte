<script lang="ts">
  import type { AvailableRoom, Slot } from '../lib/api';

  let { room, slot, durationHours, isLoggedIn, submitting, error, onConfirm, onBack }: {
    room: AvailableRoom;
    slot: Slot;
    durationHours: number;
    isLoggedIn: boolean;
    submitting: boolean;
    error: string;
    onConfirm: (paymentMethod: string, guestEmail: string, guestName: string) => void;
    onBack: () => void;
  } = $props();

  let paymentMethod = $state('UPFRONT');
  let guestName = $state('');
  let guestEmail = $state('');

  const timeFmt = new Intl.DateTimeFormat('en-GB', {
    timeZone: 'Europe/London',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  });

  const dateFmt = new Intl.DateTimeFormat('en-GB', {
    timeZone: 'Europe/London',
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });

  const startDate = $derived(new Date(slot.start_time));
  const endDate = $derived(new Date(startDate.getTime() + durationHours * 3_600_000));
  const totalPrice = $derived((durationHours * parseFloat(room.hourly_rate)).toFixed(2));

  const canSubmit = $derived(
    !submitting && (!isLoggedIn ? guestName.trim() !== '' && guestEmail.trim() !== '' : true)
  );
</script>

<div class="step">
  <h2>Confirm booking</h2>

  <div class="summary-card">
    <div class="summary-row main">
      <span class="room-name">{room.name}</span>
      <span class="price">£{totalPrice}</span>
    </div>
    <div class="summary-row">
      <span>{dateFmt.format(startDate)}</span>
    </div>
    <div class="summary-row">
      <span>{timeFmt.format(startDate)} – {timeFmt.format(endDate)}</span>
      <span class="muted">{durationHours}h</span>
    </div>
  </div>

  {#if !isLoggedIn}
    <div class="guest-section">
      <p class="guest-note">No account needed — we'll email your confirmation.</p>
      <div class="field">
        <label for="guest-name">Name</label>
        <input id="guest-name" type="text" bind:value={guestName} autocomplete="name" required />
      </div>
      <div class="field">
        <label for="guest-email">Email</label>
        <input id="guest-email" type="email" bind:value={guestEmail} autocomplete="email" required />
      </div>
    </div>
  {/if}

  <div class="payment-section">
    <p class="section-label">Payment</p>
    <label class="radio-label">
      <input type="radio" bind:group={paymentMethod} value="UPFRONT" />
      Pay upfront
    </label>
    {#if isLoggedIn}
      <label class="radio-label">
        <input type="radio" bind:group={paymentMethod} value="ON_DAY" />
        Pay on the day
      </label>
    {/if}
    <p class="payment-note">Your booking is confirmed immediately. Payment details will follow separately.</p>
  </div>

  {#if error}
    <p class="error-banner">{error}</p>
  {/if}

  <div class="actions">
    <button class="back" onclick={onBack} disabled={submitting}>← Back</button>
    <button
      class="submit"
      disabled={!canSubmit}
      onclick={() => onConfirm(paymentMethod, guestEmail, guestName)}
    >
      {submitting ? 'Confirming…' : 'Confirm booking'}
    </button>
  </div>
</div>

<style>
  .step { max-width: 480px; }

  h2 {
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
    letter-spacing: -0.01em;
  }

  .summary-card {
    border: 1px solid #e5e5e5;
    border-radius: 6px;
    padding: 1rem 1.25rem;
    margin-bottom: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
  }

  .summary-row {
    display: flex;
    justify-content: space-between;
    font-size: 0.9rem;
    color: #444;
  }

  .summary-row.main { margin-bottom: 0.25rem; }

  .room-name { font-weight: 600; font-size: 1rem; color: #1a1a1a; }
  .price { font-weight: 600; font-size: 1rem; color: #1a1a1a; }
  .muted { color: #888; }

  .guest-section { margin-bottom: 1.5rem; }

  .guest-note {
    font-size: 0.875rem;
    color: #555;
    margin-bottom: 1rem;
  }

  .field {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    margin-bottom: 1rem;
  }

  label { font-size: 0.875rem; font-weight: 500; }

  input[type="text"],
  input[type="email"] {
    padding: 0.6rem 0.75rem;
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    font-size: 1rem;
    font-family: inherit;
    outline: none;
    transition: border-color 0.15s;
  }

  input[type="text"]:focus,
  input[type="email"]:focus { border-color: #1a1a1a; }

  .payment-section { margin-bottom: 1.5rem; }

  .section-label {
    font-size: 0.875rem;
    font-weight: 500;
    margin-bottom: 0.75rem;
  }

  .radio-label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
    cursor: pointer;
    font-weight: normal;
  }

  .payment-note {
    font-size: 0.8rem;
    color: #888;
    margin-top: 0.75rem;
  }

  .error-banner {
    background: #fff0f0;
    border: 1px solid #fcc;
    color: #c00;
    padding: 0.75rem 1rem;
    border-radius: 4px;
    font-size: 0.9rem;
    margin-bottom: 1.25rem;
  }

  .actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .back {
    background: none;
    border: none;
    color: #555;
    font-size: 0.875rem;
    font-family: inherit;
    cursor: pointer;
    padding: 0;
  }

  .back:hover:not(:disabled) { color: #1a1a1a; }
  .back:disabled { opacity: 0.4; cursor: not-allowed; }

  .submit {
    padding: 0.7rem 1.75rem;
    background: #1a1a1a;
    color: #fff;
    border: none;
    border-radius: 4px;
    font-size: 1rem;
    font-family: inherit;
    cursor: pointer;
    transition: background 0.15s;
  }

  .submit:hover:not(:disabled) { background: #333; }
  .submit:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
