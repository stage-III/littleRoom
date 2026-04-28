<script lang="ts">
  import { api, type Room } from '../lib/api';

  let rooms: Room[] = $state([]);
  let loading = $state(true);
  let error = $state(false);

  $effect(() => {
    api.get<Room[]>('/rooms/')
      .then(data => { rooms = data; loading = false; })
      .catch(() => { error = true; loading = false; });
  });
</script>

{#if loading}
  <p class="status">Loading rooms…</p>
{:else if error}
  <p class="status">Could not load rooms. Please try again.</p>
{:else if rooms.length === 0}
  <p class="status">No rooms listed yet — check back soon.</p>
{:else}
  <div class="room-grid">
    {#each rooms as room}
      <article class="room-card">
        <div class="room-image">
          <span class="placeholder">📷</span>
        </div>
        <div class="room-body">
          <h3>{room.name}</h3>
          {#if room.size_sqm}<p class="meta">{room.size_sqm} m²</p>{/if}
          {#if room.description}<p class="description">{room.description}</p>{/if}
          {#if room.equipment.length > 0}
            <ul class="equipment">
              {#each room.equipment as e}
                <li>{e.name}</li>
              {/each}
            </ul>
          {/if}
          <div class="footer">
            <span class="rate">£{room.hourly_rate} / hr</span>
            <a href="/book" class="btn-book">Book</a>
          </div>
        </div>
      </article>
    {/each}
  </div>
{/if}

<style>
  .status {
    color: var(--text-faint);
    font-size: 0.875rem;
  }

  .room-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
  }

  .room-card {
    border: 1px solid var(--border);
    overflow: hidden;
    display: flex;
    flex-direction: column;
    background: var(--surface);
    transition: border-color 0.15s;
  }

  .room-card:hover { border-color: var(--accent); }

  .room-image {
    background: var(--surface-2);
    height: 180px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    color: var(--text-faint);
    border-bottom: 1px solid var(--border);
  }

  .room-body {
    padding: 1.25rem;
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
    flex: 1;
  }

  h3 {
    font-family: var(--font-title);
    font-weight: 700;
    font-size: 1.05rem;
    text-transform: lowercase;
    letter-spacing: 0.02em;
    color: var(--text);
  }

  .meta {
    font-family: var(--font-ui);
    font-weight: 300;
    font-size: 1.2rem;
    color: var(--text-muted);
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }

  .description {
    font-family: 'Barlow', sans-serif;
    font-weight: 400;
    font-size: 1.05rem;
    color: var(--text-muted);
    line-height: 1.6;
  }

  .equipment {
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .equipment li {
    font-family: 'Barlow', sans-serif;
    font-weight: 400;
    font-size: 0.95rem;
    color: var(--silver);
    padding-left: 0.75rem;
    position: relative;
  }

  .equipment li::before {
    content: '—';
    position: absolute;
    left: 0;
    color: var(--text-faint);
  }

  .footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: auto;
    padding-top: 0.75rem;
    border-top: 1px solid var(--border);
  }

  .rate {
    font-weight: 700;
    font-size: 1.1rem;
    color: var(--accent);
    letter-spacing: 0.04em;
  }

  .btn-book {
    background: var(--accent);
    color: var(--accent-fg);
    padding: 0.4rem 1.1rem;
    font-family: 'Barlow', sans-serif;
    font-size: 0.97rem;
    font-weight: 400;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    border: 1px solid var(--accent);
    transition: background 0.15s;
    text-decoration: none;
  }

  .btn-book:hover { background: var(--accent-hover); border-color: var(--accent-hover); }
</style>
