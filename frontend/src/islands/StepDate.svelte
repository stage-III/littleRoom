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
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
    letter-spacing: -0.01em;
  }

  .field {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    margin-bottom: 1.25rem;
  }

  label { font-size: 0.875rem; font-weight: 500; }

  input[type="date"] {
    padding: 0.6rem 0.75rem;
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    font-size: 1rem;
    font-family: inherit;
    outline: none;
    transition: border-color 0.15s;
  }

  input[type="date"]:focus { border-color: #1a1a1a; }

  .notice {
    font-size: 0.9rem;
    color: #b06000;
    background: #fffbf0;
    border: 1px solid #f0d080;
    border-radius: 4px;
    padding: 0.6rem 0.875rem;
    margin-bottom: 1.25rem;
  }

  button {
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

  button:hover:not(:disabled) { background: #333; }
  button:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
