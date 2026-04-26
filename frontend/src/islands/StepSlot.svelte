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
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 0.35rem;
    letter-spacing: -0.01em;
  }

  .sub {
    font-size: 0.875rem;
    color: #666;
    margin-bottom: 1.5rem;
  }

  .slot-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
  }

  .slot-btn {
    padding: 0.45rem 0.875rem;
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    background: #fff;
    font-size: 0.9rem;
    font-family: inherit;
    cursor: pointer;
    transition: border-color 0.1s, background 0.1s;
  }

  .slot-btn:hover { border-color: #1a1a1a; }
  .slot-btn.active { background: #1a1a1a; color: #fff; border-color: #1a1a1a; }

  .duration-row {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
    padding: 1rem 1.25rem;
    background: #f9f9f9;
    border-radius: 6px;
  }

  .dur-label { font-size: 0.875rem; font-weight: 500; white-space: nowrap; }

  .dur-options { display: flex; flex-wrap: wrap; gap: 0.4rem; }

  .dur-btn {
    padding: 0.35rem 0.75rem;
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    background: #fff;
    font-size: 0.875rem;
    font-family: inherit;
    cursor: pointer;
    transition: border-color 0.1s, background 0.1s;
  }

  .dur-btn:hover { border-color: #1a1a1a; }
  .dur-btn.active { background: #1a1a1a; color: #fff; border-color: #1a1a1a; }

  .summary {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.9rem;
    color: #333;
    padding: 0.6rem 1.25rem;
    background: #f0f0f0;
    border-radius: 4px;
    margin-bottom: 1.5rem;
  }

  .summary-price { font-weight: 600; }

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

  .back:hover { color: #1a1a1a; }

  .next {
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

  .next:hover:not(:disabled) { background: #333; }
  .next:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
