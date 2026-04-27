<script lang="ts">
  import { loadStripe, type Stripe, type StripeCardElement } from '@stripe/stripe-js';
  import type { AvailableRoom, Slot } from '../lib/api';

  type ConfirmPaymentFn = (clientSecret: string) => Promise<{ error?: { message?: string } }>;

  let { room, slot, durationHours, isLoggedIn, submitting, error, onConfirm, onBack }: {
    room: AvailableRoom;
    slot: Slot;
    durationHours: number;
    isLoggedIn: boolean;
    submitting: boolean;
    error: string;
    onConfirm: (paymentMethod: string, guestEmail: string, guestName: string, confirmPayment?: ConfirmPaymentFn) => void;
    onBack: () => void;
  } = $props();

  let paymentMethod = $state('UPFRONT');
  let guestName = $state('');
  let guestEmail = $state('');

  const STRIPE_KEY = import.meta.env.PUBLIC_STRIPE_KEY as string | undefined;
  let stripe = $state<Stripe | null>(null);
  let cardElement = $state<StripeCardElement | null>(null);
  let cardReady = $state(false);
  let cardError = $state('');
  let cardContainer = $state<HTMLDivElement | null>(null);

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

  const needsCard = $derived(paymentMethod === 'UPFRONT' && !!STRIPE_KEY);

  $effect(() => {
    if (!needsCard || !cardContainer) return;

    loadStripe(STRIPE_KEY!).then((s: Stripe | null) => {
      if (!s || !cardContainer) return;
      stripe = s;
      const elements = s.elements();
      const card = elements.create('card', {
        style: {
          base: {
            fontFamily: 'inherit',
            fontSize: '15px',
            color: '#d8e0e3',
            '::placeholder': { color: '#3a4a50' },
            backgroundColor: '#1f2426',
          },
          invalid: { color: '#d95555' },
        },
      });
      card.mount(cardContainer);
      card.on('ready', () => { cardReady = true; });
      card.on('change', e => { cardError = e.error?.message ?? ''; });
      cardElement = card;
    });

    return () => {
      cardElement?.destroy();
      cardElement = null;
      cardReady = false;
      stripe = null;
    };
  });

  function buildConfirmPayment(): ConfirmPaymentFn | undefined {
    if (!stripe || !cardElement) return undefined;
    const s = stripe;
    const c = cardElement;
    return (clientSecret: string) =>
      s.confirmCardPayment(clientSecret, { payment_method: { card: c } });
  }

  const canSubmit = $derived(
    !submitting
    && (!isLoggedIn ? guestName.trim() !== '' && guestEmail.trim() !== '' : true)
    && (!needsCard || cardReady)
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

    {#if needsCard}
      <div class="card-field">
        <p class="card-label">Card details</p>
        <div class="card-element" bind:this={cardContainer}></div>
        {#if cardError}<p class="card-error">{cardError}</p>{/if}
      </div>
    {:else if paymentMethod === 'ON_DAY'}
      <p class="payment-note">You'll pay when you arrive at the studio.</p>
    {:else}
      <p class="payment-note">Your booking is confirmed immediately. Payment details will follow separately.</p>
    {/if}
  </div>

  {#if error}
    <p class="error-banner">{error}</p>
  {/if}

  <div class="actions">
    <button class="back" onclick={onBack} disabled={submitting}>← Back</button>
    <button
      class="submit"
      disabled={!canSubmit}
      onclick={() => onConfirm(paymentMethod, guestEmail, guestName, buildConfirmPayment())}
    >
      {submitting ? 'Confirming…' : 'Confirm booking'}
    </button>
  </div>
</div>

<style>
  .step { max-width: 480px; }

  h2 {
    font-family: var(--font-title);
    font-weight: 700;
    font-size: 1.8rem;
    text-transform: lowercase;
    letter-spacing: 0.02em;
    color: var(--text);
    margin-bottom: 1.75rem;
  }

  .summary-card {
    border: 1px solid var(--border);
    background: var(--surface);
    padding: 1rem 1.25rem;
    margin-bottom: 1.75rem;
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
  }

  .summary-row {
    display: flex;
    justify-content: space-between;
    font-size: 1.05rem;
    color: var(--text-muted);
  }

  .summary-row.main { margin-bottom: 0.25rem; }

  .room-name {
    font-weight: 600;
    font-size: 1.2rem;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--text);
  }
  .price { font-weight: 700; font-size: 1.05rem; color: var(--accent); }
  .muted { color: var(--text-faint); }

  .guest-section { margin-bottom: 1.75rem; }

  .guest-note {
    font-size: 0.97rem;
    letter-spacing: 0.04em;
    color: var(--text-faint);
    margin-bottom: 1rem;
  }

  .field {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    margin-bottom: 1rem;
  }

  label {
    font-size: 1.2rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--silver);
  }

  input[type="text"],
  input[type="email"] {
    padding: 0.65rem 0.75rem;
    border: 1px solid var(--border);
    background: var(--surface-2);
    color: var(--text);
    font-size: 1.05rem;
    font-family: inherit;
    outline: none;
    transition: border-color 0.15s;
  }

  input[type="text"]:focus,
  input[type="email"]:focus { border-color: var(--accent); }

  .payment-section { margin-bottom: 1.75rem; }

  .section-label {
    font-size: 1.2rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--silver);
    margin-bottom: 0.875rem;
  }

  .radio-label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.97rem;
    color: var(--text-muted);
    margin-bottom: 0.5rem;
    cursor: pointer;
    font-weight: normal;
    letter-spacing: 0.03em;
  }

  .card-field {
    margin-top: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
  }

  .card-label {
    font-size: 1.2rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--silver);
  }

  .card-element {
    padding: 0.65rem 0.75rem;
    border: 1px solid var(--border);
    background: var(--surface-2);
    transition: border-color 0.15s;
  }

  .card-element:focus-within { border-color: var(--accent); }

  .card-error { font-size: 0.8rem; color: var(--err-text); }

  .payment-note {
    font-size: 0.97rem;
    color: var(--text-faint);
    margin-top: 0.75rem;
    letter-spacing: 0.03em;
  }

  .error-banner {
    background: var(--err-bg);
    border: 1px solid var(--err-border);
    color: var(--err-text);
    padding: 0.75rem 1rem;
    font-size: 0.97rem;
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
    color: var(--text-muted);
    font-size: 0.97rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    font-family: inherit;
    cursor: pointer;
    padding: 0;
    transition: color 0.15s;
  }

  .back:hover:not(:disabled) { color: var(--text); }
  .back:disabled { opacity: 0.4; cursor: not-allowed; }

  .submit {
    padding: 0.7rem 1.75rem;
    background: var(--accent);
    color: var(--accent-fg);
    border: 1px solid var(--accent);
    font-size: 0.97rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    font-family: inherit;
    cursor: pointer;
    transition: background 0.15s;
  }

  .submit:hover:not(:disabled) { background: var(--accent-hover); border-color: var(--accent-hover); }
  .submit:disabled { opacity: 0.4; cursor: not-allowed; }
</style>
