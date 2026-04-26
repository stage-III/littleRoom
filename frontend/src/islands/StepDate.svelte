<script lang="ts">
  import { api, type AvailabilityResponse } from '../lib/api';

  let { initialDate, minDate, onConfirm }: {
    initialDate: string;
    minDate: string;
    onConfirm: (date: string, avail: AvailabilityResponse) => void;
  } = $props();

  let date = $state(initialDate || minDate);
  let loading = $state(false);
  let message = $state('');

  async function check() {
    if (!date) return;
    loading = true;
    message = '';
    try {
      const avail = await api.get<AvailabilityResponse>(`/availability/?date=${date}`);
      if (!avail.is_open) {
        message = 'The studio is closed on this date — please choose another.';
        return;
      }
      const hasSlots = avail.rooms.some(r => r.slots.length > 0);
      if (!hasSlots) {
        message = 'No availability on this date — all rooms are fully booked.';
        return;
      }
      onConfirm(date, avail);
    } catch {
      message = 'Could not load availability. Please try again.';
    } finally {
      loading = false;
    }
  }
</script>

<div class="step">
  <h2>Pick a date</h2>
  <div class="field">
    <label for="date">Date</label>
    <input
      id="date"
      type="date"
      bind:value={date}
      min={minDate}
      onchange={() => { message = ''; }}
    />
  </div>
  {#if message}
    <p class="notice">{message}</p>
  {/if}
  <button onclick={check} disabled={!date || loading}>
    {loading ? 'Checking…' : 'Check availability'}
  </button>
</div>

<style>
  .step { max-width: 400px; }

  h2 {
    font-family: var(--font-title);
    font-weight: 700;
    font-size: 1.5rem;
    text-transform: lowercase;
    letter-spacing: 0.02em;
    color: var(--text);
    margin-bottom: 1.75rem;
  }

  .field {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    margin-bottom: 1.25rem;
  }

  label {
    font-size: 0.9rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--silver);
  }

  input[type="date"] {
    padding: 0.65rem 0.75rem;
    border: 1px solid var(--border);
    background: var(--surface-2);
    color: var(--text);
    font-size: 0.95rem;
    font-family: inherit;
    outline: none;
    transition: border-color 0.15s;
    color-scheme: dark;
  }

  input[type="date"]:focus { border-color: var(--accent); }

  .notice {
    font-size: 0.875rem;
    color: var(--warn-text);
    background: var(--warn-bg);
    border: 1px solid var(--warn-border);
    padding: 0.65rem 0.875rem;
    margin-bottom: 1.25rem;
  }

  button {
    padding: 0.7rem 1.75rem;
    background: var(--accent);
    color: var(--accent-fg);
    border: 1px solid var(--accent);
    font-size: 0.78rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    font-family: inherit;
    cursor: pointer;
    transition: background 0.15s;
  }

  button:hover:not(:disabled) { background: var(--accent-hover); border-color: var(--accent-hover); }
  button:disabled { opacity: 0.4; cursor: not-allowed; }
</style>
