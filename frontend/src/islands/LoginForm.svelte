<script lang="ts">
  const API = import.meta.env.PUBLIC_API_URL ?? 'http://127.0.0.1:8000/api';

  let email = $state('');
  let password = $state('');
  let loading = $state(false);
  let errors: Record<string, string[]> = $state({});

  function fieldError(key: string): string | undefined {
    return errors[key]?.[0];
  }

  async function submit(e: Event) {
    e.preventDefault();
    loading = true;
    errors = {};
    try {
      const res = await fetch(`${API}/auth/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json();
      if (!res.ok) {
        errors = data;
        return;
      }
      localStorage.setItem('token', data.key);
      window.location.href = '/account';
    } catch {
      errors = { non_field_errors: ['Could not reach the server. Please try again.'] };
    } finally {
      loading = false;
    }
  }
</script>

<div class="auth-wrap">
  <h1>Log in</h1>

  {#if errors.non_field_errors}
    <p class="error-banner">{errors.non_field_errors[0]}</p>
  {/if}

  <form onsubmit={submit} novalidate>
    <div class="field" class:has-error={!!fieldError('email')}>
      <label for="email">Email</label>
      <input
        id="email"
        type="email"
        bind:value={email}
        autocomplete="email"
        required
      />
      {#if fieldError('email')}<span class="field-error">{fieldError('email')}</span>{/if}
    </div>

    <div class="field" class:has-error={!!fieldError('password')}>
      <label for="password">Password</label>
      <input
        id="password"
        type="password"
        bind:value={password}
        autocomplete="current-password"
        required
      />
      {#if fieldError('password')}<span class="field-error">{fieldError('password')}</span>{/if}
    </div>

    <button type="submit" disabled={loading}>
      {loading ? 'Logging in…' : 'Log in'}
    </button>
  </form>

  <p class="switch">Don't have an account? <a href="/register">Register</a></p>
</div>

<style>
  .auth-wrap {
    max-width: 400px;
    margin: 0 auto;
  }

  h1 {
    font-family: var(--font-title);
    font-weight: 700;
    font-size: 1.8rem;
    text-transform: lowercase;
    letter-spacing: 0.02em;
    color: var(--text);
    margin-bottom: 2.5rem;
  }

  .error-banner {
    background: var(--err-bg);
    border: 1px solid var(--err-border);
    color: var(--err-text);
    padding: 0.75rem 1rem;
    font-size: 0.875rem;
    margin-bottom: 1.5rem;
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

  input {
    padding: 0.65rem 0.75rem;
    border: 1px solid var(--border);
    background: var(--surface-2);
    color: var(--text);
    font-size: 0.95rem;
    font-family: inherit;
    transition: border-color 0.15s;
    outline: none;
  }

  input:focus { border-color: var(--accent); }

  .has-error input { border-color: var(--err-border); }

  .field-error {
    font-size: 0.78rem;
    color: var(--err-text);
  }

  button {
    width: 100%;
    padding: 0.75rem;
    background: var(--accent);
    color: var(--accent-fg);
    border: 1px solid var(--accent);
    font-size: 0.78rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    font-family: inherit;
    cursor: pointer;
    transition: background 0.15s;
    margin-top: 0.5rem;
  }

  button:hover:not(:disabled) { background: var(--accent-hover); border-color: var(--accent-hover); }
  button:disabled { opacity: 0.5; cursor: not-allowed; }

  .switch {
    text-align: center;
    margin-top: 1.75rem;
    font-size: 0.78rem;
    letter-spacing: 0.06em;
    color: var(--text-muted);
  }

  .switch a { color: var(--accent); }
  .switch a:hover { text-decoration: underline; }
</style>
