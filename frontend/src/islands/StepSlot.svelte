<script lang="ts">
  import type { AvailableRoom, Slot } from '../lib/api';

  let { room, minBookingHours, onConfirm, onBack }: {
    room: AvailableRoom;
    minBookingHours: number;
    onConfirm: (slot: Slot, hours: number) => void;
    onBack: () => void;
  } = $props();

  let selectedSlot: Slot | null = $state(null);
  let selectedHours: number = $state(0);

  const timeFmt = new Intl.DateTimeFormat('en-GB', {
    timeZone: 'Europe/London',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  });

  function fmt(iso: string) {
    return timeFmt.format(new Date(iso));
  }

  function endTime(slot: Slot, hours: number) {
    return fmt(new Date(new Date(slot.start_time).getTime() + hours * 3_600_000).toISOString());
  }

  function price(hours: number) {
    return (hours * parseFloat(room.hourly_rate)).toFixed(2);
  }

  function durationOptions(slot: Slot): number[] {
    const options: number[] = [];
    for (let h = minBookingHours; h <= slot.max_hours; h++) options.push(h);
    return options;
  }

  function selectSlot(slot: Slot) {
    selectedSlot = slot;
    selectedHours = minBookingHours;
  }

  const canProceed = $derived(selectedSlot !== null && selectedHours > 0);
</script>

<div class="step">
  <h2>Choose a time</h2>
  <p class="sub">{room.name}</p>

  <div class="slot-grid">
    {#each room.slots as slot}
      <button
        class="slot-btn"
        class:active={selectedSlot?.start_time === slot.start_time}
        onclick={() => selectSlot(slot)}
      >
        {fmt(slot.start_time)}
      </button>
    {/each}
  </div>

  {#if selectedSlot}
    <div class="duration-row">
      <span class="dur-label">Duration</span>
      <div class="dur-options">
        {#each durationOptions(selectedSlot) as h}
          <button
            class="dur-btn"
            class:active={selectedHours === h}
            onclick={() => { selectedHours = h; }}
          >
            {h}h
          </button>
        {/each}
      </div>
    </div>

    {#if selectedHours > 0}
      <div class="summary">
        <span>{fmt(selectedSlot.start_time)} – {endTime(selectedSlot, selectedHours)}</span>
        <span class="summary-price">£{price(selectedHours)}</span>
      </div>
    {/if}
  {/if}

  <div class="actions">
    <button class="back" onclick={onBack}>← Back</button>
    <button
      class="next"
      disabled={!canProceed}
      onclick={() => onConfirm(selectedSlot!, selectedHours)}
    >
      Next →
    </button>
  </div>
</div>

<style>
  .step { max-width: 520px; }

  h2 {
    font-family: var(--font-title);
    font-weight: 700;
    font-size: 1.8rem;
    text-transform: lowercase;
    letter-spacing: 0.02em;
    color: var(--text);
    margin-bottom: 0.35rem;
  }

  .sub {
    font-family: var(--font-ui);
    font-weight: 300;
    font-size: 1.4rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 1.75rem;
  }

  .slot-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    margin-bottom: 1.5rem;
  }

  .slot-btn {
    padding: 0.45rem 0.875rem;
    border: 1px solid var(--border);
    background: var(--surface);
    color: var(--text-muted);
    font-size: 0.97rem;
    font-family: inherit;
    cursor: pointer;
    transition: border-color 0.1s, background 0.1s, color 0.1s;
    letter-spacing: 0.04em;
  }

  .slot-btn:hover { border-color: var(--accent); color: var(--text); }
  .slot-btn.active { background: var(--accent); color: var(--accent-fg); border-color: var(--accent); }

  .duration-row {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
    padding: 1rem 1.25rem;
    background: var(--surface);
    border: 1px solid var(--border);
  }

  .dur-label {
    font-size: 1.2rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--silver);
    white-space: nowrap;
  }

  .dur-options { display: flex; flex-wrap: wrap; gap: 0.4rem; }

  .dur-btn {
    padding: 0.35rem 0.75rem;
    border: 1px solid var(--border);
    background: var(--surface-2);
    color: var(--text-muted);
    font-size: 0.97rem;
    font-family: inherit;
    cursor: pointer;
    transition: border-color 0.1s, background 0.1s, color 0.1s;
    letter-spacing: 0.04em;
  }

  .dur-btn:hover { border-color: var(--accent); color: var(--text); }
  .dur-btn.active { background: var(--accent); color: var(--accent-fg); border-color: var(--accent); }

  .summary {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 1.05rem;
    color: var(--text);
    padding: 0.65rem 1.25rem;
    background: var(--accent-dim);
    border: 1px solid var(--accent);
    margin-bottom: 1.5rem;
  }

  .summary-price { font-weight: 700; color: var(--accent); letter-spacing: 0.04em; }

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
    font-weight: 400;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    font-family: inherit;
    cursor: pointer;
    padding: 0;
    transition: color 0.15s;
  }

  .back:hover { color: var(--text); }

  .next {
    padding: 0.7rem 1.75rem;
    background: var(--accent);
    color: var(--accent-fg);
    border: 1px solid var(--accent);
    font-size: 0.97rem;
    font-weight: 400;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    font-family: inherit;
    cursor: pointer;
    transition: background 0.15s;
  }

  .next:hover:not(:disabled) { background: var(--accent-hover); border-color: var(--accent-hover); }
  .next:disabled { opacity: 0.4; cursor: not-allowed; }
</style>
