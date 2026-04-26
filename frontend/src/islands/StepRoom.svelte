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

  .notice {
    font-size: 0.9rem;
    color: #888;
    margin-bottom: 1.5rem;
  }

  .room-list {
    list-style: none;
    padding: 0;
    margin: 0 0 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .room-card {
    width: 100%;
    text-align: left;
    padding: 1rem 1.25rem;
    border: 1px solid #e5e5e5;
    border-radius: 6px;
    background: #fff;
    cursor: pointer;
    font-family: inherit;
    transition: border-color 0.15s, box-shadow 0.15s;
  }

  .room-card:hover {
    border-color: #1a1a1a;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  }

  .room-name {
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 0.3rem;
  }

  .room-meta {
    font-size: 0.875rem;
    color: #555;
    display: flex;
    gap: 0.4rem;
  }

  .sep { color: #bbb; }

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
</style>
