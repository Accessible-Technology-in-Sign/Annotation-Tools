<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';

  const API_BASE = 'http://127.0.0.1:5000';
  const username = (localStorage.getItem('username') || '').trim();

  let items = [];
  let loading = true;
  let error = null;

  $: params = $page.params;

  function basename(p) { return (p || '').split('/').pop(); }

  onMount(async () => {
    try {
      const url = new URL(`${API_BASE}/annots`);
      url.searchParams.set('user', username);
      url.searchParams.set('sign', params.word);

      const r = await fetch(url);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const saved = await r.json(); 

      items = Object.entries(saved)
        .map(([full, v]) => ({ full, video: basename(full), label: v.label, time: v.time }))
        .sort((a, b) => a.video.localeCompare(b.video));
    } catch (e) {
      error = String(e);
    } finally {
      loading = false;
    }
  });
  
  function reReview(item) {
    // item.full is the server path we got from /annots
    const q = new URLSearchParams({ video: item.full });
    goto(`/annotation/${params.batch}/${params.word}?${q.toString()}`);
  }

  function labelMeta(l) {
    const base = "inline-flex items-center gap-2 px-2.5 py-1 rounded-md text-sm font-medium shrink-0";
    if (l === "Good")           return { cls: `${base} bg-green-200`,  icon: "/thumbs-up.svg" };
    if (l === "Variant")        return { cls: `${base} bg-yellow-200`, icon: "/variant.svg" };
    if (l === "Bad")            return { cls: `${base} bg-red-200`,    icon: "/thumbs-down.svg" };
    if (l === "Further Review") return { cls: `${base} bg-blue-200`,   icon: "/archive.svg" };
    return { cls: `${base} bg-gray-200`, icon: "" };
  }
</script>

{#if loading}
  <div class="p-6 text-gray-500">Loading…</div>
{:else if error}
    <div class="p-6 text-red-600">Error: {error}</div>
{:else}
  <div class="p-6 max-w-3xl mx-auto">
    <h1 class="text-xl font-semibold">Summary — {params.word} <span class="text-gray-500">({params.batch})</span></h1>
    {#if items.length === 0}
      <div class="mt-4 text-gray-500">No annotations yet for this word.</div>
    {:else}
      <div class="mt-4 border rounded overflow-hidden">
        {#each items as it (it.full)}
        {@const meta = labelMeta(it.label)} 

        <div class="flex items-center gap-3 px-3 py-2 border-b last:border-b-0">
            <div class="min-w-0 flex-1">
            <span class="font-mono truncate block" title={it.full}>{it.video}</span>
            </div>

            <span class={meta.cls}>
            {#if meta.icon}<img src={meta.icon} class="w-4 h-4" alt="" />{/if}
            {it.label}
            </span>

            <button class="shrink-0 px-3 py-1 rounded bg-blue-600 text-white hover:bg-blue-700"
                    on:click={() => reReview(it)}>
            Re-review
            </button>
        </div>
        {/each}

      </div>
    {/if}
  </div>
{/if}
