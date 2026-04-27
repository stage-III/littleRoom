<script lang="ts">
  import type { AvailabilityResponse, AvailableRoom } from '../lib/api';

  let { availability, onConfirm, onBack }: {
    availability: AvailabilityResponse;
    onConfirm: (room: AvailableRoom) => void;
    onBack: () => void;
  } = $props();

  const rooms = $derived(availability.rooms.filter(r => r.slots.length > 0));
</script>

<div class="step">
  <h2>Choose a room</h2>
  <p class="sub">{availability.date} · {availability.open_time} – {availability.close_time}</p>

  {#if rooms.length === 0}
    <p class="notice">No rooms available on this date.</p>
  {:else}
    <ul class="room-list">
      {#each rooms as room}
        <li>
          <button class="room-card" onclick={() => onConfirm(room)}>
            <div class="room-name">{room.name}</div>
            <div class="room-meta">
              <span>£{room.hourly_rate}/hr</span>
              <span class="sep">·</span>
              <span>{room.slots.length} slot{room.slots.length === 1 ? '' : 's'} available</span>
            </div>
          </button>
        </li>
      {/each}
    </ul>
  {/if}

  <button class="back" onclick={onBack}>← Back</button>
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
    color: var(--text-faint);
    margin-bottom: 1.75rem;
  }

  .notice {
    font-size: 0.97rem;
    color: var(--text-muted);
    margin-bottom: 1.5rem;
  }

  .room-list {
    list-style: none;
    padding: 0;
    margin: 0 0 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
  }

  .room-card {
    width: 100%;
    text-align: left;
    padding: 1rem 1.25rem;
    border: 1px solid var(--border);
    background: var(--surface);
    cursor: pointer;
    font-family: inherit;
    transition: border-color 0.15s, background 0.15s;
  }

  .room-card:hover {
    border-color: var(--accent);
    background: var(--surface-2);
  }

  .room-name {
    font-family: var(--font-title);
    font-weight: 700;
    font-size: 1.2rem;
    text-transform: lowercase;
    letter-spacing: 0.02em;
    color: var(--text);
    margin-bottom: 0.35rem;
  }

  .room-meta {
    font-family: var(--font-ui);
    font-weight: 300;
    font-size: 1.2rem;
    color: var(--text-muted);
    display: flex;
    gap: 0.4rem;
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }

  .sep { color: var(--text-faint); }

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
</style>
