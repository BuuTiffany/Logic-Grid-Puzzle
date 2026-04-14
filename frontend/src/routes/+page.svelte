<p>{"Home"}</p>

<script>
  import { PUBLIC_API_BASE } from '$env/static/public';
  import { onMount } from 'svelte';

  let message = '';

  onMount(async () => {
    const res = await fetch(`${PUBLIC_API_BASE}/api/hello/`);
    const data = await res.json();
    message = data.message;
  });
</script>

<p>{message}</p>