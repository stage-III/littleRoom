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
    font-size: 1.8rem;
    letter-spacing: -0.03em;
    margin-bottom: 2rem;
  }

  .success-panel {
    text-align: center;
    padding: 2rem;
    background: #f0faf0;
    border: 1px solid #b0ddb0;
    border-radius: 8px;
  }

  .success-panel h1 { margin-bottom: 1rem; }

  .success-panel p {
    color: #444;
    line-height: 1.6;
  }

  .success-panel a { text-decoration: underline; }

  .error-banner {
    background: #fff0f0;
    border: 1px solid #fcc;
    color: #c00;
    padding: 0.75rem 1rem;
    border-radius: 4px;
    font-size: 0.9rem;
    margin-bottom: 1.5rem;
  }

  .field {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    margin-bottom: 1.25rem;
  }

  label {
    font-size: 0.875rem;
    font-weight: 500;
  }

  input {
    padding: 0.6rem 0.75rem;
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    font-size: 1rem;
    font-family: inherit;
    transition: border-color 0.15s;
    outline: none;
  }

  input:focus { border-color: #1a1a1a; }

  .has-error input { border-color: #c00; }

  .field-error {
    font-size: 0.8rem;
    color: #c00;
  }

  button {
    width: 100%;
    padding: 0.7rem;
    background: #1a1a1a;
    color: #fff;
    border: none;
    border-radius: 4px;
    font-size: 1rem;
    font-family: inherit;
    cursor: pointer;
    transition: background 0.15s;
    margin-top: 0.5rem;
  }

  button:hover:not(:disabled) { background: #333; }
  button:disabled { opacity: 0.6; cursor: not-allowed; }

  .switch {
    text-align: center;
    margin-top: 1.5rem;
    font-size: 0.9rem;
    color: #555;
  }

  .switch a { text-decoration: underline; }
</style>
