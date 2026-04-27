<script lang="ts">
  const API = import.meta.env.PUBLIC_API_URL ?? 'http://127.0.0.1:8000/api';

  let email = $state('');
  let password1 = $state('');
  let password2 = $state('');
  let loading = $state(false);
  let success = $state(false);
  let errors: Record<string, string[]> = $state({});

  function fieldError(key: string): string | undefined {
    return errors[key]?.[0];
  }

  async function submit(e: Event) {
    e.preventDefault();
    loading = true;
    errors = {};
    try {
      const res = await fetch(`${API}/auth/registration/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password1, password2 }),
      });
      const data = await res.json();
      if (!res.ok) {
        errors = data;
        return;
      }
      success = true;
    } catch {
      errors = { non_field_errors: ['Could not reach the server. Please try again.'] };
    } finally {
      loading = false;
    }
  }
</script>

<div class="auth-wrap">
  {#if success}
    <div class="success-panel">
      <h1>Check your email</h1>
      <p>
        We've sent a verification link to <strong>{email}</strong>.
        Click it to activate your account, then <a href="/login">log in</a>.
      </p>
    </div>
  {:else}
    <h1>Create account</h1>

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

      <div class="field" class:has-error={!!fieldError('password1')}>
        <label for="password1">Password</label>
        <input
          id="password1"
          type="password"
          bind:value={password1}
          autocomplete="new-password"
          required
        />
        {#if fieldError('password1')}<span class="field-error">{fieldError('password1')}</span>{/if}
      </div>

      <div class="field" class:has-error={!!fieldError('password2')}>
        <label for="password2">Confirm password</label>
        <input
          id="password2"
          type="password"
          bind:value={password2}
          autocomplete="new-password"
          required
        />
        {#if fieldError('password2')}<span class="field-error">{fieldError('password2')}</span>{/if}
      </div>

      <button type="submit" disabled={loading}>
        {loading ? 'Creating account…' : 'Create account'}
      </button>
    </form>

    <p class="switch">Already have an account? <a href="/login">Log in</a></p>
  {/if}
</div>

<style>
  .auth-wrap {
    max-width: 400px;
    margin: 0 auto;
  }

  h1 {
    font-family: var(--font-title);
    font-weight: 700;
    font-size: 2rem;
    text-transform: lowercase;
    letter-spacing: 0.02em;
    color: var(--text);
    margin-bottom: 2.5rem;
  }

  .success-panel {
    text-align: center;
    padding: 2rem;
    background: var(--ok-bg);
    border: 1px solid var(--ok-border);
  }

  .success-panel h1 { margin-bottom: 1rem; color: var(--ok-text); font-size: 1.5rem; }

  .success-panel p {
    color: var(--text-muted);
    line-height: 1.7;
    font-size: 0.9rem;
  }

  .success-panel a { color: var(--accent); }
  .success-panel a:hover { text-decoration: underline; }

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
    font-size: 1.2rem;
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
    font-size: 1.05rem;
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
    font-size: 0.93rem;
    letter-spacing: 0.06em;
    color: var(--text-muted);
  }

  .switch a { color: var(--accent); }
  .switch a:hover { text-decoration: underline; }
</style>
