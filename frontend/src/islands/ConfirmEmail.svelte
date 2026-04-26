<script lang="ts">
  const API = import.meta.env.PUBLIC_API_URL ?? 'http://127.0.0.1:8000/api';

  let key = $state('');
  let status: 'idle' | 'loading' | 'success' | 'error' = $state('idle');
  let errorMessage = $state('');

  $effect(() => {
    key = new URLSearchParams(window.location.search).get('key') ?? '';
    if (!key) {
      status = 'error';
      errorMessage = 'Invalid confirmation link — the key is missing.';
    }
  });

  async function confirm() {
    status = 'loading';
    try {
      const res = await fetch(`${API}/auth/registration/verify-email/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        errorMessage = data.detail ?? 'This link has expired or has already been used.';
        status = 'error';
        return;
      }
      status = 'success';
    } catch {
      errorMessage = 'Could not reach the server. Please try again.';
      status = 'error';
    }
  }
</script>

<div class="confirm-wrap">
  {#if status === 'success'}
    <div class="panel success">
      <h1>Email confirmed</h1>
      <p>Your account is now active. <a href="/login">Log in</a> to continue.</p>
    </div>

  {:else if status === 'error'}
    <div class="panel error">
      <h1>Something went wrong</h1>
      <p>{errorMessage}</p>
      <p><a href="/register">Register again</a> to get a new link.</p>
    </div>

  {:else}
    <div class="panel">
      <h1>Confirm your email</h1>
      <p>Click the button below to verify your email address and activate your account.</p>
      <button onclick={confirm} disabled={status === 'loading'}>
        {status === 'loading' ? 'Confirming…' : 'Confirm email'}
      </button>
    </div>
  {/if}
</div>

<style>
  .confirm-wrap {
    max-width: 480px;
    margin: 4rem auto;
  }

  .panel {
    border: 1px solid #e5e5e5;
    border-radius: 8px;
    padding: 2.5rem;
    text-align: center;
  }

  .panel.success {
    background: #f0faf0;
    border-color: #b0ddb0;
  }

  .panel.error {
    background: #fff0f0;
    border-color: #fcc;
  }

  h1 {
    font-size: 1.5rem;
    letter-spacing: -0.03em;
    margin-bottom: 1rem;
  }

  p {
    color: #444;
    line-height: 1.6;
    margin-bottom: 1rem;
  }

  p:last-child { margin-bottom: 0; }

  a { text-decoration: underline; }

  button {
    margin-top: 1.5rem;
    padding: 0.7rem 2rem;
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
  button:disabled { opacity: 0.6; cursor: not-allowed; }
</style>
